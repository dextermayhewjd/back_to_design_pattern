# Design Document: AST Pattern Analyzer & Pythonic Modernization

## 1. Intent and Why
While the GoF design patterns provide foundational object-oriented abstractions, developers and AI agents frequently face two practical challenges in Python codebases:
1. **The "Writing Java in Python" Anti-Pattern**: Classic GoF patterns were conceived in 1994 for early C++ and Java before functions were first-class citizens and before language features like closures, decorators, generators, and duck typing existed. In modern Python 3.10+, dogmatically creating class hierarchies for patterns like Strategy, Command, Iterator, Singleton, and Visitor is an anti-pattern that violates Pythonic simplicity (the "Stop Writing Classes" principle).
2. **Lack of Reverse Architectural Insight**: Developers looking at legacy or foreign code often struggle to discern what patterns are already in use or where code smells (e.g., giant condition switches, single-method classes, telescoping constructors) would benefit from refactoring into cleaner Pythonic idioms or appropriate structural patterns.

This project refactors the `pat` CLI and universal agent plugin to be strictly **Pythonic-First**:
- **Default to Idiomatic Python**: `pat code <id>` defaults to modern Python 3.10+ implementations (functions as first-class citizens, generators, dataclasses, decorators, `singledispatch`). Classical verbose OOP class hierarchies are retained as `--type classic-oop` for reference.
- **Reverse AST Analyzer (`pat analyze <path>`)**: An offline, zero-dependency AST static code analyzer that detects existing patterns and flags "Java-in-Python" code smells with specific Pythonic refactoring recommendations.
- **Pythonic Agent Rules & Skills**: Updates agent rules to enforce "Pythonic First: Prefer functions, dataclasses, and generators over boilerplate OOP classes" (YAGNI/KISS).

---

## 2. Goals, Non-Goals, and Anti-Goals

### Goals
- **Pythonic-First by Default**:
  - `pat code <pattern_id>` outputs the modern, lightweight, idiomatic Python 3.10+ solution by default.
  - Classical verbose OOP implementations remain available via `--type classic-oop`.
  - `pat show <pattern_id>` highlights the Pythonic alternative prominently at the top with "When to avoid writing a class".
- **AST Pattern & Anti-Pattern Recognition (`pat analyze <path>`)**:
  - Analyze Python files or entire directories using standard library `ast`.
  - Detect common pattern signatures:
    - **Visitor**: `accept` method dispatching to `visit_*` or `@singledispatch`.
    - **Singleton**: Overridden `__new__`, metaclass instance cache, or module-level singletons.
    - **Composite**: Class holding a collection of its own base type with recursive calls.
    - **Decorator / Proxy**: Wrapper classes delegating to an internal instance or `@wraps` decorators.
    - **Observer**: Classes managing subscriber callbacks with subscribe/notify methods.
    - **Template Method**: Base class with invariant method calling abstract step methods.
    - **Strategy**: Classes or functions taking `Callable` or strategy instances.
  - Detect architectural code smells and "Java-in-Python" anti-patterns:
    - **Single-Method Classes (Java-style Strategy/Command)**: Class with only `__init__` and `run()`/`execute()` -> suggest refactoring to a plain function (`Callable`).
    - **Complex State/Type Branching**: >3 `if/elif/else` branches on status/type -> suggest `State` or dictionary dispatch.
    - **Constructor Parameter Explosion**: `__init__` with >5 parameters -> suggest `dataclass(kw_only=True)`.
    - **Manual Iterator Class**: Class with explicit `__next__` raising `StopIteration` -> suggest generator with `yield`.
    - **Hardcoded Concrete Instantiations**: Class instantiation inside business logic -> suggest `Factory Method` or dependency injection.
