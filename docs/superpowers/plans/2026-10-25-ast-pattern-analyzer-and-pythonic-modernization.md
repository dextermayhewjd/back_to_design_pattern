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

### Task 1: Model & Catalog Expansion with Pythonic Idioms across all 22 Patterns

**Files:**
- Modify: `src/design_patterns/models.py`
- Modify: `src/design_patterns/catalog/creational/*.py` (5 files)
- Modify: `src/design_patterns/catalog/structural/*.py` (7 files)
- Modify: `src/design_patterns/catalog/behavioral/*.py` (10 files)
- Create: `tests/test_pythonic_patterns.py`

**Interfaces:**
- Produces: `Pattern.pythonic_code: str`, `Pattern.pythonic_notes: str` populated across all 22 patterns.

- [ ] **Step 1: Write failing tests verifying all 22 patterns have valid pythonic code and notes**

```python
# tests/test_pythonic_patterns.py
from design_patterns.catalog import ALL_PATTERNS

def test_all_patterns_have_pythonic_content():
    assert len(ALL_PATTERNS) == 22
    for p in ALL_PATTERNS:
        assert len(p.pythonic_code.strip()) > 0, f"{p.id} missing pythonic_code"
        assert len(p.pythonic_notes.strip()) > 0, f"{p.id} missing pythonic_notes"
        # Compile pythonic code
        compile(p.pythonic_code, f"{p.id}_pythonic", "exec")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_pythonic_patterns.py -v`
Expected: FAIL (AttributeError or missing content)

- [ ] **Step 3: Update `models.py` and author pythonic code/notes for all 22 patterns**

Add `pythonic_code: str = ""` and `pythonic_notes: str = ""` in `models.py`. In each catalog module, author modern Python 3.10+ implementations (e.g. `functools.singledispatch` for Visitor, `Callable` for Strategy, generators for Iterator, dataclasses for Builder, closures for Command, `@wraps` for Decorator).

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_pythonic_patterns.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/design_patterns/ models.py catalog/ tests/test_pythonic_patterns.py
git commit -m "feat: add modern pythonic implementations for all 22 patterns"
```

---

### Task 2: AST Pattern & Code Smell Analyzer Engine

**Files:**
- Create: `src/design_patterns/analyzer.py`
- Create: `tests/test_analyzer.py`

**Interfaces:**
- Produces:
  - `PatternMatch(pattern_id: str, pattern_name: str, file_path: str, line_number: int, evidence: str)`
  - `CodeSmell(smell_type: str, file_path: str, line_number: int, description: str, recommended_pattern: str, rationale: str)`
  - `AnalysisReport(files_scanned: int, detected_patterns: list[PatternMatch], code_smells: list[CodeSmell])`
  - `CodebaseAnalyzer`:
    - `analyze_source(source: str, file_path: str = "<memory>") -> tuple[list[PatternMatch], list[CodeSmell]]`
    - `analyze_path(path: Path) -> AnalysisReport`

- [ ] **Step 1: Write failing tests for AST pattern recognition and code smells**

```python
# tests/test_analyzer.py
from pathlib import Path
from design_patterns.analyzer import CodebaseAnalyzer

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_analyzer.py -v`
Expected: FAIL

- [ ] **Step 3: Implement `src/design_patterns/analyzer.py`**

Implement `CodebaseAnalyzer` using `ast.NodeVisitor` detecting Visitor, Singleton, Composite, Decorator/Proxy, Observer, Template Method, and Strategy, as well as smells: Single-Method Class ("Java in Python"), Parameter Explosion (>5 args), and Complex Branching (>3 if-branches).

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_analyzer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/design_patterns/analyzer.py tests/test_analyzer.py
git commit -m "feat: implement AST pattern and code smell analyzer engine"
```

---

### Task 3: CLI Subcommand `analyze` & Pythonic-First Refactor in `cli.py`

**Files:**
- Modify: `src/design_patterns/cli.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Produces:
  - `pat analyze <target_path> [--json]`
  - `pat code <id> [--type pythonic|realworld|classic-oop]` (default: `pythonic`)
  - `pat show <id>` includes `## Pythonic 现代惯用法` section.

- [ ] **Step 1: Write CLI tests for `analyze` and pythonic defaults**

```python
# In tests/test_cli.py
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
    assert "Strategy" in captured.out

def test_cli_code_defaults_to_pythonic(capsys):
    ret = main(["code", "strategy"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Callable" in captured.out or "def " in captured.out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_cli.py -k "test_cli_analyze_file or test_cli_code_defaults_to_pythonic" -v`
Expected: FAIL

- [ ] **Step 3: Update `cli.py` to add `analyze` and make `pythonic` default**

Add `analyze` subcommand parsing files/directories with `CodebaseAnalyzer`. Update `code` argument default to `pythonic`. In `show`, display `pattern.pythonic_notes`.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_cli.py -v`
Expected: PASS

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
