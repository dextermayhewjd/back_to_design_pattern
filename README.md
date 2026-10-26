# Python GoF Design Patterns CLI, Recommender, AST Analyzer & Agent Plugin

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A canonical, RefactoringGuru-faithful catalog of all 22 Gang of Four (GoF) design patterns implemented in idiomatic Python, paired with a static AST pattern analyzer, 3-tier version evolution matrix, interactive diagnostic recommender, code generator, and universal multi-agent plugin.

Designed for human software engineers, engineering teams, and AI coding agents (Antigravity, Claude Code, Cursor, Codex) to build maintainable, Pythonic systems while strictly enforcing YAGNI, KISS, and "Stop Writing Classes" principles.

---

## Features

- **All 22 Gang of Four Patterns**: Complete catalog across Creational, Structural, and Behavioral categories with rich metadata (intent, problem, solution, applicability, pros, cons, and executable code).
- **3-Tier Version Evolution Matrix (`pat matrix`)**: Compare and choose between `classic` GoF OOP hierarchies (ABCs), idiomatic `3.10+` baseline (`match-case`, `@dataclass(slots=True, kw_only=True)`, closures), and next-generation `3.12+` syntax (PEP 695 type parameters `class C[T]:`, `typing.Self`, PEP 698 `@override`).
- **AST Pattern Analyzer & Anti-Pattern Detector (`pat analyze`)**: Static AST analysis of Python source files and directories to automatically identify implemented design patterns (Visitor, Singleton, Composite, Decorator, Proxy, Observer, Template Method, and Strategy), detect code smells (Single-Method Class, Parameter Explosion, Complex Branching, and Manual Iterator), and suggest version modernization opportunities.
- **Pythonic-First Architecture**: Built on the "Stop Writing Classes" principle—prioritizing functions, `Callable`, structural pattern matching, dataclasses, and `@singledispatch` over heavyweight OOP boilerplate.
- **Intelligent Diagnostic Recommender**: Natural-language search engine matching architectural friction statements to candidate patterns with confidence scores, rationale, and runtime requirements.
- **Interactive Diagnostic Wizard**: Guided step-by-step questionnaire diagnosing architectural friction and recommending optimal patterns.
- **Code Scaffolding**: Generate clean, type-annotated, runnable starter templates directly into your project files with `--out`.
- **Zero-Setup CLI Launcher**: Run immediately via `bin/pat` with zero external dependencies (pure Python standard library).
- **Machine-Readable Outputs**: All query, analysis, and matrix commands support `--json` output for direct programmatic integration with AI agents.
- **Universal Multi-Agent Plugin**: Pre-configured with `plugin.json`, `skills/design-patterns/SKILL.md`, and `rules/AGENTS.md` enforcing SOLID principles, Pythonic guidelines, and anti-over-engineering rules.

---

## Installation

### 1. As an Antigravity Plugin
Install or mount the plugin in Antigravity CLI:
```bash
agy plugin install .
```
Or enable it in your workspace configuration:
```bash
agy plugin enable design-patterns
```

### 2. As a Python Package
Install locally with `pip`:
```bash
pip install .
```
Or in editable development mode:
```bash
pip install -e .
```
This registers the global `pat` command in your environment.

### 3. Zero-Setup (No Installation Required)
You can directly run the launcher script from the repository root:
```bash
./bin/pat --help
```

---

## CLI Commands Cheat Sheet

| Command | Aliases / Key Flags | Description | Example |
| :--- | :--- | :--- | :--- |
| `list` | `-c`, `--category`, `--json` | List all patterns, optionally filtered by category | `bin/pat list --category creational` |
| `show` | `--summary`, `--json` | Display detailed documentation and code for a pattern | `bin/pat show observer --summary` |
| `code` | `--py <auto\|classic\|3.10\|3.12>`, `-t`, `--type`, `--json` | Print Python implementation code for a pattern | `bin/pat code strategy --py 3.10` |
| `matrix` | `--json` | Display 3-tier version evolution matrix (`classic`, `3.10`, `3.12`) | `bin/pat matrix strategy` |
| `analyze` | `--json` | Statically analyze Python code for patterns and anti-patterns | `bin/pat analyze src/` |
| `scaffold` | `--py <auto\|classic\|3.10\|3.12>`, `-o`, `--out`, `--force` / `--overwrite`, `--json` | Generate starter code for a pattern to a target file | `bin/pat scaffold strategy -o src/strategy.py --force` |
| `recommend` | `-q`, `--query`, `-i`, `--interactive`, `--top`, `--json` | Recommend patterns from a natural-language description | `bin/pat recommend -q "notify multiple UI elements"` |
| `search` | Alias to `recommend --query` (`--top`, `--json`) | Search pattern names, intents, and keywords | `bin/pat search "decouple abstraction"` |
| `diagnose` | Alias to `recommend --interactive` (`--json`) | Interactive diagnostic wizard to find the right pattern | `bin/pat diagnose` |
| `run` | `--py <auto\|classic\|3.10\|3.12>`, `-t`, `--type` | Execute runnable pattern example directly | `bin/pat run strategy --py 3.12` |

