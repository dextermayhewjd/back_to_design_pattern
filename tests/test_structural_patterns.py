from design_patterns.catalog.structural import STRUCTURAL_PATTERNS
from design_patterns.models import Category

def test_structural_patterns_loaded():
    assert len(STRUCTURAL_PATTERNS) == 7
    ids = {p.id for p in STRUCTURAL_PATTERNS}
    expected_ids = {"adapter", "bridge", "composite", "decorator", "facade", "flyweight", "proxy"}
    assert ids == expected_ids
    for p in STRUCTURAL_PATTERNS:
        assert p.category == Category.STRUCTURAL
        assert len(p.intent) > 0
        assert len(p.problem) > 0
        assert len(p.solution) > 0
        assert len(p.applicability) > 0
        assert len(p.symptoms) > 0
        compile(p.conceptual_code, f"{p.id}_conceptual", "exec")
        compile(p.realworld_code, f"{p.id}_realworld", "exec")
        compile(p.scaffold_template, f"{p.id}_scaffold", "exec")
