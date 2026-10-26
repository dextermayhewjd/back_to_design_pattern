# Universal Architectural Guidelines & Agent Rules

These rules govern architectural design, refactoring, and code generation across all development tasks. All AI agents and software engineers must adhere to these guidelines to maintain high software quality, clarity, and maintainability.

---

## 1. Core Principles: SOLID in Modern Python

Modern Python emphasizes clarity, duck typing, and pragmatic object orientation. Apply the SOLID principles with Pythonic elegance:

### S — Single Responsibility Principle (SRP)
- Every class, module, and function should have one, and only one, reason to change.
- Separate business domain logic from I/O, presentation, networking, and persistence.
- Keep functions small and cohesive: a function should do one thing well.

### O — Open/Closed Principle (OCP)
- Software entities should be open for extension, but closed for modification.
- Favor polymorphism, dependency injection, and abstract protocols (`typing.Protocol` or `abc.ABC`) over editing core algorithms when introducing new variations.
- Avoid large chains of `if/elif` statements checking type or strategy markers; dispatch via polymorphic strategies or registry lookups instead.

### L — Liskov Substitution Principle (LSP)
- Subtypes must be substitutable for their base types without altering program correctness.
- Subclasses and protocol implementations must adhere to the expected input contracts, return types, and side-effect guarantees of the abstraction.
- Never weaken preconditions or strengthen postconditions in subclasses.

### I — Interface Segregation Principle (ISP)
- Clients should not be forced to depend on methods they do not use.
- Prefer multiple, narrow, focused interfaces/protocols over a single fat interface.
- In Python, use lightweight `typing.Protocol` classes containing only the required methods (e.g., `Reader`, `Writer`, `Closeable`).

### D — Dependency Inversion Principle (DIP)
- High-level modules should not depend on low-level modules; both should depend on abstractions.
- Abstractions should not depend on details; details should depend on abstractions.
- Inject dependencies (database clients, loggers, external APIs) through constructors or factory functions rather than hard-coding concrete instances.

---

## 2. High Cohesion & Loose Coupling

Architectural quality is measured by cohesion within modules and coupling between modules:

### High Cohesion
- Code that changes together should live together.
- A cohesive module focuses entirely on a single bounded domain concept.
- If a class requires fields that are only used by a subset of its methods, decompose the class into smaller, more cohesive units.

### Loose Coupling
- Minimize cross-module knowledge and direct dependencies.
- Communicate between distinct boundaries using well-defined data structures (`dataclass`, typed dictionaries) and abstract interfaces.
- Avoid circular imports, tight temporal coupling (e.g., must call `init()`, then `configure()`, then `start()` without compile/runtime enforcement), and leaking internal representations.

---

## 3. Design Patterns: When to Apply and When to Avoid

Design Patterns represent battle-tested solutions to recurring architectural tensions. However, uncritical pattern application leads to premature abstraction and excessive indirection.

### Pragmatic Use of Design Patterns
- Consult the 22 Gang of Four (GoF) patterns cataloged in this repository via the CLI (`bin/pat` or `pat`).
- **Use Creational Patterns** (Factory Method, Abstract Factory, Builder, Prototype, Singleton):
  - When object creation involves complex rules, multi-step construction, or dynamic family selection.
- **Use Structural Patterns** (Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy):
  - When organizing relationships between classes, adapting third-party libraries, or simplifying subsystem interfaces.
- **Use Behavioral Patterns** (Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor):
  - When distributing responsibilities, decoupling senders from receivers, or managing algorithmic state transitions.

### Enforce YAGNI and KISS (Anti-Over-Engineering)
- **YAGNI (You Aren't Gonna Need It)**:
  - Never design for hypothetical future requirements. Solve the concrete problem in front of you.
  - Do NOT build an Abstract Factory if there is only one product family.
  - Do NOT create a State machine hierarchy if an enum with two states in a dataclass suffices.
- **KISS (Keep It Simple, Stupid)**:
  - Python features first-class functions: a function passed as an argument is often cleaner and faster than a full Strategy class hierarchy.
  - Python dictionary lookups (`actions.get(key, default)()`) are frequently preferable to an elaborate Chain of Responsibility or Command hierarchy for simple dispatching.
  - Use context managers (`contextlib.contextmanager` or `__enter__`/`__exit__`) for resource lifecycle rather than manual Proxy or Manager hierarchies.
- **Rule of Three**:
  - Do not abstract on the first or second occurrence of a pattern. Refactor on the third occurrence when the true variation axis is clear.

---

## 4. When and How to Refactor

Refactoring improves internal structure without altering external observable behavior.

### Recognize Common Code Smells
1. **Long Parameter Lists**: Bundle related parameters into a domain `dataclass`.
2. **Feature Envy**: A method that accesses more data of another object than its own belongs on that other object.
3. **Divergent Change**: A class frequently modified for different reasons violates SRP. Split it.
4. **Shotgun Surgery**: A single business requirement change forces edits across multiple unrelated files. Consolidate responsibility.
5. **Primitive Obsession**: Using raw strings and ints for domain identifiers (e.g., currency, order IDs). Wrap them in value objects or typed newtypes.

### Refactoring Protocol for Agents
1. **Ensure Comprehensive Test Coverage**: Never refactor without passing automated tests acting as a safety net.
2. **Make Small, Incremental Steps**: Run tests after each transformation.
3. **Separate Refactoring from Feature Additions**: Do not mix structural reorganization with new functional behavior in the same commit.
4. **Boy Scout Rule**: Always leave the codebase cleaner than you found it.

---

## 5. Tooling Integration

When evaluating or generating patterns:
- Run `bin/pat recommend -q "<tension>"` to find the most fitting pattern.
- Run `bin/pat show <pattern-id> --json` to inspect canonical structure.
- Run `bin/pat scaffold <pattern-id> --out <path>` to generate a clean foundation.
