# Python Design Patterns CLI & Universal Agent Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-dependency Python CLI (`pat`) covering all 22 classic GoF design patterns from RefactoringGuru with metadata, type-hinted Python examples, diagnostic recommender, and code scaffolding, packaged as a universal agent plugin for `agy`, Claude Code, and Codex.

**Architecture:** A pure Python 3.10+ package with domain models (`models.py`), pattern registry (`registry.py`), modular pattern catalogs (creational, structural, behavioral), symptom-based diagnostic recommender (`recommender.py`), and CLI interface (`cli.py`). A zero-setup launcher (`bin/pat`), `plugin.json`, `skills/design-patterns/SKILL.md`, and `rules/AGENTS.md` make it directly installable and usable across multi-agent environments.

**Tech Stack:** Python 3.10+ (Standard Library: `argparse`, `dataclasses`, `typing`, `abc`, `json`, `sys`, `pathlib`), `pytest` for testing.

**Spec:** [`docs/superpowers/specs/2026-10-25-python-design-patterns-cli-plugin-design.md`](file:///Users/dextermayhew/projects/back_to_design_pattern/docs/superpowers/specs/2026-10-25-python-design-patterns-cli-plugin-design.md)

## Global Constraints

- Python version floor: Python 3.10+
- Pure Python standard library for runtime (zero third-party dependencies required to run `pat`).
- Standardized kebab-case identifiers for all 22 patterns (e.g. `abstract-factory`, `strategy`).
- Strict typing and `abc.ABC` in all conceptual and real-world code examples.
- Runnable without mandatory `pip install` via standalone executable `bin/pat`.
- Plugin manifest at `plugin.json`, skill at `skills/design-patterns/SKILL.md`, and rules at `rules/AGENTS.md`.

## Review Focus

1. **Unknown pattern identifier**: `pat show non-existent` or `pat code invalid-id` must exit with returncode 1 and a helpful error message listing close matches or directing to `pat list`.
2. **Empty or ambiguous recommendation query**: `pat recommend -q ""` must return a clear prompt instead of empty output or crashing.
3. **Scaffold path collision**: `pat scaffold <id> --out existing_file.py` without an overwrite flag must refuse to clobber existing files and exit cleanly.
4. **Execution sandboxing / safety**: `pat run <id>` must execute only vetted catalog examples within isolated function scopes without lingering global side effects.
5. **Standalone launcher environment**: Running `bin/pat` from any working directory (e.g. `/tmp`) without `PYTHONPATH` set must resolve its own package root and succeed.

---

### Task 1: Core Domain Models & Pattern Registry

**Files:**
- Create: `src/design_patterns/__init__.py`
- Create: `src/design_patterns/models.py`
- Create: `src/design_patterns/registry.py`
- Test: `tests/test_registry.py`

**Interfaces:**
- Produces:
  - `Category(Enum)`: `CREATIONAL = "creational"`, `STRUCTURAL = "structural"`, `BEHAVIORAL = "behavioral"`
  - `Pattern` dataclass with fields: `id: str`, `name: str`, `chinese_name: str`, `category: Category`, `intent: str`, `problem: str`, `solution: str`, `applicability: list[str]`, `symptoms: list[str]`, `pros: list[str]`, `cons: list[str]`, `relations: list[str]`, `conceptual_code: str`, `realworld_code: str`, `scaffold_template: str`
  - `PatternRegistry`: `register(pattern: Pattern) -> None`, `get(pattern_id: str) -> Pattern | None`, `list_all(category: Category | None = None) -> list[Pattern]`, `count() -> int`

- [ ] **Step 1: Write the failing tests for models and registry**

```python
# tests/test_registry.py
import pytest
from design_patterns.models import Category, Pattern
from design_patterns.registry import PatternRegistry

def test_pattern_registry_register_and_get():
    registry = PatternRegistry()
    pattern = Pattern(
        id="factory-method",
        name="Factory Method",
        chinese_name="工厂方法",
        category=Category.CREATIONAL,
        intent="Provides an interface for creating objects in a superclass.",
        problem="Tight coupling to concrete product classes.",
        solution="Replace direct constructor calls with a factory method.",
        applicability=["When you don't know exact types beforehand"],
        symptoms=["tight coupling", "new keyword proliferation"],
        pros=["Avoids tight coupling", "Single Responsibility"],
        cons=["Can lead to many subclasses"],
        relations=["Abstract Factory"],
        conceptual_code="class Creator: pass",
        realworld_code="class Logistics: pass",
        scaffold_template="# Template"
    )
    registry.register(pattern)
    assert registry.count() == 1
    assert registry.get("factory-method") == pattern
    assert registry.get("non-existent") is None
    assert len(registry.list_all(Category.CREATIONAL)) == 1
    assert len(registry.list_all(Category.STRUCTURAL)) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_registry.py -v`
Expected: FAIL (ModuleNotFoundError or Import failure)

- [ ] **Step 3: Implement `models.py` and `registry.py`**

Implement `Category` enum, `Pattern` dataclass in `src/design_patterns/models.py`, and `PatternRegistry` with dictionary store and filtering in `src/design_patterns/registry.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_registry.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ tests/
git commit -m "feat: add domain models and pattern registry"
```

---

### Task 2: Creational Patterns Catalog (5 Patterns)

**Files:**
- Create: `src/design_patterns/catalog/__init__.py`
- Create: `src/design_patterns/catalog/creational/__init__.py`
- Create: `src/design_patterns/catalog/creational/factory_method.py`
- Create: `src/design_patterns/catalog/creational/abstract_factory.py`
- Create: `src/design_patterns/catalog/creational/builder.py`
- Create: `src/design_patterns/catalog/creational/prototype.py`
- Create: `src/design_patterns/catalog/creational/singleton.py`
- Test: `tests/test_creational_patterns.py`

**Interfaces:**
- Consumes: `Category`, `Pattern` from `src/design_patterns/models.py`
- Produces: Each module exports `PATTERN: Pattern` defining all metadata, runnable `conceptual_code`, `realworld_code`, and `scaffold_template`. `catalog/creational/__init__.py` exports `CREATIONAL_PATTERNS: list[Pattern]`.

- [ ] **Step 1: Write test verifying all 5 creational patterns exist and contain valid Python code**

```python
# tests/test_creational_patterns.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_creational_patterns.py -v`
Expected: FAIL

- [ ] **Step 3: Implement the 5 creational patterns**

Author `factory_method.py`, `abstract_factory.py`, `builder.py`, `prototype.py`, and `singleton.py` with RefactoringGuru-fidelity intent, problem, solution, applicability, symptoms, and type-hinted runnable Python code. Export them in `catalog/creational/__init__.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_creational_patterns.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/design_patterns/catalog/creational tests/test_creational_patterns.py
git commit -m "feat: add 5 creational design patterns"
```

---

### Task 3: Structural Patterns Catalog (7 Patterns)

**Files:**
- Create: `src/design_patterns/catalog/structural/__init__.py`
- Create: `src/design_patterns/catalog/structural/adapter.py`
- Create: `src/design_patterns/catalog/structural/bridge.py`
- Create: `src/design_patterns/catalog/structural/composite.py`
- Create: `src/design_patterns/catalog/structural/decorator.py`
- Create: `src/design_patterns/catalog/structural/facade.py`
- Create: `src/design_patterns/catalog/structural/flyweight.py`
- Create: `src/design_patterns/catalog/structural/proxy.py`
- Test: `tests/test_structural_patterns.py`

**Interfaces:**
- Consumes: `Category`, `Pattern` from `src/design_patterns/models.py`
- Produces: `catalog/structural/__init__.py` exports `STRUCTURAL_PATTERNS: list[Pattern]`.

- [ ] **Step 1: Write test verifying all 7 structural patterns exist and contain valid Python code**

```python
# tests/test_structural_patterns.py
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
        compile(p.conceptual_code, f"{p.id}_conceptual", "exec")
        compile(p.realworld_code, f"{p.id}_realworld", "exec")
        compile(p.scaffold_template, f"{p.id}_scaffold", "exec")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_structural_patterns.py -v`
Expected: FAIL

- [ ] **Step 3: Implement the 7 structural patterns**

Author all 7 structural pattern modules and export them in `catalog/structural/__init__.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_structural_patterns.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/design_patterns/catalog/structural tests/test_structural_patterns.py
git commit -m "feat: add 7 structural design patterns"
```

---

### Task 4: Behavioral Patterns Catalog (10 Patterns) & Master Registry Loading

**Files:**
- Create: `src/design_patterns/catalog/behavioral/__init__.py`
- Create: `src/design_patterns/catalog/behavioral/chain_of_responsibility.py`
- Create: `src/design_patterns/catalog/behavioral/command.py`
- Create: `src/design_patterns/catalog/behavioral/iterator.py`
- Create: `src/design_patterns/catalog/behavioral/mediator.py`
- Create: `src/design_patterns/catalog/behavioral/memento.py`
- Create: `src/design_patterns/catalog/behavioral/observer.py`
- Create: `src/design_patterns/catalog/behavioral/state.py`
- Create: `src/design_patterns/catalog/behavioral/strategy.py`
- Create: `src/design_patterns/catalog/behavioral/template_method.py`
- Create: `src/design_patterns/catalog/behavioral/visitor.py`
- Modify: `src/design_patterns/catalog/__init__.py`
- Test: `tests/test_behavioral_patterns.py`

**Interfaces:**
- Consumes: `Category`, `Pattern` from `src/design_patterns/models.py`
- Produces: `catalog/behavioral/__init__.py` exports `BEHAVIORAL_PATTERNS: list[Pattern]`. `catalog/__init__.py` exports `ALL_PATTERNS: list[Pattern]` (total 22 patterns) and `load_default_registry() -> PatternRegistry`.

- [ ] **Step 1: Write test verifying all 10 behavioral patterns and master 22-pattern catalog**

```python
# tests/test_behavioral_patterns.py
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

def test_all_22_patterns_in_master_registry():
    registry = load_default_registry()
    assert registry.count() == 22
    assert len(registry.list_all(Category.CREATIONAL)) == 5
    assert len(registry.list_all(Category.STRUCTURAL)) == 7
    assert len(registry.list_all(Category.BEHAVIORAL)) == 10
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_behavioral_patterns.py -v`
Expected: FAIL

- [ ] **Step 3: Implement the 10 behavioral patterns and master catalog loader**

Author the 10 behavioral modules, compile checks for valid syntax, and implement `load_default_registry()` in `catalog/__init__.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_behavioral_patterns.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/design_patterns/catalog/ tests/test_behavioral_patterns.py
git commit -m "feat: add 10 behavioral patterns and complete 22-pattern registry"
```

---

### Task 5: Recommender Engine & Diagnostic Wizard

**Files:**
- Create: `src/design_patterns/recommender.py`
- Test: `tests/test_recommender.py`

**Interfaces:**
- Consumes: `Pattern`, `Category` from `models.py`, `PatternRegistry` from `registry.py`
- Produces:
  - `RecommendationResult`: `pattern: Pattern`, `score: float`, `matched_symptoms: list[str]`, `rationale: str`
  - `PatternRecommender`:
    - `recommend(query: str, top_k: int = 3) -> list[RecommendationResult]`
    - `run_interactive_wizard(input_fn=input, print_fn=print) -> list[RecommendationResult]`

- [ ] **Step 1: Write tests for recommendation scoring and interactive stepper**

```python
# tests/test_recommender.py
from design_patterns.catalog import load_default_registry
from design_patterns.recommender import PatternRecommender

def test_recommend_by_symptoms_and_keywords():
    registry = load_default_registry()
    recommender = PatternRecommender(registry)
    
    results = recommender.recommend("I need to swap interchangeable algorithms at runtime")
    assert len(results) > 0
    assert results[0].pattern.id == "strategy"
    assert "algorithms" in results[0].matched_symptoms or "runtime" in results[0].matched_symptoms

    undo_results = recommender.recommend("need undo and redo history rollback")
    top_ids = [r.pattern.id for r in undo_results]
    assert "memento" in top_ids or "command" in top_ids

def test_recommend_empty_query():
    registry = load_default_registry()
    recommender = PatternRecommender(registry)
    results = recommender.recommend("")
    assert results == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_recommender.py -v`
Expected: FAIL

- [ ] **Step 3: Implement `recommender.py`**

Implement `PatternRecommender` with weighted matching across symptoms, problem keywords, and intent. Implement `run_interactive_wizard` asking 3 structured diagnostic questions.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_recommender.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/design_patterns/recommender.py tests/test_recommender.py
git commit -m "feat: implement diagnostic recommender engine and wizard"
```

---

### Task 6: CLI Engine & Zero-Setup Launcher

**Files:**
- Create: `src/design_patterns/cli.py`
- Create: `src/design_patterns/__main__.py`
- Create: `bin/pat`
- Create: `pyproject.toml`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `load_default_registry`, `PatternRecommender`, `cli`
- Produces: CLI commands `list`, `show`, `code`, `recommend`, `scaffold`, `run`. `bin/pat` executable launcher with `chmod +x`.

- [ ] **Step 1: Write CLI unit tests**

```python
# tests/test_cli.py
import json
import pytest
from design_patterns.cli import main

def test_cli_list(capsys):
    ret = main(["list", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 22

def test_cli_show(capsys):
    ret = main(["show", "singleton", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["id"] == "singleton"

def test_cli_code(capsys):
    ret = main(["code", "singleton", "--type", "conceptual"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "class Singleton" in captured.out

def test_cli_unknown_pattern(capsys):
    ret = main(["show", "non-existent-pattern"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Pattern 'non-existent-pattern' not found" in captured.err

def test_cli_scaffold_no_overwrite(tmp_path):
    target = tmp_path / "factory.py"
    target.write_text("existing code")
    ret = main(["scaffold", "factory-method", "--out", str(target)])
    assert ret == 1
    assert target.read_text() == "existing code"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL

- [ ] **Step 3: Implement `cli.py`, `__main__.py`, `bin/pat`, and `pyproject.toml`**

- Author `cli.py` with `argparse`, formatted output, JSON export, and command handlers.
- Author `__main__.py` calling `cli.main()`.
- Author `bin/pat` with `#!/usr/bin/env python3` and dynamic root `sys.path` injection. Make it executable (`chmod +x bin/pat`).
- Author `pyproject.toml` declaring `pat = "design_patterns.cli:main"`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/design_patterns/cli.py src/design_patterns/__main__.py bin/pat pyproject.toml tests/test_cli.py
git commit -m "feat: implement CLI engine and zero-setup launcher"
```

---

### Task 7: Universal Plugin Manifest, Skill & Agent Rules

**Files:**
- Create: `plugin.json`
- Create: `rules/AGENTS.md`
- Create: `skills/design-patterns/SKILL.md`
- Create: `README.md`
- Test: `tests/test_plugin_metadata.py`

**Interfaces:**
- Produces: Complete Antigravity / Claude Code / Codex plugin specification.

- [ ] **Step 1: Write test verifying plugin manifest, skill syntax, and rules file**

```python
# tests/test_plugin_metadata.py
import json
from pathlib import Path

def test_plugin_json_valid():
    manifest_path = Path("plugin.json")
    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text())
    assert data["name"] == "design-patterns"
    assert "description" in data

def test_skill_md_valid():
    skill_path = Path("skills/design-patterns/SKILL.md")
    assert skill_path.exists()
    content = skill_path.read_text()
    assert content.startswith("---")
    assert "name: design-patterns" in content

def test_rules_agents_md_valid():
    rule_path = Path("rules/AGENTS.md")
    assert rule_path.exists()
    content = rule_path.read_text()
    assert "Design Patterns" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_plugin_metadata.py -v`
Expected: FAIL

- [ ] **Step 3: Implement `plugin.json`, `skills/design-patterns/SKILL.md`, `rules/AGENTS.md`, and `README.md`**

- Write `plugin.json` compliant with Antigravity plugin loader.
- Write `skills/design-patterns/SKILL.md` describing how agents can diagnose and scaffold patterns with `bin/pat` or `pat`.
- Write `rules/AGENTS.md` outlining architectural guidelines, SOLID principles, and anti-over-engineering instructions (YAGNI/KISS).
- Write `README.md` detailing CLI commands, installation, and agent integration.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_plugin_metadata.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugin.json rules/ skills/ README.md tests/test_plugin_metadata.py
git commit -m "feat: add universal plugin manifest, skill, and architectural rules"
```

---

### Task 8: End-to-End Execution Verification & Test Suite

**Files:**
- Create: `tests/test_patterns_execution.py`
- Test: Full test suite (`pytest -v`)

**Interfaces:**
- Validates: That all 22 pattern examples run successfully when invoked via `pat run <id>` or imported directly, producing expected outputs without runtime exceptions.

- [ ] **Step 1: Write end-to-end execution test for all 22 patterns**

```python
# tests/test_patterns_execution.py
from design_patterns.catalog import ALL_PATTERNS
from design_patterns.cli import main

def test_all_patterns_run_without_exception(capsys):
    for pattern in ALL_PATTERNS:
        ret = main(["run", pattern.id, "--type", "conceptual"])
        assert ret == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0
```

- [ ] **Step 2: Run test to verify all tests pass**

Run: `pytest -v`
Expected: All tests pass across the entire suite.

- [ ] **Step 3: Verify standalone launcher execution directly in shell**

Run: `./bin/pat list` and `./bin/pat recommend -q "swap algorithm at runtime"`
Expected: Clean terminal output with returncode 0.

- [ ] **Step 4: Commit**

```bash
git add tests/test_patterns_execution.py
git commit -m "test: add end-to-end execution verification for all 22 patterns"
```
