from types import SimpleNamespace

from benchmark.local_graph_context_builder import (
    build_local_graph_context,
    format_local_graph_context,
)


def test_build_local_graph_context(monkeypatch):
    fake_ctx = SimpleNamespace(
        known_entities={
            "PhysicalObject_Medicine1",
            "PhysicalObject_ShadowTray",
            "Agent_Shadow",
            "Agent_Nurse",
            "PhysicalPlace_Corridor1",
        },
        known_triples=[
            ("PhysicalObject_Medicine1", "DUL.hasLocation", "PhysicalObject_ShadowTray"),
            ("PhysicalObject_ShadowTray", "DUL.hasLocation", "Agent_Shadow"),
            ("Agent_Shadow", "DUL.hasLocation", "PhysicalPlace_Corridor1"),
            ("Agent_Nurse", "DUL.hasLocation", "PhysicalPlace_Corridor1"),
            ("Agent_Shadow", "DUL.executesTask", "Task_FollowSupervisor"),
            ("X", "DUL.isAbout", "Y"),  # should be ignored
        ],
    )

    monkeypatch.setattr(
        "benchmark.local_graph_context_builder.get_case_context",
        lambda case_id: fake_ctx,
    )

    ctx = build_local_graph_context("CG1_base_loss_clean")

    assert ctx.case_id == "CG1_base_loss_clean"
    assert "PhysicalObject_Medicine1" in ctx.anchors
    assert ("PhysicalObject_Medicine1", "DUL.hasLocation", "PhysicalObject_ShadowTray") in ctx.triples
    assert all(triple[1] != "DUL.isAbout" for triple in ctx.triples)


def test_format_local_graph_context(monkeypatch):
    fake_ctx = SimpleNamespace(
        known_entities={
            "PhysicalObject_Medicine1",
            "PhysicalObject_ShadowTray",
            "Agent_Shadow",
        },
        known_triples=[
            ("PhysicalObject_Medicine1", "DUL.hasLocation", "PhysicalObject_ShadowTray"),
            ("PhysicalObject_ShadowTray", "DUL.hasLocation", "Agent_Shadow"),
        ],
    )

    monkeypatch.setattr(
        "benchmark.local_graph_context_builder.get_case_context",
        lambda case_id: fake_ctx,
    )

    text = format_local_graph_context("CG1_base_loss_clean")

    assert "Retrieved local ABox context:" in text
    assert "PhysicalObject_Medicine1 --DUL.hasLocation--> PhysicalObject_ShadowTray" in text