import pytest

from benchmark.candidate_schema import (
    CandidateSchemaError,
    parse_candidate_output,
)


def make_valid_payload():
    return {
        "case_id": "CG1_base_loss_clean",
        "condition": "PC3",
        "candidates": [
            {
                "rank": 1,
                "event_type_label": "DropFromTray",
                "event_type_source": "inferred",
                "participants": ["PhysicalObject_Medicine1", "PhysicalObject_ShadowTray"],
                "location": "PhysicalPlace_Corridor1",
                "short_rationale": "The medicine may have fallen from the tray.",
                "operational_projection": {
                    "event_class": "DUL.Event",
                    "event_type": "EventType_DropFromTray",
                    "participants": ["PhysicalObject_Medicine1", "PhysicalObject_ShadowTray"],
                    "location": "PhysicalPlace_Corridor1",
                },
            }
        ],
    }


def test_parse_valid_candidate_output():
    payload = make_valid_payload()
    result = parse_candidate_output(payload)

    assert result.case_id == "CG1_base_loss_clean"
    assert result.condition == "PC3"
    assert len(result.candidates) == 1

    cand = result.candidates[0]
    assert cand.rank == 1
    assert cand.event_type_label == "DropFromTray"
    assert cand.event_type_source == "inferred"
    assert cand.participants == ["PhysicalObject_Medicine1", "PhysicalObject_ShadowTray"]
    assert cand.location == "PhysicalPlace_Corridor1"

    proj = cand.operational_projection
    assert proj.event_class == "DUL.Event"
    assert proj.event_type == "EventType_DropFromTray"
    assert proj.participants == ["PhysicalObject_Medicine1", "PhysicalObject_ShadowTray"]
    assert proj.location == "PhysicalPlace_Corridor1"


def test_accept_action_projection_with_event_type():
    payload = make_valid_payload()
    payload["candidates"][0]["operational_projection"]["event_class"] = "DUL.Action"
    payload["candidates"][0]["operational_projection"]["event_type"] = "Task_TakeMedicine"

    result = parse_candidate_output(payload)
    proj = result.candidates[0].operational_projection

    assert proj.event_class == "DUL.Action"
    assert proj.event_type == "Task_TakeMedicine"


def test_reject_invalid_condition():
    payload = make_valid_payload()
    payload["condition"] = "C99"

    with pytest.raises(CandidateSchemaError):
        parse_candidate_output(payload)


def test_reject_more_than_three_candidates():
    payload = make_valid_payload()
    payload["candidates"] = [
        payload["candidates"][0] | {"rank": 1},
        payload["candidates"][0] | {"rank": 2},
        payload["candidates"][0] | {"rank": 3},
        payload["candidates"][0] | {"rank": 4},
    ]

    with pytest.raises(CandidateSchemaError):
        parse_candidate_output(payload)


def test_reject_repeated_ranks():
    payload = make_valid_payload()
    payload["candidates"] = [
        payload["candidates"][0] | {"rank": 1},
        payload["candidates"][0] | {"rank": 1, "event_type_label": "Collision"},
    ]

    with pytest.raises(CandidateSchemaError):
        parse_candidate_output(payload)


def test_reject_invalid_event_type_source():
    payload = make_valid_payload()
    payload["candidates"][0]["event_type_source"] = "random_source"

    with pytest.raises(CandidateSchemaError):
        parse_candidate_output(payload)


def test_reject_invalid_projection_event_class():
    payload = make_valid_payload()
    payload["candidates"][0]["operational_projection"]["event_class"] = "DUL.Process"

    with pytest.raises(CandidateSchemaError):
        parse_candidate_output(payload)


def test_reject_missing_operational_projection():
    payload = make_valid_payload()
    del payload["candidates"][0]["operational_projection"]

    with pytest.raises(CandidateSchemaError):
        parse_candidate_output(payload)


def test_deduplicate_participants():
    payload = make_valid_payload()
    payload["candidates"][0]["participants"] = [
        "PhysicalObject_Medicine1",
        "PhysicalObject_Medicine1",
        "PhysicalObject_ShadowTray",
    ]
    payload["candidates"][0]["operational_projection"]["participants"] = [
        "PhysicalObject_Medicine1",
        "PhysicalObject_Medicine1",
        "PhysicalObject_ShadowTray",
    ]

    result = parse_candidate_output(payload)

    cand = result.candidates[0]
    assert cand.participants == [
        "PhysicalObject_Medicine1",
        "PhysicalObject_ShadowTray",
    ]
    assert cand.operational_projection.participants == [
        "PhysicalObject_Medicine1",
        "PhysicalObject_ShadowTray",
    ]
    
    
def test_reject_missing_projection_event_type():
    payload = make_valid_payload()
    del payload["candidates"][0]["operational_projection"]["event_type"]

    with pytest.raises(CandidateSchemaError):
        parse_candidate_output(payload)