### CLI Options & Flags
- `--py <auto|classic|3.10|3.12>`: Target Python version tier for code, run, and scaffold commands (default: `auto`).
- `--json`: Output results in structured JSON format (ideal for AI agents).
- `--summary`: Output a concise summary without full source code.
- `--category <creational|structural|behavioral>`: Filter list results by category.
- `--out` / `-o`: Destination file path for scaffolding.
- `--force` / `--overwrite`: Overwrite existing destination file during scaffolding.
- `--top <n>`: Limit number of recommendations returned (default: 3).

---

## The 3-Tier Python Version Evolution Matrix

Python has evolved significantly from classic Java-like OOP hierarchies to modern, multi-paradigm idioms. This catalog presents every pattern across three distinct evolutionary tiers:

| Feature / Aspect | `classic` (Python 3.8+) | `3.10+` Modern Baseline | `3.12+` NextGen |
| :--- | :--- | :--- | :--- |
| **Primary Abstraction** | Abstract Base Classes (`abc.ABC`) | Closures, Callables & `typing.Protocol` | Generic Protocols & PEP 695 |
| **Type Parameters** | `TypeVar('T')` (verbose) | `TypeVar('T')` / Union `X \| Y` | PEP 695 `class C[T]:`, `def f[T](x: T):` |
| **Branching / Dispatch** | Polymorphic class hierarchies | Structural Pattern Matching (`match-case`) | `match-case` with guard clauses |
| **Data Representation** | Standard classes with manual `__init__` | `@dataclass(slots=True, kw_only=True)` | Modern slotted `@dataclass` |
| **Method Guarantees** | Convention & docstrings | Type annotations | PEP 698 `@override` & `typing.Self` |
| **Over-Engineering Risk** | High (excessive inheritance trees) | Low (functions and closures) | Minimal (clean, self-documenting syntax) |

Use `pat matrix <pattern_id>` to view side-by-side architectural comparisons, pros, cons, and code snippets for any pattern:
```bash
bin/pat matrix strategy
bin/pat matrix observer --json
```

---

## Reverse AST Pattern Analysis & Anti-Pattern Detection

Use `pat analyze <target>` to run static AST analysis on any Python source file or codebase directory:

```bash
bin/pat analyze src/
```

The analyzer statically detects:
1. **Implemented Design Patterns**: Recognizes 8 classic patterns across Python codebases:
   - **Visitor**: Classes implementing the visitor interface (`accept` method or `visit_*` dispatch).
   - **Singleton**: Classes controlling instance creation via `__new__` instance caching or singleton metaclasses.
   - **Composite**: Classes managing child component hierarchies with `add`/`remove` methods.
   - **Decorator & Proxy**: Classes wrapping an inner component or target and delegating method calls.
   - **Observer**: Classes managing event subscriptions (`subscribe`/`attach`) and publishing notifications (`notify`/`publish`).
   - **Template Method**: Abstract classes coordinating abstract/hook methods from a template skeleton method.
   - **Strategy**: Context classes delegating execution to an injected strategy argument or Callable.
2. **Code Smells & Anti-Patterns**:
   - **Single-Method Class ("Java in Python")**: Flags classes with only 1 public method, recommending refactoring to a plain function or Callable strategy.
   - **Parameter Explosion**: Flags functions or methods with more than 5 parameters, recommending grouping into a `@dataclass(kw_only=True)` or Builder.
   - **Complex Branching**: Flags functions with more than 3 `if`/`elif` branches, recommending refactoring to `match-case` or Strategy dispatch.
   - **Manual Iterator**: Flags classes manually implementing `__iter__` and `__next__`, recommending replacement with a generator function using `yield`.
3. **Modernization Opportunities**: Suggests upgrades to Python 3.10+ structural pattern matching, union syntax, or Python 3.12+ generic parameters.

---

## CLI Examples

### Recommend Patterns from a Problem Description
```bash
bin/pat recommend -q "I need to add logging and caching without modifying the original service"
```

### Compare Paradigms Across Python Versions
```bash
bin/pat matrix strategy
```

### Run Static AST Analysis
```bash
bin/pat analyze src/
```

### Show Pattern in JSON Format
```bash
bin/pat show decorator --json
```

### Inspect Version-Specific Code
```bash
bin/pat code strategy --py 3.10
bin/pat code strategy --py 3.12
```

### Execute Pattern Examples
```bash
bin/pat run strategy --py 3.10
bin/pat run singleton --type conceptual
```

