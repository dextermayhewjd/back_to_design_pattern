# Design Document: Python Design Patterns CLI & Universal Agent Plugin

## 1. Intent and Why
Software developers and autonomous AI agents (such as Google Antigravity `agy`, Claude Code, OpenAI Codex, and Cursor) frequently encounter architectural challenges when implementing features or refactoring legacy code. Without structured design principles, agent-generated code can easily devolve into tight coupling, monolithic classes, and brittle switch-case logic.

RefactoringGuru provides world-class explanations and Python implementations for the 22 classic Gang of Four (GoF) design patterns. By distilling these patterns into an offline, zero-dependency Python CLI tool (`pat` / `design-patterns`) and bundling it as a cross-platform, multi-agent plugin (compatible with `agy`, Claude Code, and standard agent skills), we provide both human developers and AI agents with:
1. Immediate offline access to pattern metadata, trade-offs, and Pythonic implementations.
2. A diagnostic recommendation engine that maps architectural pain points to appropriate design patterns.
3. Rapid boilerplate / scaffolding generation for clean, type-hinted Python architectures.
4. Agent behavioral rules and skills that enforce thoughtful design decisions without over-engineering.

---

## 2. Goals, Non-Goals, and Anti-Goals

### Goals
- **Complete GoF Coverage**: Support all 22 classic GoF patterns across Creational (5), Structural (7), and Behavioral (10) categories.
- **Pythonic Implementations**: Every pattern must include idiomatic Python 3.10+ implementations using modern language features (`abc.ABC`, `typing`, `dataclasses`, and type hints).
- **Dual Examples per Pattern**:
  - *Conceptual Example*: Minimalist, role-labeled code explaining participant relationships.
  - *Real-World Example*: Practical scenario (e.g. multi-format document exporter, notification dispatch, database connectivity, UI component trees).
- **Standalone CLI (`pat` / `python -m design_patterns`)**:
  - `list`: Browse all patterns with 1-line intents and categories (text and JSON output).
  - `show <pattern>`: Comprehensive details: intent, problem/solution, applicability triggers, pros/cons, and relations with other patterns.
  - `code <pattern> [--type conceptual|realworld]`: Output directly runnable Python code.
  - `recommend [--query "<symptom/problem>"]`: Heuristic rule-based matching engine mapping architectural requirements to pattern candidates.
  - `scaffold <pattern> [--out <path>]`: Generate customizable boilerplate templates with placeholder classes.
  - `run <pattern>`: Execute pattern demonstration code and display live stdout.
- **Universal Agent Plugin Compatibility**:
  - `plugin.json` compatible with Antigravity (`agy plugin install <repo-url>`) and Claude Code plugins.
  - `skills/design-patterns/SKILL.md` exposing progressive disclosure workflows and slash command triggers for agents.
  - `rules/AGENTS.md` guiding agents on when to consult design patterns during planning, refactoring, and feature additions.
- **Zero Heavy External Dependencies**: Built entirely on standard Python 3.10+ libraries (`argparse`, `dataclasses`, `typing`, `abc`, `json`, `sys`, `pathlib`).

### Non-Goals
- Web UI or graphical dashboard.
- Cloud API synchronization or remote telemetry.
- Dynamic bytecode rewriting or runtime monkey-patching.

