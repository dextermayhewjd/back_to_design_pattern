"""Tests for pat matrix subcommand and 3-tier version evolution matrix display."""

import json
import pytest
from design_patterns.catalog import ALL_PATTERNS
from design_patterns.cli import main


def test_cli_matrix_strategy(capsys):
    ret = main(["matrix", "strategy"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Evolution Matrix: Strategy (strategy)" in captured.out
    assert "Tier" in captured.out
    assert "Lines" in captured.out
    assert "Key Features" in captured.out
    assert "Summary" in captured.out
    assert "classic" in captured.out
    assert "3.10+" in captured.out
    assert "3.12+" in captured.out
    assert "Evolution Notes:" in captured.out
    assert "[classic]" in captured.out
    assert "[3.10+]" in captured.out
    assert "[3.12+]" in captured.out


def test_cli_matrix_json(capsys):
    ret = main(["matrix", "strategy", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["id"] == "strategy"
    assert data["name"] == "Strategy"
    assert "tiers" in data
    assert len(data["tiers"]) == 3

    tiers = {t["tier"]: t for t in data["tiers"]}
    assert "classic" in tiers
    assert "3.10+" in tiers
    assert "3.12+" in tiers

    for tag, t in tiers.items():
        assert t["lines"] > 0
        assert isinstance(t["key_features"], list)
        assert len(t["summary"]) > 0
        assert len(t["code"]) > 0


def test_cli_matrix_all_patterns():
    for p in ALL_PATTERNS:
        # Verify matrix works for each pattern in the catalog
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main(["matrix", p.id, "--json"])
        assert ret == 0
        data = json.loads(buf.getvalue())
        assert data["id"] == p.id
        assert len(data["tiers"]) == 3


def test_cli_matrix_unknown_pattern(capsys):
    ret = main(["matrix", "unknown-pattern"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Pattern 'unknown-pattern' not found" in captured.err


def test_cli_matrix_fuzzy_suggestion(capsys):
    ret = main(["matrix", "singletn"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Did you mean: singleton" in captured.err