### Scaffold a Pattern
```bash
bin/pat scaffold factory-method --out src/creators/factory.py
```

### Interactive Diagnosis
```bash
bin/pat diagnose
```

---

## Pattern Catalog Overview

### Creational Patterns
| Pattern ID | Name | Intent |
| :--- | :--- | :--- |
| `factory-method` | Factory Method | Provides an interface for creating objects in a superclass while letting subclasses alter the created types. |
| `abstract-factory` | Abstract Factory | Lets you produce families of related or dependent objects without specifying concrete classes. |
| `builder` | Builder | Lets you construct complex objects step by step and produce different representations. |
| `prototype` | Prototype | Lets you copy existing objects without making your code dependent on their classes. |
| `singleton` | Singleton | Lets you ensure that a class has only one instance while providing a global access point. |

### Structural Patterns
| Pattern ID | Name | Intent |
| :--- | :--- | :--- |
| `adapter` | Adapter | Allows objects with incompatible interfaces to collaborate. |
| `bridge` | Bridge | Splits a large class into separate abstraction and implementation hierarchies. |
| `composite` | Composite | Composes objects into tree structures to represent part-whole hierarchies. |
| `decorator` | Decorator | Attaches new behaviors to objects dynamically by placing them inside wrappers. |
| `facade` | Facade | Provides a simplified interface to a complex subsystem or library. |
| `flyweight` | Flyweight | Fits more objects into RAM by sharing common state among multiple objects. |
| `proxy` | Proxy | Provides a surrogate or placeholder for another object to control access, caching, or logging. |

### Behavioral Patterns
| Pattern ID | Name | Intent |
| :--- | :--- | :--- |
| `chain-of-responsibility` | Chain of Responsibility | Passes requests along a chain of handlers until one handles it. |
| `command` | Command | Encapsulates requests as standalone objects for queueing, logging, and undo. |
| `iterator` | Iterator | Traverses elements of a collection without exposing underlying representation. |
| `mediator` | Mediator | Restricts direct communication between objects, routing through a mediator. |
| `memento` | Memento | Saves and restores an object's previous state without exposing implementation. |
| `observer` | Observer | Defines a subscription mechanism to notify multiple objects of state changes. |
| `state` | State | Lets an object alter its behavior when its internal state changes. |
| `strategy` | Strategy | Defines a family of algorithms and makes them interchangeable at runtime. |
| `template-method` | Template Method | Defines algorithm skeleton in a superclass, letting subclasses override steps. |
| `visitor` | Visitor | Separates algorithms from the objects on which they operate. |

---

## Architecture Overview

```text
back_to_design_pattern/
├── bin/
│   └── pat                       # Zero-dependency CLI entry point executable
├── plugin.json                   # Universal plugin manifest (Antigravity / Claude Code)
├── pyproject.toml                # Standard PEP 518/621 Python package configuration
├── rules/
│   └── AGENTS.md                 # Universal architectural rules, Pythonic guidelines & 3-tier matrix
├── skills/
│   └── design-patterns/
│       └── SKILL.md              # Agent skill guide and execution workflows
├── src/
│   └── design_patterns/
│       ├── __init__.py           # Package exports and version metadata
│       ├── __main__.py           # Package execution entry point
│       ├── analyzer.py           # AST Pattern Analyzer & Anti-Pattern Detector
│       ├── cli.py                # Command-line interface with ANSI and JSON modes
│       ├── models.py             # Domain dataclasses (Pattern, Category, EvolutionMatrix, etc.)
│       ├── recommender.py        # Diagnostic scoring engine & interactive wizard
│       ├── registry.py           # In-memory PatternRegistry storing 22 GoF patterns
│       └── catalog/
│           ├── __init__.py       # Auto-loader registering all pattern modules
│           ├── creational/       # 5 Creational patterns with multi-version code
│           ├── structural/       # 7 Structural patterns with multi-version code
│           └── behavioral/       # 10 Behavioral patterns with multi-version code
└── tests/                        # Comprehensive pytest test suite
```

---

## Agent Integration

This repository is pre-configured as an Antigravity and Claude Code plugin.

- **Skill (`skills/design-patterns/SKILL.md`)**: Instructs AI agents on how to analyze code with `pat analyze`, compare versions with `pat matrix`, consult patterns, run commands, and evaluate architectural trade-offs.
- **Architectural Rules (`rules/AGENTS.md`)**: Enforces "Pythonic-First" / "Stop Writing Classes" principles, the 3-tier version evolution matrix, SOLID guidelines, high cohesion, loose coupling, and strict anti-over-engineering rules (YAGNI / KISS).

---

## Development & Testing

Run the full test suite using `pytest`:

```bash
pytest tests/ -v
```

All 22 patterns, the AST analyzer, version matrices, and CLI commands are validated with automated unit tests.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
