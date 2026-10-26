---
name: design-patterns
description: >-
  Architectural design pattern catalog, diagnostic recommender, AST analyzer, and code
  generator based on Gang of Four (GoF) and RefactoringGuru standards with Pythonic-First
  modernization. Use during planning, reverse analysis, feature design, or refactoring
  to analyze codebases, select appropriate patterns, evaluate 3-tier version trade-offs
  (classic, 3.10, 3.12), and scaffold clean Python implementations while strictly
  enforcing YAGNI and KISS.
---

# Design Patterns Skill Guide for Coding Agents

This skill enables agents to make principled architectural decisions, consult canonical Gang of Four (GoF) design patterns, analyze existing codebases for patterns and anti-patterns, compare implementations across modern Python versions, and scaffold production-ready Python code.

---

## 1. Core Philosophy: Patterns as Solutions, Not Dogma

Design patterns are reusable solutions to recurring design problems within a given context. However, **patterns introduce indirection and structural complexity**.

### Strict Anti-Over-Engineering Guidelines (YAGNI & KISS)
1. **YAGNI (You Aren't Gonna Need It)**:
   - Do NOT introduce patterns speculatively for hypothetical future requirements.
   - If a simple function or dictionary lookup solves the current problem, use it.
   - Do NOT apply patterns to one-off scripts, simple CLI tools, or straightforward data pipelines.
2. **KISS (Keep It Simple, Stupid) & Pythonic-First**:
   - Modern Python is not Java: prefer Pythonic primitives over heavyweight OOP hierarchies:
     - Use first-class functions, closures, or `Callable` instead of single-method Strategy or Command classes ("Stop Writing Classes").
     - Use `dataclasses` (with `slots=True`, `kw_only=True`) or named tuples instead of complex Builders when object creation is flat.
     - Use structural pattern matching (`match-case`) instead of elaborate Visitor or State hierarchies where states are closed and discrete.
     - Use `@singledispatch` for overloading instead of manual class dispatch trees.
     - Use context managers (`with` statement) instead of manual Proxy or lifecycle wrappers.
     - Use generator functions (`yield`) instead of full Iterator classes.
3. **When to Apply a Pattern**:
   - Apply a pattern ONLY when you encounter concrete architectural pain points:
     - Multiple variants of algorithms needing runtime interchangeability (Strategy).
     - Need to notify an open-ended number of decoupled listeners (Observer).
     - Multi-step assembly of complex composite structures (Builder).
     - Translating between incompatible legacy and modern interfaces (Adapter).
     - Tree-like part-whole hierarchies with uniform processing (Composite).
     - Complex state-dependent behaviors polluting business logic with nested conditionals (State).

---

## 2. The 3-Tier Python Version Evolution Matrix

The catalog provides 3 distinct paradigms for patterns to fit any Python deployment target:

1. **`classic`**: Classic Gang of Four OOP class hierarchies using `abc.ABC`, `@abstractmethod`, and nominal inheritance. Ideal for legacy compatibility or strict OOP frameworks.
2. **`3.10` / `3.10+`**: Idiomatic modern Python leveraging `match-case`, `dataclass(slots=True, kw_only=True)`, union type operator `X | Y`, and functional closures.
3. **`3.12` / `3.12+`**: NextGen Python leveraging PEP 695 type parameter syntax (`class Container[T]:`, `def process[T](item: T):`), `typing.Self`, and PEP 698 `@override`.

Use `--py <auto|classic|3.10|3.12>` to specify the target version. By default, `auto` detects the active Python runtime environment.

---

## 3. CLI Tooling: `bin/pat`

The repository provides a zero-setup executable CLI at `bin/pat` (as well as `pat` when installed as a Python package). AI agents should use `bin/pat` or `pat` to inspect, analyze, compare, and scaffold patterns.

### CLI Commands for Agents

#### A. Static Codebase AST Analysis (`pat analyze`)
Analyze a Python file or entire directory for detected GoF patterns, Java-in-Python anti-patterns, and version evolution opportunities:
```bash
bin/pat analyze src/
```
For machine-readable JSON output suitable for programmatic agent parsing:
```bash
bin/pat analyze src/ --json
```
Detects:
- **Detected Design Patterns**: Visitor, Singleton, Composite, Decorator, Proxy, Observer, Template Method, and Strategy.
- **Detected Code Smells**:
  - Single-Method Class ("Java in Python", recommend plain function or Callable).
  - Parameter Explosion (>5 parameters, recommend `@dataclass(kw_only=True)` or Builder).
  - Complex Branching (>3 `if`/`elif` branches, recommend `match-case` or Strategy).
  - Manual Iterator (`__iter__` and `__next__`, recommend generator `yield`).
- **Modernization Opportunities**: Version baseline modernization recommendations (Python 3.10+ and 3.12+ enhancements).

#### B. Comparing Version Evolution Matrix (`pat matrix`)
Compare the 3-tier implementation matrix (`classic`, `3.10+`, `3.12+`) for a pattern:
```bash
bin/pat matrix strategy
```
Or machine-readable JSON:
```bash
bin/pat matrix strategy --json
```

#### C. Recommending Patterns based on Problem Description
Query the built-in diagnostic recommender engine with a plain-text problem description:
```bash
bin/pat recommend -q "I need to notify multiple UI widgets when sensor data changes"
```
Or in JSON format:
```bash
bin/pat recommend -q "parse structured expressions and queries" --json
```

#### D. Inspecting Pattern Blueprints & Code
View the complete canonical implementation, intent, applicability, and trade-offs:
```bash
bin/pat show observer --json
```
View concise high-level summary:
```bash
bin/pat show strategy --summary
```
Print implementation code with Python version targeting:
```bash
bin/pat code strategy --py 3.10
bin/pat code strategy --py 3.12 --json
bin/pat code strategy --type realworld
```

#### E. Executing Runnable Examples
Execute runnable pattern examples directly with version selection:
```bash
bin/pat run strategy --py 3.10
bin/pat run singleton --type conceptual
```

#### F. Scaffolding Pattern Implementations
Generate clean, type-annotated Python starter code into a target file:
```bash
bin/pat scaffold observer --out src/events/publisher.py --py 3.10
```
To overwrite an existing file:
```bash
bin/pat scaffold strategy -o shipping.py --force
```

#### G. Searching and Browsing Patterns
List patterns by category:
```bash
bin/pat list --category behavioral
bin/pat list --category creational
bin/pat list --category structural
```
Search patterns by intent, keyword, or problem:
```bash
bin/pat search "decouple abstraction from implementation"
```

#### H. Interactive Architectural Diagnostic Wizard
To run a step-by-step diagnostic questionnaire:
```bash
bin/pat diagnose
```

---

## 4. Concrete Prompt & Command Scenarios for Agents

### Scenario 1: Reverse Code Analysis
When evaluating an existing codebase or reviewing pull requests for architectural anti-patterns:
```bash
./bin/pat analyze src/
```
*Agent action*: Parse the output. If code smells like single-method classes, parameter explosion, complex branching, or manual iterators are reported, refactor them according to the analyzer's recommendations (plain functions, `@dataclass`, `match-case`, or generators).

### Scenario 2: Paradigm Matrix Comparison
When planning how to implement a design pattern across different Python target versions:
```bash
./bin/pat matrix strategy
```
*Agent action*: Check whether the target project runs Python 3.10+ or 3.12+. Prefer the Python 3.10+ functional closure or 3.12+ generic approach over classic ABC inheritance boilerplate.

### Scenario 3: Scaffold Generation
When generating a new component based on an established design pattern:
```bash
./bin/pat scaffold strategy -o shipping.py
```
Or targeting Python 3.12+:
```bash
./bin/pat scaffold strategy -o shipping.py --py 3.12 --force
```
*Agent action*: Tailor the generated boilerplate with domain-specific naming and business logic.

---

## 5. Pattern Catalog Reference

The catalog contains all 22 classic Gang of Four patterns divided into three categories:

### Creational Patterns (5)
- **Factory Method** (`factory-method`): Provides an interface for creating objects in a superclass while allowing subclasses to alter the type of created objects.
- **Abstract Factory** (`abstract-factory`): Produces families of related or dependent objects without specifying their concrete classes.
- **Builder** (`builder`): Constructs complex objects step-by-step; allows producing different types and representations using the same construction process.
- **Prototype** (`prototype`): Produces new objects by copying existing instances without depending on their concrete classes.
- **Singleton** (`singleton`): Ensures a class has only one instance while providing a global access point to this instance.

### Structural Patterns (7)
- **Adapter** (`adapter`): Allows objects with incompatible interfaces to collaborate.
- **Bridge** (`bridge`): Splits a large class or set of closely related classes into two separate hierarchies—abstraction and implementation—which can be developed independently.
- **Composite** (`composite`): Composes objects into tree structures to represent part-whole hierarchies, allowing clients to treat individual objects and compositions uniformly.
- **Decorator** (`decorator`): Attaches new behaviors to objects dynamically by placing them inside special wrapper objects.
- **Facade** (`facade`): Provides a simplified interface to a library, a framework, or any other complex set of classes.
- **Flyweight** (`flyweight`): Fits more objects into available RAM by sharing common parts of state between multiple objects instead of keeping all data in each object.
- **Proxy** (`proxy`): Provides a surrogate or placeholder for another object to control access to it, perform lazy initialization, caching, or logging.

### Behavioral Patterns (10)
- **Chain of Responsibility** (`chain-of-responsibility`): Passes requests along a chain of handlers until one handles it.
- **Command** (`command`): Turns a request into a stand-alone object containing all information about the request, supporting undoable operations, queuing, and logging.
- **Iterator** (`iterator`): Traverses elements of a collection without exposing its underlying representation.
- **Mediator** (`mediator`): Restricts direct communications between objects and forces them to collaborate only via a mediator object.
- **Memento** (`memento`): Saves and restores the previous state of an object without revealing the details of its implementation.
- **Observer** (`observer`): Defines a subscription mechanism to notify multiple objects about any events that happen to the object they're observing.
- **State** (`state`): Allows an object to alter its behavior when its internal state changes, appearing as if it changed its class.
- **Strategy** (`strategy`): Defines a family of algorithms, puts each in a separate class, and makes their objects interchangeable.
- **Template Method** (`template-method`): Defines the skeleton of an algorithm in the superclass but lets subclasses override specific steps without changing structure.
- **Visitor** (`visitor`): Separates algorithms from the objects on which they operate.

---

## 6. Agent Step-by-Step Workflow

When working on a feature, bugfix, or refactoring task:

1. **Analyze Existing Code (Reverse Analysis)**:
   - Run `bin/pat analyze <target_dir> --json` to detect existing patterns and anti-patterns.
2. **Evaluate Simpler Alternatives First (YAGNI/KISS)**:
   - Ask: Can this be solved with a simple function, a standard Python dictionary, pattern matching (`match-case`), or a standard library utility (`functools`, `dataclasses`, `itertools`)?
   - If yes, **stop here** and use the simple Pythonic solution.
3. **Query Recommender**:
   - Run `bin/pat recommend -q "<friction description>" --json`.
   - Inspect the top recommended patterns, their confidence scores, and Python version compatibility.
4. **Compare Modern Paradigms**:
   - Run `bin/pat matrix <id>` to inspect the classic vs Python 3.10+ vs Python 3.12+ implementations.
5. **Scaffold & Adapt**:
   - Run `bin/pat scaffold <id> --out <target_file> --py <auto|classic|3.10|3.12>`.
   - Tailor the scaffolded code to the domain: rename generic terms (`ConcreteComponent`, `Receiver`) to domain terms (`PaymentGateway`, `OrderProcessor`).
6. **Verify with Tests**:
   - Write comprehensive unit tests verifying both the happy path and edge cases.
