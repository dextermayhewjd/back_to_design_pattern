import json
import os
import subprocess
import sys
from pathlib import Path
import pytest
from design_patterns.cli import main


def test_cli_no_args(capsys):
    ret = main([])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Available subcommands" in captured.out or "usage: pat" in captured.out


def test_cli_list_text(capsys):
    ret = main(["list"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Total: 22 patterns" in captured.out
    assert "singleton" in captured.out
    assert "strategy" in captured.out


def test_cli_list_json(capsys):
    ret = main(["list", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 22
    assert any(p["id"] == "singleton" for p in data)


def test_cli_list_category_filter(capsys):
    ret = main(["list", "--category", "creational", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 5

    ret_s = main(["list", "-c", "structural", "--json"])
    assert ret_s == 0
    data_s = json.loads(capsys.readouterr().out)
    assert len(data_s) == 7

    ret_b = main(["list", "-c", "behavioral", "--json"])
    assert ret_b == 0
    data_b = json.loads(capsys.readouterr().out)
    assert len(data_b) == 10


def test_cli_show_text(capsys):
    ret = main(["show", "singleton"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "# Singleton" in captured.out
    assert "意图 (Intent)" in captured.out
    assert "问题 (Problem)" in captured.out
    assert "解决方案 (Solution)" in captured.out
    assert "适合应用场景 (Applicability)" in captured.out
    assert "优缺点 (Pros & Cons)" in captured.out


def test_cli_show_json(capsys):
    ret = main(["show", "singleton", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["id"] == "singleton"
    assert data["name"] == "Singleton"
    assert "intent" in data
    assert "applicability" in data
    assert "pros" in data
    assert "cons" in data
    assert "relations" in data


def test_cli_show_unknown_pattern(capsys):
    ret = main(["show", "non-existent-pattern"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Pattern 'non-existent-pattern' not found" in captured.err
    assert "Run 'pat list' to see all available patterns." in captured.err


def test_cli_show_close_match_suggestion(capsys):
    ret = main(["show", "singletn"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Did you mean: singleton" in captured.err


def test_cli_code_conceptual(capsys):
    ret = main(["code", "singleton", "--type", "conceptual"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "class Singleton" in captured.out


def test_cli_code_realworld(capsys):
    ret = main(["code", "singleton", "--type", "realworld"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "class " in captured.out


def test_cli_code_json(capsys):
    ret = main(["code", "singleton", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["id"] == "singleton"
    assert "code" in data
    # Defaults to pythonic (3.12 on 3.12, 3.10 on 3.10)
    assert "ServiceRegistry" in data["code"] or "get_settings" in data["code"]


def test_cli_code_json_conceptual(capsys):
    ret = main(["code", "singleton", "--type", "conceptual", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["id"] == "singleton"
    assert data["type"] == "conceptual"
    assert "code" in data
    assert "class Singleton" in data["code"]


def test_cli_code_unknown(capsys):
    ret = main(["code", "unknown-pattern"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Pattern 'unknown-pattern' not found" in captured.err


def test_cli_scaffold_stdout(capsys):
    ret = main(["scaffold", "singleton"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Singleton" in captured.out


def test_cli_scaffold_json(capsys):
    ret = main(["scaffold", "singleton", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["id"] == "singleton"
    assert "scaffold_template" in data


def test_cli_scaffold_to_file(tmp_path):
    target = tmp_path / "factory.py"
    ret = main(["scaffold", "factory-method", "--out", str(target)])
    assert ret == 0
    assert target.exists()
    assert "Factory Method" in target.read_text(encoding="utf-8")


def test_cli_scaffold_no_overwrite(tmp_path, capsys):
    target = tmp_path / "factory.py"
    target.write_text("existing code")
    ret = main(["scaffold", "factory-method", "--out", str(target)])
    assert ret == 1
    assert target.read_text() == "existing code"
    captured = capsys.readouterr()
    assert "already exists. Use --overwrite" in captured.err


def test_cli_scaffold_overwrite(tmp_path):
    target = tmp_path / "factory.py"
    target.write_text("existing code")
    ret = main(["scaffold", "factory-method", "--out", str(target), "--overwrite"])
    assert ret == 0
    assert "Factory Method" in target.read_text(encoding="utf-8")


def test_cli_scaffold_unknown(capsys):
    ret = main(["scaffold", "unknown-pat"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Pattern 'unknown-pat' not found" in captured.err


def test_cli_scaffold_py_flag(tmp_path):
    target_310 = tmp_path / "strategy_310.py"
    ret = main(["scaffold", "strategy", "-o", str(target_310), "--py", "3.10"])
    assert ret == 0
    assert target_310.exists()
    content_310 = target_310.read_text(encoding="utf-8")
    assert "Callable" in content_310

    target_classic = tmp_path / "strategy_classic.py"
    ret = main(["scaffold", "strategy", "-o", str(target_classic), "--py", "classic"])
    assert ret == 0
    assert target_classic.exists()
    content_classic = target_classic.read_text(encoding="utf-8")
    assert "ABC" in content_classic


def test_cli_recommend_query(capsys):
    ret = main(["recommend", "-q", "swap interchangeable algorithms at runtime"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Strategy" in captured.out


def test_cli_recommend_query_json(capsys):
    ret = main(["recommend", "-q", "swap interchangeable algorithms", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == "strategy"


def test_cli_recommend_empty_query(capsys):
    ret = main(["recommend", "-q", ""])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Please provide a query" in captured.err


def test_cli_recommend_no_args(capsys):
    ret = main(["recommend"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Specify a query with -q/--query or run --interactive" in captured.err


def test_cli_recommend_no_match(capsys):
    ret = main(["recommend", "-q", "zzzzxxxxqqqqrandomwords"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "No matching design pattern found with high confidence" in captured.out


def test_cli_run_conceptual(capsys):
    ret = main(["run", "singleton", "--type", "conceptual"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "--- Running Singleton (conceptual) ---" in captured.out


def test_cli_run_realworld(capsys):
    ret = main(["run", "singleton", "--type", "realworld"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "--- Running Singleton (realworld) ---" in captured.out


def test_cli_run_unknown(capsys):
    ret = main(["run", "non-existent"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Pattern 'non-existent' not found" in captured.err


def test_bin_pat_standalone(tmp_path):
    project_root = Path(__file__).resolve().parent.parent
    pat_bin = project_root / "bin" / "pat"
    assert pat_bin.exists()
    assert os.access(pat_bin, os.X_OK)

    # Run from an external directory (tmp_path) with empty PYTHONPATH
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    proc = subprocess.run(
        [sys.executable, str(pat_bin), "list", "--json"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert len(data) == 22


def test_python_module_standalone(tmp_path):
    project_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "src")

    proc = subprocess.run(
        [sys.executable, "-m", "design_patterns", "list", "--json"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert len(data) == 22


def test_cli_search_subcommand(capsys):
    ret = main(["search", "swap algorithm"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Strategy" in captured.out


def test_cli_search_json(capsys):
    ret = main(["search", "swap algorithm", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) > 0
    assert data[0]["id"] == "strategy"


def test_cli_diagnose_subcommand(monkeypatch, capsys):
    mock_inputs = iter(["1", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(mock_inputs))
    ret = main(["diagnose"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Factory Method" in captured.out


def test_cli_diagnose_interrupted(monkeypatch):
    def raise_interrupt(_):
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", raise_interrupt)
    ret = main(["diagnose"])
    assert ret == 0


def test_cli_scaffold_force(tmp_path):
    target = tmp_path / "factory.py"
    target.write_text("existing code")
    ret = main(["scaffold", "factory-method", "--out", str(target), "--force"])
    assert ret == 0
    assert "Factory Method" in target.read_text(encoding="utf-8")


def test_cli_scaffold_target_is_dir(tmp_path, capsys):
    dir_path = tmp_path / "somedir"
    dir_path.mkdir()
    ret = main(["scaffold", "factory-method", "--out", str(dir_path)])
    assert ret == 1
    captured = capsys.readouterr()
    assert captured.err == f"Error: Target path '{dir_path}' is a directory, not a file.\n"


def test_cli_show_summary(capsys):
    ret = main(["show", "factory-method", "--summary"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Factory Method" in captured.out
    assert "意图 (Intent)" in captured.out
    assert "## 优缺点" not in captured.out
    assert "## 与其他模式的关系" not in captured.out


def test_cli_show_summary_json(capsys):
    ret = main(["show", "factory-method", "--summary", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["id"] == "factory-method"
    assert "intent" in data
    assert "problem" not in data


def test_cli_code_defaults_to_pythonic(capsys):
    ret = main(["code", "strategy"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Callable" in captured.out or "def " in captured.out


def test_cli_code_py_options(capsys):
    # Test classic
    ret = main(["code", "strategy", "--py", "classic"])
    assert ret == 0
    out_classic = capsys.readouterr().out
    assert "class Strategy(ABC)" in out_classic

    # Test 3.10
    ret = main(["code", "strategy", "--py", "3.10"])
    assert ret == 0
    out_310 = capsys.readouterr().out
    assert "Callable" in out_310

    # Test 3.12
    ret = main(["code", "strategy", "--py", "3.12"])
    assert ret == 0
    out_312 = capsys.readouterr().out
    assert "[" in out_312 and "]" in out_312  # PEP 695 generics


def test_cli_code_type_backward_compatibility(capsys):
    # --type conceptual maps to classic
    ret = main(["code", "strategy", "--type", "conceptual"])
    assert ret == 0
    assert "class Strategy(ABC)" in capsys.readouterr().out

    # --type classic-oop maps to classic
    ret = main(["code", "strategy", "--type", "classic-oop"])
    assert ret == 0
    assert "class Strategy(ABC)" in capsys.readouterr().out

    # --type pythonic maps to pythonic
    ret = main(["code", "strategy", "--type", "pythonic"])
    assert ret == 0
    assert "Callable" in capsys.readouterr().out

    # --type realworld maps to pythonic
    ret = main(["code", "strategy", "--type", "realworld"])
    assert ret == 0
    assert "Callable" in capsys.readouterr().out


def test_cli_run_version_gating(monkeypatch, capsys):
    # Simulate Python 3.10 runtime
    monkeypatch.setattr(sys, "version_info", (3, 10, 8, "final", 0))
    monkeypatch.setattr(sys, "version", "3.10.8 (main, Oct 2023)")
    ret = main(["run", "strategy", "--py", "3.12"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Python 3.12+ is required to execute PEP 695 syntax (current: 3.10.8)." in captured.err


def test_cli_analyze_file(tmp_path, capsys):
    sample = tmp_path / "calculator.py"
    sample.write_text("""
class TaxCalculator:
    def execute(self, amount: float) -> float:
        return amount * 0.1
""")
    ret = main(["analyze", str(sample)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Scanned 1 files" in captured.out
    assert "SINGLE_METHOD_CLASS" in captured.out
    assert "TaxCalculator" in captured.out
    assert "strategy" in captured.out
    assert "Python 3.10+" in captured.out


def test_cli_analyze_directory(tmp_path, capsys):
    file1 = tmp_path / "calc.py"
    file1.write_text("""
class TaxCalculator:
    def execute(self, amount: float) -> float:
        return amount * 0.1
""")
    file2 = tmp_path / "helper.py"
    file2.write_text("def helper(): pass\n")

    ret = main(["analyze", str(tmp_path)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Scanned 2 files" in captured.out
    assert "SINGLE_METHOD_CLASS" in captured.out


def test_cli_analyze_missing_path(capsys):
    ret = main(["analyze", "non_existent_path_xyz123.py"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Target path 'non_existent_path_xyz123.py' does not exist." in captured.err


def test_cli_analyze_syntax_error(tmp_path, capsys):
    broken = tmp_path / "broken.py"
    broken.write_text("def invalid_syntax(:\n")

    ret = main(["analyze", str(broken)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Syntax Errors:" in captured.out
    assert "broken.py" in captured.out


def test_cli_analyze_json(tmp_path, capsys):
    sample = tmp_path / "sample.py"
    sample.write_text("""
class SingleHandler:
    def handle(self, req: str) -> str:
        return req
""")
    ret = main(["analyze", str(sample), "--json"])
    assert ret == 0
    data = json.loads(capsys.readouterr().out)
    assert data["files_scanned"] == 1
    assert len(data["code_smells"]) >= 1
    assert data["code_smells"][0]["smell_type"] == "SINGLE_METHOD_CLASS"


def test_cli_recommend_version_badges(capsys):
    ret = main(["recommend", "-q", "swap interchangeable algorithms at runtime"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Strategy" in captured.out
    assert "[Best Practice: Python 3.10+" in captured.out or "[Requires Python 3.10+]" in captured.out


def test_cli_search_version_badges(capsys):
    ret = main(["search", "strategy"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Strategy" in captured.out
    assert "[Best Practice: Python 3.10+" in captured.out or "[Requires Python 3.10+]" in captured.out


def test_cli_show_evolution_summary(capsys):
    ret = main(["show", "strategy"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "版本演进 (Version Evolution):" in captured.out
    assert "Classic GoF:" in captured.out
    assert "Python 3.10+:" in captured.out
    assert "Python 3.12+:" in captured.out

