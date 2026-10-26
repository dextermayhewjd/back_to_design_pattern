"""End-to-end execution verification tests for all 22 GoF patterns."""

import pytest
from design_patterns.catalog import ALL_PATTERNS
from design_patterns.cli import main


def test_all_patterns_run_without_exception(capsys):
    """Test that all 22 patterns run without exception via conceptual mode."""
    for pattern in ALL_PATTERNS:
        ret = main(["run", pattern.id, "--type", "conceptual"])
        assert ret == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0


def test_all_patterns_realworld_run_without_exception(capsys):
    """Test that all 22 patterns run without exception via realworld mode."""
    for pattern in ALL_PATTERNS:
        ret = main(["run", pattern.id, "--type", "realworld"])
        assert ret == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0


@pytest.mark.parametrize("pattern", ALL_PATTERNS, ids=lambda p: p.id)
@pytest.mark.parametrize("code_type", ["conceptual", "realworld"])
def test_individual_pattern_execution(capsys, pattern, code_type):
    """Granular test for individual pattern execution to ensure traceability."""
    ret = main(["run", pattern.id, "--type", code_type])
    assert ret == 0
    captured = capsys.readouterr()
    assert len(captured.out) > 0
    assert f"Running {pattern.name} ({code_type})" in captured.out
