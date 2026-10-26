"""Tests for 3-tier Python version evolution matrix across all 22 GoF patterns."""

import sys
import pytest
from design_patterns.catalog import ALL_PATTERNS
from design_patterns.models import VersionEvolution


def test_all_patterns_have_3tier_evolution_matrix():
    assert len(ALL_PATTERNS) == 22
    for p in ALL_PATTERNS:
        assert len(p.classic_code.strip()) > 0, f"{p.id} missing classic_code"
        assert len(p.python310_code.strip()) > 0, f"{p.id} missing python310_code"
        assert len(p.python312_code.strip()) > 0, f"{p.id} missing python312_code"
        assert "classic" in p.matrix_notes, f"{p.id} missing classic matrix note"
        assert "3.10" in p.matrix_notes, f"{p.id} missing 3.10 matrix note"
        assert "3.12" in p.matrix_notes, f"{p.id} missing 3.12 matrix note"

        # Backward compatibility properties
        assert p.conceptual_code == p.classic_code
        assert p.realworld_code == p.python310_code
        assert p.pythonic_code in (p.python312_code, p.python310_code)
        assert p.pythonic_notes == p.matrix_notes.get("3.10", "")

        evo_classic = p.get_evolution("classic")
        assert isinstance(evo_classic, VersionEvolution)
        assert evo_classic.version_tag == "classic"
        assert len(evo_classic.summary) > 0
        assert isinstance(evo_classic.key_features, list)
        assert evo_classic.code == p.classic_code
        assert evo_classic.line_count > 0

        evo_310 = p.get_evolution("3.10")
        assert isinstance(evo_310, VersionEvolution)
        assert evo_310.version_tag == "3.10+"
        assert len(evo_310.summary) > 0
        assert evo_310.code == p.python310_code
        assert evo_310.line_count > 0

        evo_312 = p.get_evolution("3.12")
        assert isinstance(evo_312, VersionEvolution)
        assert evo_312.version_tag == "3.12+"
        assert len(evo_312.summary) > 0
        assert evo_312.code == p.python312_code
        assert evo_312.line_count > 0

        # Version string normalization
        assert p.get_evolution("3.10+").version_tag == "3.10+"
        assert p.get_evolution("3.12+").version_tag == "3.12+"

        # Compilation of classic and 3.10 code
        compile(p.classic_code, f"{p.id}_classic", "exec")
        compile(p.python310_code, f"{p.id}_python310", "exec")


def test_all_patterns_classic_code_executes():
    for p in ALL_PATTERNS:
        exec_scope = {"__name__": "__main__"}
        exec(p.classic_code, exec_scope)


def test_all_patterns_python310_code_executes():
    for p in ALL_PATTERNS:
        exec_scope = {"__name__": "__main__"}
        exec(p.python310_code, exec_scope)


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Requires Python 3.12+ to compile PEP 695 syntax")
def test_all_patterns_312_code_compiles_and_executes():
    for p in ALL_PATTERNS:
        compile(p.python312_code, f"{p.id}_python312", "exec")
        exec_scope = {"__name__": "__main__"}
        exec(p.python312_code, exec_scope)


def test_get_evolution_invalid_version():
    pattern = ALL_PATTERNS[0]
    with pytest.raises(ValueError, match="Unknown evolution version"):
        pattern.get_evolution("python2.7")