- **Pythonic Implementations across all 22 Patterns**:
  - Add `pythonic_code: str` and `pythonic_notes: str` to `Pattern`.
  - Specific modern Python 3.10+ mappings:
    - *Strategy*: First-class functions (`Callable`) & dictionary dispatch vs Strategy class hierarchies.
    - *Visitor*: `@functools.singledispatch` / `@singledispatchmethod` vs double dispatch.
    - *Iterator*: Generator functions (`yield` / `yield from`) vs iterator classes.
    - *Decorator*: Native `@decorator` syntax with `functools.wraps` vs wrapper classes.
    - *Builder*: `dataclasses.dataclass(kw_only=True)` vs telescoping builders.
    - *Singleton*: Module-level singletons (Python's native import cache) vs metaclasses.
    - *Command*: Closures and `functools.partial` vs Command classes.
    - *Observer*: `collections.defaultdict` event callbacks & context managers vs Subject/Observer interfaces.
    - *Template Method*: Abstract base classes with hook methods vs higher-order functions.
- **CLI Commands**:
  - `pat analyze <file_or_dir> [--json]`: Run AST pattern and smell detection.
  - `pat code <id> [--type pythonic|realworld|classic-oop]`: Defaults to `pythonic`.
  - `pat show <id>`: Displays Pythonic Idioms and "When to avoid writing classes".
- **Zero Heavy Runtime Dependencies**: Pure Python Standard Library (`ast`, `argparse`, `dataclasses`, `typing`, `sys`, `pathlib`).


### Non-Goals
- Full-blown type inference engine or linter replacement (not a replacement for mypy or ruff).
- Modifying or automatically rewriting user code (read-only diagnostic analysis).
- High-concurrency distributed patterns (DDIA / Saga / Outbox) are deferred per user decision.

### Anti-Goals
- **No False-Positive Spam**: The AST analyzer must filter out standard library patterns and only report high-confidence architectural signals.
- **No OOP Dogmatism**: Enforce that the simplest Pythonic solution (e.g. a plain function or dataclass) wins over an elaborate OOP pattern whenever possible (YAGNI/KISS).

---

## 3. Constraints
- Python 3.10+ standard library only (`ast`, `token`, `dataclasses`, `typing`).
- Analysis must work on valid Python files and skip or report syntax errors gracefully.
- Compatible with existing `bin/pat` launcher and `plugin.json` plugin distribution.

---

## 4. Architectural Specification & Directory Structure

### New & Modified Files
```text
back_to_design_pattern/
├── src/
│   └── design_patterns/
│       ├── models.py                        # Add pythonic_code, pythonic_notes to Pattern
│       ├── analyzer.py                      # AST Pattern and Code Smell Analyzer
│       ├── cli.py                           # Add analyze subcommand and --type pythonic
│       └── catalog/                         # Update all 22 pattern modules with pythonic content
│           ├── creational/
│           ├── structural/
│           └── behavioral/
├── skills/
│   └── design-patterns/
│       └── SKILL.md                         # Add reverse code analysis instructions & pythonic priority
├── rules/
│   └── AGENTS.md                            # Add Pythonic-first principle before OOP class generation
└── tests/
    ├── test_analyzer.py                     # Unit tests for AST analyzer
    ├── test_cli.py                          # CLI tests for analyze and --type pythonic
    └── test_pythonic_patterns.py            # Verification of pythonic code compilation and execution
```

### Core Components

#### 1. AST Analyzer (`src/design_patterns/analyzer.py`)
- `PatternMatch`:
  - `pattern_id: str`
  - `pattern_name: str`
  - `file_path: str`
  - `line_number: int`
  - `evidence: str`
- `CodeSmell`:
  - `smell_type: str` (e.g. `COMPLEX_BRANCHING`, `PARAMETER_EXPLOSION`)
  - `file_path: str`
  - `line_number: int`
  - `description: str`
  - `recommended_pattern: str`
  - `rationale: str`
- `AnalysisReport`:
  - `files_scanned: int`
  - `detected_patterns: list[PatternMatch]`
  - `code_smells: list[CodeSmell]`
- `CodebaseAnalyzer`:
  - `analyze_source(source: str, file_path: str = "<memory>") -> tuple[list[PatternMatch], list[CodeSmell]]`
  - `analyze_path(path: Path) -> AnalysisReport`

#### 2. Enhanced Data Model (`models.py`)
- `Pattern`:
  - `pythonic_code: str = ""`
  - `pythonic_notes: str = ""`

#### 3. CLI Command (`cli.py`)
- `pat analyze <target_path> [--json]`
- `pat code <id> --type pythonic`
- `pat show <id>` formatted with Pythonic modern idioms.

---

## 5. What's Left to the Builder
- Detailed threshold tuning for AST visitor heuristics (e.g., parameter count threshold = 5, branch count threshold = 4).
- Terminal color formatting for `pat analyze` human output.
- Comprehensive unit tests for AST edge cases (nested classes, lambdas, async functions).
