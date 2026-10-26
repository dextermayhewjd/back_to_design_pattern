# Design Document: AST Pattern Analyzer & Pythonic Modernization

## 1. Intent and Why
While the GoF design patterns provide foundational object-oriented abstractions, developers and AI agents frequently face two practical challenges:
1. **Lack of Reverse Architectural Insight**: Developers looking at legacy or foreign code often struggle to discern what patterns are already in use or where code smells (e.g., giant condition switches, telescoping constructors) would benefit from refactoring into specific patterns.
2. **Java-Style Over-Engineering in Python**: Classic GoF patterns originated in early C++/Java and rely heavily on rigid class hierarchies. In modern Python 3.10+, language features such as first-class functions, closures, `functools.singledispatch`, generators (`yield`), dataclasses, and decorators provide vastly simpler, more idiomatic solutions. Agents without explicit guidance tend to write verbose, boilerplated OOP classes rather than idiomatic Python.

This project enhances the `pat` CLI and agent plugin with:
- An offline, zero-dependency AST static code analyzer (`pat analyze <path>`) that detects existing design patterns and flags code smells with pattern recommendations.
- A comprehensive modernization of all 22 GoF patterns with **Pythonic Idioms** (`--type pythonic` and modern contrast notes).
- Updated agent rules and skills empowering agents to reverse-analyze code and favor Pythonic idioms over heavy class boilerplate.

---

## 2. Goals, Non-Goals, and Anti-Goals

### Goals
- **AST Pattern Recognition (`pat analyze <path>`)**:
  - Analyze Python files or entire directories using standard library `ast`.
  - Detect common pattern signatures:
    - **Visitor**: `accept` method dispatching to `visit_*` or `singledispatch`.
    - **Singleton**: Overridden `__new__` or metaclass instance dictionary check.
    - **Composite**: Class holding a collection of its own base type with recursive calls.
    - **Decorator / Proxy**: Wrapper classes delegating to an internal instance.
    - **Observer**: Classes managing subscriber lists with subscribe/notify methods.
    - **Template Method**: Base class with invariant method calling abstract step methods.
    - **Strategy**: Classes taking `Callable` or strategy instances for algorithmic execution.
  - Detect architectural code smells:
    - **Complex State/Type Branching**: >3 `if/elif/else` branches on status/type -> suggest `State` or `Strategy`.
    - **Constructor Parameter Explosion**: `__init__` with >5 parameters -> suggest `Builder` or `dataclass`.
    - **Hardcoded Concrete Instantiations**: Class instantiation inside business logic -> suggest `Factory Method`.
- **Pythonic Idioms for all 22 Patterns**:
  - Add `pythonic_code: str` and `pythonic_notes: str` to `Pattern`.
  - Showcase modern Python 3.10+ alternatives for each pattern:
    - *Strategy*: First-class functions (`Callable`) vs Strategy class hierarchies.
    - *Visitor*: `functools.singledispatch` / `singledispatchmethod` vs double dispatch.
    - *Iterator*: Generator functions (`yield` / `yield from`) vs iterator classes.
    - *Decorator*: Native `@decorator` syntax with `functools.wraps`.
    - *Builder*: `dataclasses.dataclass(kw_only=True)` vs telescoping builders.
    - *Singleton*: Module-level singletons (Python's native import cache) vs metaclasses.
    - *Command*: Closures and `functools.partial` vs Command objects.
    - *Observer*: `collections.defaultdict` event callbacks vs Subject/Observer interfaces.
- **CLI Enhancements**:
  - `pat analyze <file_or_dir> [--json]`: Run AST pattern and smell detection.
  - `pat code <id> --type [conceptual|realworld|pythonic]`: Display modern Pythonic code.
  - `pat show <id>`: Include `## Pythonic 现代惯用法 (Modern Pythonic Idiom)`.
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
