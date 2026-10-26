from design_patterns.catalog.creational import CREATIONAL_PATTERNS
from design_patterns.models import Category

def test_creational_patterns_loaded():
    assert len(CREATIONAL_PATTERNS) == 5
    ids = {p.id for p in CREATIONAL_PATTERNS}
    expected_ids = {"factory-method", "abstract-factory", "builder", "prototype", "singleton"}
    assert ids == expected_ids
    for p in CREATIONAL_PATTERNS:
        assert p.category == Category.CREATIONAL
        assert len(p.intent) > 0
        assert len(p.problem) > 0
        assert len(p.solution) > 0
        assert len(p.applicability) > 0
        assert len(p.symptoms) > 0
        # Verify Python code parses without syntax error
        compile(p.conceptual_code, f"{p.id}_conceptual", "exec")
        compile(p.realworld_code, f"{p.id}_realworld", "exec")
        compile(p.scaffold_template, f"{p.id}_scaffold", "exec")
