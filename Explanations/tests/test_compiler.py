from benchmark.candidate_schema import parse_candidate_output
from benchmark.compiler import (
    compile_candidate_output,
    compile_candidate_to_step,
    make_generated_event_id,
    make_step_name,
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
                "participants": ["PhysicalObject_ShadowTray", "PhysicalObject_Medicine1"],
                "location": "PhysicalPlace_Corridor1",
                "short_rationale": "The medicine may have fallen from the tray.",
                "operational_projection": {
                    "event_class": "DUL.Event",
                    "event_type": "EventType_DropFromTray",
                    "participants": ["PhysicalObject_ShadowTray", "PhysicalObject_Medicine1"],
                    "location": "PhysicalPlace_Corridor1",
                },
            }
        ],
    }


def test_make_generated_event_id():
    assert make_generated_event_id("CG1_base_loss_clean", 1) == "GeneratedEvent_CG1_base_loss_clean_R1"


def test_make_step_name():
    assert make_step_name("CG1_base_loss_clean", 1) == "GEN_CG1_base_loss_clean_R1"


def test_compile_candidate_to_step_with_event_type():
    parsed = parse_candidate_output(make_valid_payload())
    candidate = parsed.candidates[0]

    compiled = compile_candidate_to_step(parsed.case_id, candidate)

    assert compiled.case_id == "CG1_base_loss_clean"
    assert compiled.rank == 1
    assert compiled.event_id == "GeneratedEvent_CG1_base_loss_clean_R1"
    assert compiled.step_name == "GEN_CG1_base_loss_clean_R1"

    step = compiled.step
    assert step.name == "GEN_CG1_base_loss_clean_R1"
    assert step.types == [
        ("GeneratedEvent_CG1_base_loss_clean_R1", "DUL.Event"),
        ("EventType_DropFromTray", "SOMA.EventType"),
    ]

    assert step.asserts == [
        ("GeneratedEvent_CG1_base_loss_clean_R1", "SOMA.isOccurrenceOf", "EventType_DropFromTray"),
        ("GeneratedEvent_CG1_base_loss_clean_R1", "DUL.hasParticipant", "PhysicalObject_Medicine1"),
        ("GeneratedEvent_CG1_base_loss_clean_R1", "DUL.hasParticipant", "PhysicalObject_ShadowTray"),
        ("GeneratedEvent_CG1_base_loss_clean_R1", "DUL.hasLocation", "PhysicalPlace_Corridor1"),
    ]


def test_compile_candidate_to_step_with_event_type():
    payload = make_valid_payload()
    payload["candidates"][0]["operational_projection"]["event_class"] = "DUL.Action"
    payload["candidates"][0]["operational_projection"]["event_type"] = "Task_TakeMedicine"
    payload["candidates"][0]["operational_projection"]["participants"] = [
        "PhysicalObject_Medicine1",
        "Agent_Nurse",
    ]

    parsed = parse_candidate_output(payload)
    candidate = parsed.candidates[0]

    compiled = compile_candidate_to_step(parsed.case_id, candidate)
    step = compiled.step

    assert step.types == [
        ("GeneratedEvent_CG1_base_loss_clean_R1", "DUL.Action"),
        ("Task_TakeMedicine", "SOMA.EventType"),
    ]
    assert step.asserts == [
        ("GeneratedEvent_CG1_base_loss_clean_R1", "SOMA.isOccurrenceOf", "Task_TakeMedicine"),
        ("GeneratedEvent_CG1_base_loss_clean_R1", "DUL.hasParticipant", "Agent_Nurse"),
        ("GeneratedEvent_CG1_base_loss_clean_R1", "DUL.hasParticipant", "PhysicalObject_Medicine1"),
        ("GeneratedEvent_CG1_base_loss_clean_R1", "DUL.hasLocation", "PhysicalPlace_Corridor1"),
    ]


def test_compile_candidate_output():
    parsed = parse_candidate_output(make_valid_payload())
    compiled = compile_candidate_output(parsed)

    assert len(compiled) == 1
    assert compiled[0].rank == 1
    assert compiled[0].step.name == "GEN_CG1_base_loss_clean_R1"


def test_compile_without_location():
    payload = make_valid_payload()
    payload["candidates"][0]["location"] = None
    payload["candidates"][0]["operational_projection"]["location"] = None

    parsed = parse_candidate_output(payload)
    compiled = compile_candidate_output(parsed)

    step = compiled[0].step
    assert step.asserts == [
        ("GeneratedEvent_CG1_base_loss_clean_R1", "SOMA.isOccurrenceOf", "EventType_DropFromTray"),
        ("GeneratedEvent_CG1_base_loss_clean_R1", "DUL.hasParticipant", "PhysicalObject_Medicine1"),
        ("GeneratedEvent_CG1_base_loss_clean_R1", "DUL.hasParticipant", "PhysicalObject_ShadowTray"),
    ]