### Anti-Goals
- **Over-Engineering Dogmatism**: Patterns must not be forced where simple functions or modules suffice. The agent skill must explicitly enforce *YAGNI* (You Aren't Gonna Need It) and *KISS* (Keep It Simple, Stupid).
- **Fragile Installation Requirements**: The CLI must be runnable without mandatory `pip install` by supporting direct `python3 src/design_patterns` execution as well as editable/package installs.

---

## 3. Constraints
- **Python Version**: Python 3.10 or higher.
- **Dependency Constraint**: Pure Python Standard Library for runtime execution. `pytest` for running unit tests.
- **Plugin Standards**: Must conform strictly to Antigravity plugin manifest specifications (`plugin.json` at root, `skills/<name>/SKILL.md`, `rules/AGENTS.md`).

---

## 4. Approaches Considered

### Approach 1: Pure Python CLI + Universal Agent Skill Plugin (Selected)
- **Architecture**: A modular Python package providing a standalone CLI (`pat`) bundled with `plugin.json`, `skills/design-patterns/SKILL.md`, and `rules/AGENTS.md`.
- **Trade-offs**:
  - *Pros*: Maximum portability; zero external runtime dependencies; can be invoked by humans in bash, by agents via terminal tools, and by `agy plugin install`.
  - *Cons*: Agent interactions rely on terminal commands / bash tool rather than custom protocol RPCs.
- **Selection Rationale**: Meets the user's explicit request for wide agent interoperability (`agy`, Claude Code, Codex) without external daemon or socket dependencies.

### Approach 2: CLI + Dedicated Model Context Protocol (MCP) Server Plugin
- **Architecture**: In addition to Approach 1, bundles an MCP server exposing JSON-RPC endpoints (`get_pattern`, `recommend_pattern`).
- **Trade-offs**:
  - *Pros*: Rich structured tool calling in MCP-native clients.
  - *Cons*: Requires running an external process/daemon, introduces MCP SDK dependencies, and is incompatible with agents that lack MCP support. Dropped in favor of universal CLI/Skill simplicity.

### Approach 3: Static Markdown/JSON Knowledge Base
- **Architecture**: Plain markdown repository without an executable Python CLI.
- **Trade-offs**:
  - *Pros*: Zero code to maintain.
  - *Cons*: Cannot run code demonstrations, cannot generate scaffold files dynamically, lacks interactive diagnostic recommendations. Rejected.

---

## 5. Architectural Specification & Directory Structure

### Directory Layout
```text
back_to_design_pattern/
├── bin/
│   └── pat                                  # Zero-setup standalone executable launcher
├── plugin.json                              # Antigravity & Agent plugin manifest
├── pyproject.toml                           # Python package definition (entrypoint: pat)
├── README.md                                # Human & Agent documentation
├── rules/
│   └── AGENTS.md                            # Universal architectural guidelines
├── skills/
│   └── design-patterns/
│       └── SKILL.md                         # Agent skill & progressive disclosure
├── src/
│   └── design_patterns/
│       ├── __init__.py
│       ├── __main__.py                      # Entry point for python -m design_patterns
│       ├── cli.py                           # CLI commands and argument parsing
│       ├── models.py                        # Dataclasses: Pattern, Category, Metadata
│       ├── recommender.py                   # Symptom & heuristic matching engine + wizard
│       ├── registry.py                      # Pattern registration and index
│       └── catalog/                         # 22 Pattern Modules
│           ├── __init__.py
│           ├── creational/
│           │   ├── __init__.py
│           │   ├── factory_method.py
│           │   ├── abstract_factory.py
│           │   ├── builder.py
│           │   ├── prototype.py
│           │   └── singleton.py
│           ├── structural/
│           │   ├── __init__.py
│           │   ├── adapter.py
│           │   ├── bridge.py
│           │   ├── composite.py
│           │   ├── decorator.py
│           │   ├── facade.py
│           │   ├── flyweight.py
│           │   └── proxy.py
│           └── behavioral/
│               ├── __init__.py
│               ├── chain_of_responsibility.py
│               ├── command.py
│               ├── iterator.py
│               ├── mediator.py
│               ├── memento.py
│               ├── observer.py
│               ├── state.py
│               ├── strategy.py
│               ├── template_method.py
│               └── visitor.py
└── tests/
    ├── test_cli.py
    ├── test_registry.py
    ├── test_recommender.py
    └── test_patterns_execution.py
```

### Core Components

#### 1. Data Models (`models.py`)
- `Category` (Enum): `CREATIONAL`, `STRUCTURAL`, `BEHAVIORAL`.
- `Pattern`:
  - `id`: kebab-case identifier (e.g. `abstract-factory`).
  - `name`: English name (e.g. "Abstract Factory").
  - `chinese_name`: 中文名 (e.g. "抽象工厂").
  - `category`: `Category`.
  - `intent`: Single-sentence summary of the pattern's goal.
  - `problem`: Architectural pain points and challenges prior to applying the pattern.
  - `solution`: How the pattern structures classes and interfaces to solve the problem.
  - `applicability`: Concrete trigger conditions and scenarios where the pattern fits.
  - `symptoms`: List of diagnostic symptoms/keywords used for heuristic matching.
  - `pros`: List of benefits.
  - `cons`: List of trade-offs / drawbacks.
  - `relations`: Related patterns and comparisons (e.g., Abstract Factory vs Factory Method).
  - `conceptual_code`: Python source string.
  - `realworld_code`: Python source string with realistic scenario.
  - `scaffold_template`: Python starter boilerplate string.

#### 2. Recommender Engine (`recommender.py`)
- Supports two recommendation flows:
  1. **Query Matching Mode** (`--query "<text>"` / `-q`): Matches queries against pattern symptoms, problems, applicability, and keywords using weighted scoring.
  2. **Interactive Diagnostic Wizard Mode** (`--interactive`): A guided 3-stage terminal questionnaire (Category classification -> Core design tension -> Scored pattern candidates with explanation).
- Heuristic symptom mappings:
  - "family of related products without specifying concrete classes" -> `abstract-factory`
  - "complex object construction with many parameters / telescoping constructors" -> `builder`
  - "incompatible interfaces between classes" -> `adapter`
  - "dynamically attach new responsibilities / wrapping" -> `decorator`
  - "undo, redo, rollback, state history" -> `memento` / `command`
  - "swap interchangeable algorithms at runtime" -> `strategy`
  - "object alters behavior when internal state changes" -> `state`
  - "tree structure / part-whole hierarchy" -> `composite`
  - "1-to-N notification / event subscription" -> `observer`
  - "pass request along dynamic chain of handlers" -> `chain-of-responsibility`

#### 3. Zero-Setup Agent & CLI Execution (`bin/pat`)
- In addition to standard `pip install` entry points via `pyproject.toml`, a standalone executable launcher `bin/pat` is included at the repository root.
- The launcher dynamically resolves its own directory, injects `src` into `sys.path`, and executes the CLI directly.
- When an agent installs the plugin via `agy plugin install`, the agent's `SKILL.md` can invoke the launcher via relative path `${PLUGIN_DIR}/bin/pat` or global `pat` if in `$PATH`, guaranteeing zero-setup execution without requiring the user or agent to run `pip install`.

#### 4. CLI Command Interface (`cli.py`)
- Built using Python's standard `argparse`.
- Supported subcommands:
  - `list [--category <creational|structural|behavioral>] [--json]`
  - `show <pattern_id> [--json]`
  - `code <pattern_id> [--type conceptual|realworld]`
  - `scaffold <pattern_id> [--out <filepath>]`
  - `recommend [--query "<problem description>"] [--interactive]`
  - `run <pattern_id> [--type conceptual|realworld]`

#### 5. Universal Agent Skill (`skills/design-patterns/SKILL.md`)
- Provides instructions for agents on:
  - When to consult design patterns (architectural refactoring, extending legacy modules, designing new subsystems).
  - Progressive disclosure: how to run `bin/pat recommend` to test architectural hypotheses.
  - How to generate and inspect scaffolding before writing production code.
  - Cautionary checks: checking for pattern over-use and anti-patterns.

#### 6. Universal Agent Rules (`rules/AGENTS.md`)
- Always-on rule ensuring agents evaluate architectural modularity, follow open-closed and single-responsibility principles, and consult `pat` when facing complex multi-class structures.

---

## 6. Builder Decisions (Reviewer Check Calls)
1. **Interactive Recommender (`--interactive`)**: Sized as a structured 3-stage diagnostic wizard (Category selection -> Pain point selection -> Scored recommendation summary) for terminal users, while agents can use `-q / --query` for non-interactive automated scoring.
2. **Zero-Setup Agent Execution**: Added `bin/pat` launcher to resolve `sys.path` so the plugin works immediately after `agy plugin install` without needing `pip install` or `$PATH` modifications.
3. **Data Model Completeness**: Explicitly retained `problem`, `solution`, and `applicability` in the `Pattern` model to ensure complete RefactoringGuru fidelity and rich `--json` exports for agents.


---

## 6. What's Left to the Builder
- Detailed styling of CLI terminal output (clean tables, headers, ANSI formatting).
- Exact real-world domain scenarios chosen for each pattern (e.g., SQLite vs Postgres connection for Abstract Factory, HTTP cache for Proxy, GUI widgets for Composite, etc.).
- Unit test suite coverage and assertions.
