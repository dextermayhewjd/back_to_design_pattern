"""End-to-end execution verification tests for all 22 GoF patterns."""

import sys
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


def test_all_patterns_run_cli_classic(capsys):
    """Verify pat run <id> --py classic succeeds with exit code 0 for all 22 patterns."""
    for pattern in ALL_PATTERNS:
        ret = main(["run", pattern.id, "--py", "classic"])
        assert ret == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert f"Running {pattern.name} (classic)" in captured.out


def test_all_patterns_run_cli_python310(capsys):
    """Verify pat run <id> --py 3.10 succeeds with exit code 0 for all 22 patterns."""
    for pattern in ALL_PATTERNS:
        ret = main(["run", pattern.id, "--py", "3.10"])
        assert ret == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert f"Running {pattern.name} (3.10)" in captured.out


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Requires Python 3.12+ for PEP 695 generic syntax")
def test_all_patterns_run_cli_python312(capsys):
    """Verify pat run <id> --py 3.12 succeeds with exit code 0 for all 22 patterns on Python 3.12+."""
    for pattern in ALL_PATTERNS:
        ret = main(["run", pattern.id, "--py", "3.12"])
        assert ret == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert f"Running {pattern.name} (3.12)" in captured.out


@pytest.mark.parametrize("pattern", ALL_PATTERNS, ids=lambda p: p.id)
@pytest.mark.parametrize("code_type", ["conceptual", "realworld"])
def test_individual_pattern_execution(capsys, pattern, code_type):
    """Granular test for individual pattern execution to ensure traceability."""
    ret = main(["run", pattern.id, "--type", code_type])
    assert ret == 0
    captured = capsys.readouterr()
    assert len(captured.out) > 0
    assert f"Running {pattern.name} ({code_type})" in captured.out


@pytest.mark.parametrize("pattern", ALL_PATTERNS, ids=lambda p: p.id)
@pytest.mark.parametrize("py_tier", ["classic", "3.10"])
def test_individual_pattern_execution_tiers(capsys, pattern, py_tier):
    """Granular test for individual pattern execution across classic and 3.10 tiers."""
    ret = main(["run", pattern.id, "--py", py_tier])
    assert ret == 0
    captured = capsys.readouterr()
    assert len(captured.out) > 0
    assert f"Running {pattern.name} ({py_tier})" in captured.out


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Requires Python 3.12+ for PEP 695 generic syntax")
@pytest.mark.parametrize("pattern", ALL_PATTERNS, ids=lambda p: p.id)
def test_individual_pattern_execution_tier_312(capsys, pattern):
    """Granular test for individual pattern execution on Python 3.12 tier."""
    ret = main(["run", pattern.id, "--py", "3.12"])
    assert ret == 0
    captured = capsys.readouterr()
    assert len(captured.out) > 0
    assert f"Running {pattern.name} (3.12)" in captured.out

