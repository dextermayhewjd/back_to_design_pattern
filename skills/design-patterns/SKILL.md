---
name: design-patterns
description: >-
  Architectural design pattern catalog, diagnostic recommender, and code generator
  based on Gang of Four (GoF) and RefactoringGuru standards. Use during planning,
  feature design, or refactoring to select appropriate patterns, evaluate trade-offs,
  and scaffold clean Python implementations while strictly enforcing YAGNI and KISS.
---

# Design Patterns Skill Guide for Coding Agents

This skill enables agents to make principled architectural decisions, consult canonical Gang of Four (GoF) design patterns, diagnose architectural friction, and scaffold production-ready Python implementations.

---

## 1. Core Philosophy: Patterns as Solutions, Not Dogma

Design patterns are reusable solutions to recurring design problems within a given context. However, **patterns introduce indirection and structural complexity**.

### Strict Anti-Over-Engineering Guidelines (YAGNI & KISS)
1. **YAGNI (You Aren't Gonna Need It)**:
   - Do NOT introduce patterns speculatively for hypothetical future requirements.
   - If a simple function or dictionary lookup solves the current problem, use it.
   - Do NOT apply patterns to one-off scripts, simple CLI tools, or straightforward data pipelines.
2. **KISS (Keep It Simple, Stupid)**:
   - Prefer standard Python idioms over heavyweight OOP hierarchies:
     - Use first-class functions or lambdas instead of single-method Strategy classes when behavior is simple.
     - Use `dataclasses` or named tuples instead of complex Builders when object creation is flat.
     - Use dictionary dispatch (`handlers[event_type](payload)`) instead of Chain of Responsibility or State patterns if transitions are static.
     - Use context managers (`with` statement) instead of manual lifecycle management.
3. **When to Apply a Pattern**:
   - Apply a pattern ONLY when you encounter concrete architectural pain points:
     - Multiple variants of algorithms needing runtime interchangeability (Strategy).
     - Need to notify an open-ended number of decoupled listeners (Observer).
     - Multi-step assembly of complex composite structures (Builder).
     - Translating between incompatible legacy and modern interfaces (Adapter).
     - Tree-like part-whole hierarchies with uniform processing (Composite).
     - Complex state-dependent behaviors polluting business logic with nested conditionals (State).

---

## 2. CLI Tooling: `bin/pat`

The repository provides a zero-setup executable CLI at `bin/pat` (as well as `pat` when installed as a Python package). AI agents should use `bin/pat` or `pat` to inspect and scaffold patterns directly.

### CLI Usage for Agents

#### A. Recommending Patterns based on Problem Description
Query the built-in diagnostic recommender engine with a plain-text problem description:
```bash
bin/pat recommend -q "I need to notify multiple UI widgets when sensor data changes"
```
For machine-readable JSON output suitable for programmatic agent parsing:
```bash
bin/pat recommend -q "parse structured expressions and queries" --json
```

#### B. Inspecting Pattern Blueprints & Code Examples
View the complete canonical implementation, intent, applicability, and trade-offs:
```bash
bin/pat show observer --json
```
Or view a concise high-level summary:
```bash
bin/pat show strategy --summary
```

#### C. Scaffolding Pattern Implementations
Generate a clean, standalone, type-annotated Python starter implementation into a specified file:
```bash
bin/pat scaffold observer --out src/events/publisher.py
```
To overwrite an existing file:
```bash
bin/pat scaffold observer --out src/events/publisher.py --force
```

#### D. Searching and Browsing Patterns
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

#### E. Interactive Architectural Diagnostic Wizard
To run a step-by-step diagnostic questionnaire:
```bash
bin/pat diagnose
```

#### F. Inspecting Implementation Code & Executing Runnable Examples
Inspect pure conceptual or real-world implementation code:
```bash
bin/pat code strategy --type conceptual
bin/pat code strategy --type realworld --json
```
Execute runnable pattern examples directly:
```bash
bin/pat run singleton --type conceptual
```

---

## 3. Pattern Catalog Reference

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

## 4. Agent Step-by-Step Workflow

When working on a feature, bugfix, or refactoring task:

1. **Analyze Requirements & Identify Friction**:
   - Determine if there is genuine structural friction: e.g., rigid conditional logic (`if/elif` sprawl), tight coupling between disparate subsystems, or code duplication across variants.
2. **Evaluate Simpler Alternatives First (YAGNI/KISS)**:
   - Ask: Can this be solved with a simple function, a standard Python dictionary, or a standard library utility (`functools.partial`, `dataclasses`, `itertools`, `abc`)?
   - If yes, **stop here** and use the simple solution.
3. **Query Recommender**:
   - Run `bin/pat recommend -q "<friction description>" --json`.
   - Inspect the top recommended patterns and their confidence scores.
4. **Weigh Pros, Cons, and Complexity**:
   - Check pattern details via `bin/pat show <id> --json`.
   - Evaluate trade-offs: Will the increased flexibility justify the added classes and indirection?
5. **Scaffold & Adapt**:
   - Run `bin/pat scaffold <id> --out <target_file>`.
   - Tailor the scaffolded code to the domain: rename generic terms (`ConcreteComponent`, `Receiver`) to domain terms (`PaymentGateway`, `OrderProcessor`).
6. **Verify with Tests**:
   - Write comprehensive unit tests verifying both the happy path and edge cases.
