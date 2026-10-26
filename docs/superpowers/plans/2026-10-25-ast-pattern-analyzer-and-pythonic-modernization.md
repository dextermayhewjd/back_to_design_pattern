# AST Pattern Analyzer & Pythonic Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the CLI and plugin to be strictly "Pythonic-First" by adding an AST static pattern/smell analyzer (`pat analyze`) and equipping all 22 GoF patterns with modern Python 3.10+ idioms (functions, dataclasses, generators, decorators, singledispatch) as the default output.

**Architecture:** Extend `Pattern` with `pythonic_code` and `pythonic_notes`. Author a zero-dependency `ast.NodeVisitor` engine (`src/design_patterns/analyzer.py`) detecting design patterns and "Java-in-Python" code smells (e.g., single-method classes, parameter explosion, manual iterators). Update `cli.py` to default `code` to `pythonic` and provide `analyze <path>`, with updated agent rules and skills.

**Tech Stack:** Python 3.10+ (Standard Library: `ast`, `argparse`, `dataclasses`, `typing`, `sys`, `pathlib`), `pytest` for testing.

**Spec:** [`docs/superpowers/specs/2026-10-25-ast-pattern-analyzer-and-pythonic-modernization-design.md`](file:///Users/dextermayhew/projects/back_to_design_pattern/docs/superpowers/specs/2026-10-25-ast-pattern-analyzer-and-pythonic-modernization-design.md)

## Global Constraints
- Python version floor: Python 3.10+
- Pure Python standard library for runtime (zero external dependencies).
- Standalone execution via `./bin/pat` with zero setup.
- `pat code <id>` must default to `pythonic`.
- `pat analyze` must handle non-existent paths, syntax errors, and empty files gracefully with exit code 1 or clear messages.

## Review Focus
1. **Invalid/Malformed Python Files in `analyze`**: `pat analyze <broken_syntax.py>` must report syntax errors gracefully without unhandled tracebacks.
2. **Directory traversal in `analyze`**: `pat analyze <dir>` must recursively scan only `.py` files, ignoring hidden directories like `.git` and `.venv`.
3. **Pythonic code execution**: All 22 `pythonic_code` snippets must parse and run cleanly via `compile()` and `exec()`.
4. **Backward compatibility**: `--type conceptual` and `--type classic-oop` must remain supported in `pat code` and `pat run`.
5. **False positive suppression**: Standard single-method classes or functions without smells must not trigger false positive warnings.

---

### Task 1: Model & Catalog Expansion with Python Version Evolution Matrix across all 22 Patterns

**Files:**
- Modify: `src/design_patterns/models.py`
- Modify: `src/design_patterns/catalog/creational/*.py` (5 files)
- Modify: `src/design_patterns/catalog/structural/*.py` (7 files)
- Modify: `src/design_patterns/catalog/behavioral/*.py` (10 files)
- Create: `tests/test_pythonic_patterns.py`

**Interfaces:**
- Produces:
  - `VersionEvolution(version_tag: str, summary: str, key_features: list[str], code: str, line_count: int)`
  - `Pattern` updated with:
    - `classic_code: str`
    - `python310_code: str`
    - `python312_code: str`
    - `matrix_notes: dict[str, str]`
    - Dynamic alias properties for backward compatibility: `conceptual_code` -> `classic_code`, `realworld_code` -> `python310_code`, `pythonic_code` -> `python312_code or python310_code`, `pythonic_notes` -> `matrix_notes.get("3.10", "")`
    - `get_evolution(version: str) -> VersionEvolution`
  - All 22 patterns in catalog populated with:
    - `classic_code`: Classic GoF OOP hierarchy (abstract base class, inheritance)
    - `python310_code`: Modern Python 3.10+ idiom (match-case, dataclass, generators, Callable)
    - `python312_code`: NextGen Python 3.12+ idiom (PEP 695 type parameters `[T]`, `typing.Self`, `@override`)
    - `matrix_notes`: Rationale and language features mapped by tier ("classic", "3.10", "3.12")

- [ ] **Step 1: Write failing tests verifying all 22 patterns have valid 3-tier evolution matrix**

```python
# tests/test_pythonic_patterns.py
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
        
        # Test backward compat properties
        assert p.conceptual_code == p.classic_code
        assert p.realworld_code == p.python310_code
        assert p.pythonic_code in (p.python312_code, p.python310_code)
        
        evo_classic = p.get_evolution("classic")
        assert isinstance(evo_classic, VersionEvolution)
        assert evo_classic.version_tag == "classic"
        
        evo_310 = p.get_evolution("3.10")
        assert evo_310.version_tag == "3.10+"
        
        evo_312 = p.get_evolution("3.12")
        assert evo_312.version_tag == "3.12+"
        
        # Compile classic and 3.10 code
        compile(p.classic_code, f"{p.id}_classic", "exec")
        compile(p.python310_code, f"{p.id}_python310", "exec")

@pytest.mark.skipif(sys.version_info < (3, 12), reason="Requires Python 3.12+ to compile PEP 695 syntax")
def test_all_patterns_312_code_compiles():
    for p in ALL_PATTERNS:
        compile(p.python312_code, f"{p.id}_python312", "exec")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_pythonic_patterns.py -v`
Expected: FAIL (AttributeError or missing fields)

- [ ] **Step 3: Update `models.py` and populate 3-tier evolution matrix for all 22 patterns**

Implement `VersionEvolution` and extend `Pattern` in `src/design_patterns/models.py`. Update catalog files across `creational/`, `structural/`, and `behavioral/` with `classic_code`, `python310_code`, `python312_code`, and `matrix_notes`.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_pythonic_patterns.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/design_patterns/models.py src/design_patterns/catalog/ tests/test_pythonic_patterns.py
git commit -m "feat: add 3-tier Python version evolution matrix across all 22 patterns"
```

---

### Task 2: AST Pattern & Code Smell Analyzer Engine

**Files:**
- Create: `src/design_patterns/analyzer.py`
- Create: `tests/test_analyzer.py`

**Interfaces:**
- Produces:
  - `PatternMatch(pattern_id: str, pattern_name: str, category: str, file_path: str, line_number: int, evidence: str, confidence: str = "high")`
  - `CodeSmell(smell_type: str, file_path: str, line_number: int, description: str, recommended_pattern: str, target_version_baseline: str, refactoring_tip: str)`
  - `AnalysisReport(files_scanned: int, total_lines: int, detected_patterns: list[PatternMatch], code_smells: list[CodeSmell], syntax_errors: list[str])` with `to_dict() -> dict`
  - `CodebaseAnalyzer`:
    - `analyze_source(source: str, file_path: str = "<memory>") -> tuple[list[PatternMatch], list[CodeSmell]]`
    - `analyze_path(path: Path) -> AnalysisReport`

- [ ] **Step 1: Write failing tests for AST pattern recognition and code smells**

```python
# tests/test_analyzer.py
from pathlib import Path
from design_patterns.analyzer import CodebaseAnalyzer, AnalysisReport

def test_detect_single_method_class_smell():
    source = """
class ShippingCostCalculator:
    def __init__(self, rate: float):
        self.rate = rate
    def execute(self, weight: float) -> float:
        return self.rate * weight
"""
    analyzer = CodebaseAnalyzer()
    patterns, smells = analyzer.analyze_source(source)
    assert any(s.smell_type == "SINGLE_METHOD_CLASS" for s in smells)
    assert any(s.recommended_pattern == "strategy" for s in smells)
    assert any("Python 3.10+" in s.target_version_baseline for s in smells)

def test_detect_visitor_pattern():
    source = """
class Node:
    def accept(self, visitor):
        return visitor.visit_node(self)
"""
    analyzer = CodebaseAnalyzer()
    patterns, smells = analyzer.analyze_source(source)
    assert any(p.pattern_id == "visitor" for p in patterns)

def test_detect_parameter_explosion_smell():
    source = """
class ServerConfig:
    def __init__(self, host, port, timeout, max_conns, retries, ssl, cert):
        pass
"""
    analyzer = CodebaseAnalyzer()
    patterns, smells = analyzer.analyze_source(source)
    assert any(s.smell_type == "PARAMETER_EXPLOSION" for s in smells)
    assert any(s.recommended_pattern in ("builder", "dataclass") for s in smells)
    assert any("Python 3.10+" in s.target_version_baseline for s in smells)

def test_analyze_syntax_error_handling(tmp_path):
    broken_file = tmp_path / "broken.py"
    broken_file.write_text("def broken_syntax(:")
    analyzer = CodebaseAnalyzer()
    report = analyzer.analyze_path(tmp_path)
    assert len(report.syntax_errors) == 1
    assert "broken.py" in report.syntax_errors[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_analyzer.py -v`
Expected: FAIL

- [ ] **Step 3: Implement `src/design_patterns/analyzer.py`**

Implement `CodebaseAnalyzer` using `ast.NodeVisitor` detecting Visitor, Singleton, Composite, Decorator/Proxy, Observer, Template Method, and Strategy, as well as smells: Single-Method Class ("Java in Python"), Parameter Explosion (>5 args), and Complex Branching (>3 if-branches). Include version-stamped recommendations (`target_version_baseline` and `refactoring_tip`) on every smell.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_analyzer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/design_patterns/analyzer.py tests/test_analyzer.py
git commit -m "feat: implement AST pattern and code smell analyzer engine"
```

---

### Task 3: CLI Subcommand `analyze`, `matrix`, and Pythonic-First Refactor in `cli.py`

**Files:**
- Modify: `src/design_patterns/cli.py`
- Modify: `tests/test_cli.py`
- Create: `tests/test_matrix.py`

**Interfaces:**
- Produces:
  - `pat matrix <pattern_id> [--json]`: Renders 3-tier version evolution comparison table.
  - `pat code <id> [--py classic|3.10|3.12] [--type ...]` (default: local runtime auto-detected, 3.12 on >=3.12, 3.10 on >=3.10).
  - `pat run <id> [--py classic|3.10|3.12]` with graceful version error if running 3.12 on <3.12 interpreter.
  - `pat analyze <target_path> [--json]`
  - `pat recommend` with explicit version baseline badges.

- [ ] **Step 1: Write CLI tests for `analyze`, `matrix`, and version auto-detection**

```python
# In tests/test_matrix.py and tests/test_cli.py
def test_cli_matrix_command(capsys):
    ret = main(["matrix", "strategy"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "classic" in captured.out
    assert "3.10+" in captured.out
    assert "3.12+" in captured.out

def test_cli_analyze_file(tmp_path, capsys):
    sample = tmp_path / "sample.py"
    sample.write_text("""
class TaxCalculator:
    def execute(self, amount):
        return amount * 0.1
""")
    ret = main(["analyze", str(sample)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "TaxCalculator" in captured.out
    assert "strategy" in captured.out.lower()
    assert "Python 3.10+" in captured.out

def test_cli_code_defaults_to_pythonic(capsys):
    ret = main(["code", "strategy"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Callable" in captured.out or "def " in captured.out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_matrix.py tests/test_cli.py -k "test_cli_matrix or test_cli_analyze" -v`
Expected: FAIL

- [ ] **Step 3: Update `cli.py` to add `matrix`, `analyze`, and version resolution**

Add `matrix` and `analyze` subcommands. Add auto-detection logic for `--py` resolving between `classic`, `3.10`, and `3.12`. Support backward compatibility for `--type`. Format `recommend` suggestions with `[Requires Python X.Y+]` badges.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_matrix.py tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/design_patterns/cli.py tests/test_cli.py tests/test_matrix.py
git commit -m "feat: add pat matrix, pat analyze, and version-stamped recommendations"
```

- [ ] **Step 5: Commit**

```bash
git add src/design_patterns/cli.py tests/test_cli.py
git commit -m "feat: add pat analyze subcommand and default code to pythonic"
```

---

### Task 4: Universal Plugin Manifest, Rules & Skill Modernization

**Files:**
- Modify: `rules/AGENTS.md`
- Modify: `skills/design-patterns/SKILL.md`
- Modify: `README.md`
- Modify: `tests/test_plugin_metadata.py`

**Interfaces:**
- Produces: Guidelines instructing AI agents to prioritize Pythonic idioms over classic class boilerplate and how to use `pat analyze` to inspect legacy code.

- [ ] **Step 1: Write test verifying updated skill and rules contain Pythonic-First guidance**

```python
# In tests/test_plugin_metadata.py
def test_rules_contains_pythonic_first_principle():
    rule_path = Path("rules/AGENTS.md")
    content = rule_path.read_text()
    assert "Pythonic-First" in content or "Stop Writing Classes" in content

def test_skill_contains_analyze_command():
    skill_path = Path("skills/design-patterns/SKILL.md")
    content = skill_path.read_text()
    assert "pat analyze" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_plugin_metadata.py -v`
Expected: FAIL

- [ ] **Step 3: Update `rules/AGENTS.md`, `skills/design-patterns/SKILL.md`, and `README.md`**

Incorporate the "Stop Writing Classes / Pythonic-First" philosophy, document `pat analyze`, and update command cheatsheets.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_plugin_metadata.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rules/AGENTS.md skills/design-patterns/SKILL.md README.md tests/test_plugin_metadata.py
git commit -m "docs: modernize agent rules and skill with pythonic-first guidelines"
```

---

### Task 5: End-to-End Regression Verification & Test Suite

**Files:**
- Modify: `tests/test_patterns_execution.py`
- Test: Full test suite (`pytest -v`)

**Interfaces:**
- Validates: That all 22 `pythonic_code` snippets execute cleanly without exception via `pat run <id> --type pythonic` or test runners.

- [ ] **Step 1: Write execution test for all 22 pythonic implementations**

```python
# In tests/test_patterns_execution.py
from design_patterns.catalog import ALL_PATTERNS
from design_patterns.cli import main

def test_all_patterns_pythonic_run_without_exception(capsys):
    for pattern in ALL_PATTERNS:
        ret = main(["run", pattern.id, "--type", "pythonic"])
        assert ret == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0
```

- [ ] **Step 2: Run full test suite to verify 100% pass**

Run: `.venv/bin/pytest -v`
Expected: All tests pass.

- [ ] **Step 3: Verify `./bin/pat analyze` on the codebase itself**

Run: `./bin/pat analyze src/`
Expected: Clean analysis report showing scanned files and detected patterns with return code 0.

- [ ] **Step 4: Commit**

```bash
git add tests/test_patterns_execution.py
git commit -m "test: add execution verification for all 22 modern pythonic pattern implementations"
```
