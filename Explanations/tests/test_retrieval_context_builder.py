from benchmark.retrieval_context_builder import (
    retrieve_validator_guided_tbox_chunks,
    format_tbox_context,
)


def test_retrieve_validator_guided_tbox_chunks_real_file():
    chunks = retrieve_validator_guided_tbox_chunks()
    assert len(chunks) >= 1
    local_names = {chunk.local_name for chunk in chunks}

    assert "Event" in local_names
    assert "hasParticipant" in local_names


def test_format_tbox_context_real_file():
    text = format_tbox_context()
    assert "Retrieved TBox context from T_op:" in text
    assert "[TBOX CHUNK 1]" in text