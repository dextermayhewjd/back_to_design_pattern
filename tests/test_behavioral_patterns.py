from design_patterns.catalog import ALL_PATTERNS, load_default_registry
from design_patterns.catalog.behavioral import BEHAVIORAL_PATTERNS
from design_patterns.models import Category

def test_behavioral_patterns_loaded():
    assert len(BEHAVIORAL_PATTERNS) == 10
    expected_ids = {
        "chain-of-responsibility", "command", "iterator", "mediator",
        "memento", "observer", "state", "strategy", "template-method", "visitor"
    }
    assert {p.id for p in BEHAVIORAL_PATTERNS} == expected_ids
    for p in BEHAVIORAL_PATTERNS:
        assert p.category == Category.BEHAVIORAL
        assert len(p.intent) > 0
        assert len(p.problem) > 0
        assert len(p.solution) > 0
        assert len(p.applicability) > 0
        assert len(p.symptoms) > 0
        compile(p.conceptual_code, f"{p.id}_conceptual", "exec")
        compile(p.realworld_code, f"{p.id}_realworld", "exec")
        compile(p.scaffold_template, f"{p.id}_scaffold", "exec")

def test_all_22_patterns_in_master_registry():
    registry = load_default_registry()
    assert registry.count() == 22
    assert len(registry.list_all(Category.CREATIONAL)) == 5
    assert len(registry.list_all(Category.STRUCTURAL)) == 7
    assert len(registry.list_all(Category.BEHAVIORAL)) == 10
    assert len(ALL_PATTERNS) == 22
