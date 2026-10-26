# Python GoF Design Patterns CLI, Recommender & Agent Plugin

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A canonical, RefactoringGuru-faithful catalog of all 22 Gang of Four (GoF) design patterns implemented in idiomatic Python, paired with an interactive diagnostic recommender, code generator, and universal multi-agent plugin.

Designed for human software engineers, engineering teams, and AI coding agents (Antigravity, Claude Code, Cursor, Codex).

---

## Features

- **All 22 Gang of Four Patterns**: Complete catalog across Creational, Structural, and Behavioral categories with rich metadata (intent, problem, solution, applicability, pros, cons, and full executable code).
- **Zero-Setup CLI Launcher**: Run immediately via `bin/pat` with zero external dependencies (pure Python standard library).
- **Intelligent Recommender**: Diagnostic search engine matching natural-language architectural problem statements to candidate patterns with confidence scores and rationale.
- **Interactive Diagnostic Wizard**: Guided step-by-step questionnaire diagnosing architectural friction and recommending optimal patterns.
- **Code Scaffolding**: Generate clean, type-annotated, runnable starter templates directly into your project files.
- **Machine-Readable Outputs**: All query commands support `--json` output for direct programmatic integration with AI agents.
- **Universal Agent Plugin**: Ships with `plugin.json`, `skills/design-patterns/SKILL.md`, and `rules/AGENTS.md` enforcing SOLID principles and anti-over-engineering guidelines (YAGNI / KISS).

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
| `code` | `-t`, `--type <conceptual\|realworld>`, `--json` | Print Python implementation code for a pattern | `bin/pat code strategy --type realworld` |
| `scaffold` | `-o`, `--out`, `--force` / `--overwrite`, `--json` | Generate starter code for a pattern to a target file | `bin/pat scaffold strategy --out src/strategy.py --force` |
| `recommend` | `-q`, `--query`, `-i`, `--interactive`, `--top`, `--json` | Recommend patterns from a natural-language description | `bin/pat recommend -q "notify multiple UI elements"` |
| `search` | Alias to `recommend --query` (`--top`, `--json`) | Search pattern names, intents, and keywords | `bin/pat search "decouple abstraction"` |
| `diagnose` | Alias to `recommend --interactive` (`--json`) | Interactive diagnostic wizard to find the right pattern | `bin/pat diagnose` |
| `run` | `-t`, `--type <conceptual\|realworld>` | Execute runnable pattern example directly | `bin/pat run singleton --type conceptual` |

### CLI Options & Flags
- `--json`: Output results in structured JSON format (ideal for AI agents).
- `--summary`: Output a concise summary without full source code.
- `--category <creational\|structural\|behavioral>`: Filter list results by category.
- `--force` / `--overwrite`: Overwrite existing destination file during scaffolding.
- `--type <conceptual|realworld>`: Select implementation variant for code inspection or execution.
- `--top <n>`: Limit number of recommendations returned (default: 3).

### CLI Examples

#### Recommend Patterns
```bash
bin/pat recommend -q "I need to add logging and caching without modifying the original service"
```

#### Show Pattern in JSON Format
```bash
bin/pat show decorator --json
```

#### Scaffold a Pattern
```bash
bin/pat scaffold factory-method --out src/creators/factory.py
```

#### Interactive Diagnosis
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
│   └── AGENTS.md                 # Universal architectural rules & SOLID guidelines
├── skills/
│   └── design-patterns/
│       └── SKILL.md              # Agent skill guide and execution workflows
├── src/
│   └── design_patterns/
│       ├── __init__.py           # Package exports
│       ├── cli.py                # Command-line interface with ANSI and JSON modes
│       ├── model.py              # Domain dataclasses (Pattern, Category, TradeOff, etc.)
│       ├── registry.py           # In-memory PatternRegistry storing 22 GoF patterns
│       ├── recommender.py        # Diagnostic scoring engine & interactive wizard
│       └── patterns/
│           ├── __init__.py       # Auto-loader registering all pattern modules
│           ├── creational.py     # 5 Creational patterns
│           ├── structural.py     # 7 Structural patterns
│           └── behavioral.py     # 10 Behavioral patterns
└── tests/                        # Comprehensive pytest test suite
```

---

## Agent Integration

This repository is pre-configured as an Antigravity and Claude Code plugin.

- **Skill (`skills/design-patterns/SKILL.md`)**: Instructs AI agents on when and how to consult patterns, how to run `bin/pat` commands, and how to evaluate architectural trade-offs.
- **Architectural Rules (`rules/AGENTS.md`)**: Enforces SOLID principles, high cohesion, loose coupling, refactoring safety, and strict anti-over-engineering rules (YAGNI / KISS).

---

## Development & Testing

Run the full test suite using `pytest`:

```bash
pytest tests/ -v
```

All 22 patterns and CLI features are validated with automated unit tests.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
