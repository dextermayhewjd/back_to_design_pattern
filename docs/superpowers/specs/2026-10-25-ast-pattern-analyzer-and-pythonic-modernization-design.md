# Design Document: AST Pattern Analyzer & Python Version Evolution Matrix

## 1. Intent and Why
Design patterns in Python cannot be treated as a static, language-agnostic dogma. Classic GoF patterns were conceived in 1994 for early C++ and Java before first-class functions, generators, closures, decorators, and pattern matching existed. Blindly writing Java-style class hierarchies in Python is an anti-pattern ("Writing Java in Python").

Furthermore, Python itself has evolved dramatically across versions:
- **Python 3.10** introduced Structural Pattern Matching (`match-case`), `dataclass(kw_only=True)`, and union types (`X | Y`), which fundamentally redefined patterns like Visitor, State, and Builder.
- **Python 3.11** introduced `typing.Self` for fluent APIs, prototype cloning, and method chaining.
- **Python 3.12** introduced PEP 695 generic syntax (`class Container[T]:`, `type Func[T] = ...`) and `@override`.

This project delivers a **Version-Aware Design Pattern CLI & Agent Plugin**:
1. **Python Version Evolution Matrix**: Every pattern is implemented across three key technical paradigms:
   - `classic`: Classical GoF OOP class hierarchies (for legacy codebases and cross-language conceptual reference).
   - `3.10`: Modern standard baseline (`match-case`, first-class functions, `kw_only` dataclasses, generators).
   - `3.12`: NextGen enhanced paradigm (`typing.Self`, PEP 695 type parameters `[T]`, `@override`).
2. **Explicit Version-Tagged Recommendations**: Every recommendation and refactoring suggestion explicitly declares its target Python baseline (e.g., `[Based on Python 3.10+: match-case]` or `[Based on Python 3.12+: PEP 695 generic parameters]`).
3. **Environment Auto-Detection & CLI Matrix Command**: `pat code` automatically detects the local Python runtime version, while `pat matrix <pattern>` visually compares the evolution of code size, complexity, and language features across versions.
4. **AST Reverse Analyzer (`pat analyze <path>`)**: Statically inspects existing codebases to identify implemented patterns and flag "Java-in-Python" anti-patterns, recommending version-appropriate refactorings.

---

## 2. Goals, Non-Goals, and Anti-Goals

### Goals
- **Three-Tier Version Matrix for all 22 Patterns**:
  - `classic`: Full OOP class hierarchies using `abc.ABC` and explicit inheritance.
  - `3.10`: Modern Python 3.10+ idiomatic code (functions as first-class citizens, `match-case`, generators, `@decorator`, `dataclass(kw_only=True)`).
  - `3.12`: NextGen Python 3.12+ code (`typing.Self`, `class Factory[T]:`, `type Algorithm[T] = Callable[[T], T]`, `@override`).
  - `matrix_notes`: Rationale explaining which Python features enabled each reduction in boilerplate.
- **Explicit Version Stamping in Output**:
  - Every recommendation from `pat recommend` and `pat analyze` must explicitly tag the version requirement (e.g. `[Requires Python >=3.10: Structural Pattern Matching]`).
- **CLI Commands**:
  - `pat code <id> [--py classic|3.10|3.12]`: Defaults to auto-detected local Python runtime (e.g. 3.12 on Python 3.12, 3.10 on Python 3.10).
  - `pat matrix <id> [--json]`: Side-by-side evolution comparison showing code and metrics across paradigms.
  - `pat analyze <path> [--py <target_version>] [--json]`: Scans code with AST, detects patterns, and produces version-aware refactoring advice.
  - `pat recommend [-q <query> | -i]`: Version-tagged pattern recommendations.
- **AST Pattern & Anti-Pattern Recognition (`analyzer.py`)**:
  - Identifies existing patterns (Visitor, Singleton, Strategy, Composite, Decorator/Proxy, Observer, Template Method).
  - Identifies code smells: Single-Method Classes ("Java in Python"), Giant Condition Switches (>3 branches), Parameter Explosion (>5 args), Manual `__next__` Iterators.
- **Zero Heavy Runtime Dependencies**: Pure Python Standard Library (`ast`, `argparse`, `dataclasses`, `typing`, `sys`, `pathlib`).

### Non-Goals
- Full type checker or AST rewriting tool (read-only diagnostic and generation).
- Supporting dead Python versions (<3.8).

### Anti-Goals
- No unversioned advice: Never recommend modern syntax (e.g. `match-case` or `[T]`) without stating the version prerequisite.
- No false positives: AST analyzer must avoid flagging legitimate single-function interfaces or small dataclasses.

---

## 3. Constraints
- Runtime compatibility: Python 3.10 or higher.
- Pure Python standard library for CLI execution.
- Backward compatibility with existing `pat list`, `pat show`, `pat scaffold`, `pat run`.

---

## 4. Architectural Specification & Directory Structure

