from benchmark.scoring import score_raw_output


def make_valid_payload():
    return {
        "case_id": "CG1_base_loss_clean",
        "condition": "PC3",
        "candidates": [
            {
                "rank": 1,
                "event_type_label": "TakeMedicine",
                "event_type_source": "T_op",
                "participants": ["Agent_Nurse", "PhysicalObject_Medicine1"],
                "location": "PhysicalPlace_Corridor1",
                "short_rationale": "The nurse may have taken the medicine.",
                "operational_projection": {
                    "event_class": "DUL.Action",
                    "event_type": "Task_TakeMedicine",
                    "participants": ["Agent_Nurse", "PhysicalObject_Medicine1"],
                    "location": "PhysicalPlace_Corridor1",
                },
            }
        ],
    }


def test_score_valid_output_all_grounded():
    payload = make_valid_payload()
    known_entities = {
        "Agent_Nurse",
        "PhysicalObject_Medicine1",
        "PhysicalPlace_Corridor1",
    }

    result = score_raw_output(payload, known_entities)

    assert result.schema_valid is True
    assert result.parse_error is None
    assert result.candidate_count == 1
    assert result.average_existing_anchor_rate == 1.0
    assert result.average_novel_schema_rate == 0.0
    assert result.average_grounding_rate == 1.0
    assert result.average_hallucination_rate == 0.0

    cand = result.candidates[0]
    assert cand.referenced_entities == [
        "Agent_Nurse",
        "PhysicalObject_Medicine1",
        "PhysicalPlace_Corridor1",
    ]
    assert cand.grounded_entities == [
        "Agent_Nurse",
        "PhysicalObject_Medicine1",
        "PhysicalPlace_Corridor1",
    ]
    assert cand.novel_schema_entities == []
    assert cand.invalid_entities == []
    assert cand.existing_anchor_rate == 1.0
    assert cand.novel_schema_rate == 0.0


def test_score_valid_output_with_novel_schema_entity():
    payload = make_valid_payload()
    payload["candidates"][0]["participants"] = [
        "Agent_Unknown",
        "PhysicalObject_Medicine1",
    ]
    payload["candidates"][0]["operational_projection"]["participants"] = [
        "Agent_Unknown",
        "PhysicalObject_Medicine1",
    ]

    known_entities = {
        "PhysicalObject_Medicine1",
        "PhysicalPlace_Corridor1",
    }

    result = score_raw_output(payload, known_entities)

    assert result.schema_valid is True
    assert result.candidate_count == 1
    assert result.average_existing_anchor_rate < 1.0
    assert result.average_novel_schema_rate > 0.0
    assert result.average_grounding_rate == 1.0
    assert result.average_hallucination_rate == 0.0

    cand = result.candidates[0]
    assert "Agent_Unknown" in cand.novel_schema_entities
    assert "PhysicalObject_Medicine1" in cand.grounded_entities
    assert cand.invalid_entities == []


def test_score_valid_output_with_invalid_symbol():
    payload = make_valid_payload()
    payload["candidates"][0]["participants"] = [
        "Unknown",
        "PhysicalObject_Medicine1",
    ]
    payload["candidates"][0]["operational_projection"]["participants"] = [
        "Unknown",
        "PhysicalObject_Medicine1",
    ]

    known_entities = {
        "PhysicalObject_Medicine1",
        "PhysicalPlace_Corridor1",
    }

    result = score_raw_output(payload, known_entities)

    assert result.schema_valid is True
    assert result.candidate_count == 1
    assert result.average_existing_anchor_rate < 1.0
    assert result.average_novel_schema_rate == 0.0
    assert result.average_grounding_rate < 1.0
    assert result.average_hallucination_rate > 0.0

    cand = result.candidates[0]
    assert "Unknown" in cand.invalid_entities


def test_score_invalid_output():
    payload = {
        "case_id": "CG1_base_loss_clean",
        "condition": "PC3",
        "candidates": []
    }

    known_entities = {
        "Agent_Nurse",
        "PhysicalObject_Medicine1",
        "PhysicalPlace_Corridor1",
    }

    result = score_raw_output(payload, known_entities)

    assert result.schema_valid is False
    assert result.parse_error is not None
    assert result.candidate_count == 0
    assert result.average_existing_anchor_rate == 0.0
    assert result.average_novel_schema_rate == 0.0
    assert result.average_grounding_rate == 0.0
    assert result.average_hallucination_rate == 0.0
    assert result.candidates == []
