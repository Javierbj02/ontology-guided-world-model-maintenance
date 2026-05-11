from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Any
from owlready2 import Thing

Triple = Tuple[str, str, str]


@dataclass
class Explanation:
    retract: Triple
    event_iri: str
    event_name: str
    reason: str


class causal_validator:

    def __init__(self,
                runtime: Any,
                event_class_qnames: Optional[List[str]] = None,
                participant_prop_names: Optional[List[str]] = None,
                location_prop_names: Optional[List[str]] = None,
                change_event_class_qname: Optional[str] = None,
                strict_object_loss_mode: bool = False):

        self.rt = runtime

        self.event_class_qnames = event_class_qnames or ["SOMA.Event", "DUL.Event", "DUL.Action"]
        self.event_type_prop_names = ["classifies", "isOccurrenceOf", "executesTask"]
        self._event_root_classes = None

        self.change_event_class_qname = change_event_class_qname or "SOMA.ChangeDisappearanceEvent"

        self.participant_prop_names = participant_prop_names or ["hasParticipant"]
        self.location_prop_names = location_prop_names or ["hasLocation", "occursIn"]
        self.causal_prop_names = ["causes"]

        self.strict_object_loss_mode = strict_object_loss_mode
        self.allowed_object_loss_event_types = {"Task_TakeMedicine"}
        self.required_object_loss_participants = {"Agent_Nurse"}

        self.event_birth_step: Dict[Thing, int] = {}
        self.event_tags: Dict[Thing, List[str]] = {}


    def _get_event_roots(self):
        if self._event_root_classes is None:
            roots = []
            for qn in self.event_class_qnames:
                cls = self.rt._get_class(qn)
                if cls is not None:
                    roots.append(cls)
            self._event_root_classes = roots
        return self._event_root_classes

    def _is_event_class(self, cls):
        roots = self._get_event_roots()
        if not roots:
            return False


        for root in roots:
            if root in cls.ancestors():
                return True
        return False
    
    def _is_instance_of(self, inst: Thing, class_local: str) -> bool:
        cls = getattr(self.rt.ns, class_local, None)
        if cls is None:
            return False
        try:
            return cls in inst.is_a or cls in inst.INDIRECT_is_a
        except Exception:
            return False

    def _requires_object_anchor(self, subj: Thing) -> bool:
        return self._is_instance_of(subj, "PhysicalObject")
    


    def _is_action_instance(self, ev: Thing) -> bool:
        return self._is_instance_of(ev, "Action")


    def _strong_object_loss_ok(self, ev: Thing, subj: Thing, old_loc: Thing, step_index: int) -> bool:
        if not self._when_ok(ev, step_index):
            return False

        if not self._where_ok(ev, old_loc):
            return False

        if not self._is_action_instance(ev):
            return False

        event_type_names = set(self._get_event_types(ev))
        if not (event_type_names & self.allowed_object_loss_event_types):
            return False

        participants = self._get_participants(ev)
        if subj not in participants:
            return False

        participant_names = {p.name for p in participants}
        if not self.required_object_loss_participants.issubset(participant_names):
            return False

        return True
    
    
    def _assert_causal_link(self, cause_ev: Thing, observed_ev: Thing) -> bool:
        for pname in self.causal_prop_names:
            prop = getattr(self.rt.ns, pname, None)
            if prop is None:
                continue
            try:
                col = getattr(cause_ev, prop.name)
            except Exception:
                continue
            if observed_ev not in col:
                col.append(observed_ev)
                return True
        return False

    def _create_change_event_for_retract(self, retract: Triple, step_index: int) -> Thing:
        s, p, o = retract
        subj = self.rt._get_entity(s)
        old_loc = self.rt._get_entity(o)

        change_cls = self.rt._get_class(self.change_event_class_qname)
        if change_cls is None:
            change_cls = self.rt._get_class("SOMA.Event") or Thing

        with self.rt.onto:
            ev_name = f"Ep_{step_index}_{s}_{p.split('.')[-1]}_{o}"
            ev_name = ev_name.replace(".", "_")
            ep = change_cls(ev_name)

            if subj is not None:
                for pname in self.participant_prop_names:
                    prop = getattr(self.rt.ns, pname, None)
                    if prop is not None:
                        getattr(ep, prop.name).append(subj)
                        break

            if old_loc is not None:
                for pname in self.location_prop_names:
                    prop = getattr(self.rt.ns, pname, None)
                    if prop is not None:
                        getattr(ep, prop.name).append(old_loc)
                        break


        return ep

    def register_new_types(self, step: Any, step_index: int):
        for inst_name, class_qn in step.types:
            cls = self.rt._get_class(class_qn)
            if cls is None:
                continue
            if not self._is_event_class(cls):
                continue

            inst = self.rt._get_entity(inst_name)
            if inst is None:
                continue
            if inst not in self.event_birth_step:
                self.event_birth_step[inst] = step_index
                self.event_tags[inst] = list(getattr(step, "tags", []) or [])

    def has_hl_changes(self, step: Any) -> bool:
        return bool(step.retracts)

    def validate_step(self, step: Any, step_index: int):
        errors: List[str] = []
        explanations: List[Explanation] = []

        for r in step.retracts:
            s, p, o = r

            prop_local = p.split(".")[-1]
            if prop_local != "hasLocation":
                continue

            explained, exp = self._explain_retract_hasLocation(r, step_index)
            if explained and exp is not None:
                explanations.append(exp)
            else:
                errors.append(
                    f"Retract {r} in step '{step.name}' has no known causal explanation."
                )

        return errors, explanations
    
    
    def unregister_deleted(self, names: List[str]):
        locals_to_remove = {n.split(".")[-1] for n in names}
        to_remove = [e for e in self.event_birth_step.keys()
                    if getattr(e, "name", None) in locals_to_remove]
        for e in to_remove:
            del self.event_birth_step[e]
            print(f"[Validator] Removed event from birth map: {e.name}")



    def _explain_retract_hasLocation(self, retract: Triple, step_index: int) -> Tuple[bool, Optional[Explanation]]:
        ep = self._create_change_event_for_retract(retract, step_index)

        s, p, o = retract
        subj = self.rt._get_entity(s)
        old_loc = self.rt._get_entity(o)

        if subj is None or old_loc is None:
            return False, None

        candidate_events = self._get_candidate_events_upto(step_index)

        scored_candidates = []
        for ev in candidate_events:
            if "background" in (self.event_tags.get(ev, []) or []):
                continue

            # Strict mode requires object-loss events to be directly anchored.
            if self.strict_object_loss_mode and self._requires_object_anchor(subj):
                if not self._strong_object_loss_ok(ev, subj, old_loc, step_index):
                    continue

                scored_candidates.append((2, ev, True))
                continue

            # Non-strict mode uses the broader validation rule set.
            if not self._when_ok(ev, step_index):
                continue
            if not self._where_ok(ev, old_loc):
                continue
            if not self._has_event_type(ev):
                continue

            anchor_ok = self._who_anchor_ok(ev, subj, old_loc)

            if self._requires_object_anchor(subj) and not anchor_ok:
                continue
            shared_obj = self._who_shared(ev, subj)
            score = 1
            if shared_obj:
                score += 1

            scored_candidates.append((score, ev, shared_obj))

        if not scored_candidates:
            return False, None


        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_event, shared = scored_candidates[0]
        if best_event is None:
            return False, None
        
        
        linked = self._assert_causal_link(best_event, ep)
        if linked:
            print(f"[CAUSAL-LINK] Added causal link: {best_event.name} -> {ep.name}")
        else:
            print(f"[CAUSAL-LINK] No causal property found / link not added for: {best_event.name} -> {ep.name}")



        ep_name = ep.name
        e_name = best_event.name
        birth = self.event_birth_step.get(best_event, None)

        if birth is not None:
            if birth < step_index:
                when_txt = f"E precedes Ep (birth_step(E)={birth} < step(Ep)={step_index})"
            elif birth == step_index:
                when_txt = f"E is concurrent with Ep (birth_step(E)={birth} = step(Ep)={step_index})"
            else:
                when_txt = f"E occurs after Ep (birth_step(E)={birth} > step(Ep)={step_index})"
        else:
            when_txt = "E birth step is unknown"

        e_loc = self._get_location(best_event)
        where_ok = self._where_ok(best_event, old_loc)
        where_txt = (
            f"E and Ep share a compatible location: "
            f"loc(E)={self._fmt_entity(e_loc)}, loc(Ep)={self._fmt_entity(old_loc)} -> "
            + ("compatible" if where_ok else "not compatible")
        )

        participants_E = self._get_participants(best_event)
        if shared:
            who_txt = (
                f"E and Ep share the main participant: {self._fmt_entity(subj)} "
                f"(E participants: {', '.join(self._fmt_entity(p) for p in participants_E)})"
            )
        else:
            who_txt = (
                "E and Ep do not share the main participant; "
                f"E participants: {', '.join(self._fmt_entity(p) for p in participants_E)}; "
                f"Ep main participant: {self._fmt_entity(subj)}"
            )


        event_types = self._get_event_types(best_event)
        if event_types:
            how_txt = f"E is linked to operational type/task: {', '.join(event_types)}"
        else:
            how_txt = "E lacks an operational type/task anchor (classifies / isOccurrenceOf / executesTask)"

        reason = (
            f"Event {e_name} was selected as the cause of {ep_name} for retract {retract}:\n"
            f"- When: {when_txt}.\n"
            f"- Where: {where_txt}.\n"
            f"- Who: {who_txt}.\n"
            f"- How: {how_txt}."
        )

        exp = Explanation(
            retract=retract,
            event_iri=best_event.iri,
            event_name=best_event.name,
            reason=reason,
        )
        return True, exp



    def _get_candidate_events_upto(self, step_index: int, window: int = 2) -> List[Thing]:
        lo = max(1, step_index - window)
        return [e for e, b_step in self.event_birth_step.items()
                if lo <= b_step <= step_index]

    def _when_ok(self, ev: Thing, ep_step: int) -> bool:
        b = self.event_birth_step.get(ev, None)
        return b is not None and b <= ep_step


    def _collect_locations(self, ent: Thing) -> List[Thing]:
        visited = set()
        frontier = [ent]
        locs = set()

        while frontier:
            cur = frontier.pop()
            if cur in visited:
                continue
            visited.add(cur)
            locs.add(cur)
            for pname in self.location_prop_names:
                prop = getattr(self.rt.ns, pname, None)
                if prop is None:
                    continue
                try:
                    vals = list(getattr(cur, prop.name))
                except AttributeError:
                    continue
                for v in vals:
                    if v not in visited:
                        frontier.append(v)
        return list(locs)



    def _get_location(self, ent: Thing) -> Optional[Thing]:
        for pname in self.location_prop_names:
            prop = getattr(self.rt.ns, pname, None)
            if prop is None:
                continue
            try:
                vals = list(getattr(ent, prop.name))
            except AttributeError:
                continue
            if vals:
                return vals[0]

        if ent in self.event_birth_step:
            participants = self._get_participants(ent)
            for part in participants:
                for pname in self.location_prop_names:
                    prop = getattr(self.rt.ns, pname, None)
                    if prop is None:
                        continue
                    try:
                        vals = list(getattr(part, prop.name))
                    except AttributeError:
                        continue
                    if vals:
                        return vals[0]

        return None


    def _where_ok(self, ev: Thing, ep_loc: Thing) -> bool:
        e_loc = self._get_location(ev)
        if e_loc is None:
            return False

        ep_locs = self._collect_locations(ep_loc)
        return e_loc in ep_locs


    def _get_participants(self, ev: Thing) -> List[Thing]:
        parts: List[Thing] = []
        for pname in self.participant_prop_names:
            prop = getattr(self.rt.ns, pname, None)
            if prop is None:
                continue
            try:
                vals = list(getattr(ev, prop.name))
            except AttributeError:
                continue
            parts.extend(vals)
        return parts
    
    def _fmt_entity(self, ent: Optional[Thing]) -> str:
        if ent is None:
            return "None"
        return ent.name

    def _get_event_types(self, ev: Thing) -> List[str]:
        type_names: List[str] = []
        for pname in self.event_type_prop_names:
            prop = getattr(self.rt.ns, pname, None)
            if prop is None:
                continue
            try:
                vals = list(getattr(ev, prop.name))
            except AttributeError:
                continue
            type_names.extend(v.name for v in vals)
        return type_names


    def _has_event_type(self, ev: Thing) -> bool:
        return len(self._get_event_types(ev)) > 0


    def _who_shared(self, ev: Thing, subj: Thing) -> bool:
        participants = self._get_participants(ev)
        return subj in participants
    
    
    def _who_anchor_ok(self, ev: Thing, subj: Thing, old_loc: Optional[Thing]) -> bool:
        participants = self._get_participants(ev)
        if subj in participants:
            return True
        if old_loc is not None and old_loc in participants:
            return True
        return False    