### New & Modified Files
```text
back_to_design_pattern/
├── src/
│   └── design_patterns/
│       ├── models.py                        # Pattern with classic_code, python310_code, python312_code, matrix_notes
│       ├── analyzer.py                      # AST Pattern and Code Smell Analyzer (Version-Aware)
│       ├── cli.py                           # Commands: analyze, matrix, code --py, version auto-detection
│       └── catalog/                         # 22 Pattern Modules updated with 3-tier matrix implementations
│           ├── creational/
│           ├── structural/
│           └── behavioral/
├── skills/
│   └── design-patterns/
│       └── SKILL.md                         # Updated with Version Matrix & reverse analysis workflows
├── rules/
│   └── AGENTS.md                            # Rules enforcing version-aware Pythonic recommendations
└── tests/
    ├── test_analyzer.py                     # AST analyzer tests
    ├── test_matrix.py                       # Matrix output and version filtering tests
    ├── test_cli.py                          # CLI tests for analyze, matrix, and code --py
    └── test_pythonic_patterns.py            # Verification of all 3-tier code samples compilation
```

### Core Components

#### 1. Enhanced Data Model (`models.py`)
```python
@dataclass
class VersionEvolution:
    version_tag: str             # "classic" | "3.10+" | "3.12+"
    summary: str                 # 1-line summary of how the pattern is implemented in this tier
    key_features: list[str]      # Language features used (e.g. ["match-case", "dataclass(kw_only=True)"])
    code: str                    # Complete runnable Python code for this tier
    line_count: int              # Line count metric

@dataclass
class Pattern:
    id: str
    name: str
    chinese_name: str
    category: Category
    intent: str
    problem: str
    solution: str
    applicability: list[str]
    symptoms: list[str]
    pros: list[str]
    cons: list[str]
    relations: list[str]
    # 3-Tier Evolution Matrix
    classic_code: str
    python310_code: str
    python312_code: str
    matrix_notes: dict[str, str] # version -> explanation of language features
    scaffold_template: str
    
    # Backward compatibility properties
    @property
    def conceptual_code(self) -> str:
        return self.classic_code

    @property
    def realworld_code(self) -> str:
        return self.python310_code

    @property
    def pythonic_code(self) -> str:
        return self.python312_code or self.python310_code

    def get_evolution(self, version: str) -> VersionEvolution:
        ...
```

#### 2. AST Analyzer Data Contracts (`analyzer.py`)
```python
@dataclass
class PatternMatch:
    pattern_id: str
    pattern_name: str
    category: str
    file_path: str
    line_number: int
    evidence: str
    confidence: str = "high"     # "high" | "medium"

@dataclass
class CodeSmell:
    smell_type: str              # e.g. "SINGLE_METHOD_CLASS", "COMPLEX_BRANCHING"
    file_path: str
    line_number: int
    description: str
    recommended_pattern: str
    target_version_baseline: str # e.g. "Python 3.10+ (match-case)"
    refactoring_tip: str

@dataclass
class AnalysisReport:
    files_scanned: int
    total_lines: int
    detected_patterns: list[PatternMatch] = field(default_factory=list)
    code_smells: list[CodeSmell] = field(default_factory=list)
    syntax_errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        ...
```

#### 3. CLI & Runtime Strategy (`cli.py`)
- **Version Auto-Detection**: If `--py` is not explicitly passed, inspect `sys.version_info`:
  - If `>= 3.12`: defaults to `3.12`.
  - If `>= 3.10`: defaults to `3.10`.
  - Otherwise: defaults to `classic`.
- **Backward Compatibility**: Both `--py` and `--type` are accepted:
  - `--type conceptual` or `--type classic-oop` maps to `--py classic`.
  - `--type realworld` or `--type pythonic` maps to the auto-detected version.
- **Python Version Gating**:
  - If running `pat run <id> --py 3.12` on a Python `< 3.12` runtime, emit a graceful error: `Error: Python 3.12+ is required to execute PEP 695 syntax (current: {sys.version.split()[0]}).`
  - In `analyzer.py`, unparseable files append to `syntax_errors` without crashing.
- **`pat matrix <id>`**: Formats a 3-tier side-by-side comparison table (Paradigm, Version Baseline, Language Features, Lines of Code) with `--json` option.
- **`pat recommend`**: Supports `--py [classic|3.10|3.12]` (auto-detected by default) and stamps every suggestion with its explicit version requirement badge (e.g. `[Best Practice: Python 3.10+ (using match-case)]`).

---

## 5. Builder Decisions (Reviewer Check Calls)
1. **Backward Compatibility Guarantee**: Kept `conceptual_code` and `realworld_code` as dynamic properties aliasing `classic_code` and `python310_code`. All existing 96 tests and legacy calls remain 100% green without breaking changes.
2. **Runtime Version Gating**: Gated PEP 695 execution on `sys.version_info >= (3, 12)` with graceful messages for older interpreters, and isolated syntax errors in `analyzer.py` into `report.syntax_errors`.
3. **Exact Schemas Fixed**: Formally fixed the dataclass fields and `--json` serialization contracts for `PatternMatch`, `CodeSmell`, and `AnalysisReport`.
4. **Flag Compatibility**: Unified `--type` and `--py` flags under a single precedence resolver.
5. **Version-Stamped Recommendations**: Added auto-detection and explicit baseline badges to all `recommend` and `analyze` outputs.

