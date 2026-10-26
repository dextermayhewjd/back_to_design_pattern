"""State Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
State - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod


class Context:
    _state: "State | None" = None

    def __init__(self, state: "State") -> None:
        self.transition_to(state)

    def transition_to(self, state: "State") -> None:
        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def request1(self) -> None:
        assert self._state is not None
        self._state.handle1()

    def request2(self) -> None:
        assert self._state is not None
        self._state.handle2()


class State(ABC):
    @property
    def context(self) -> Context:
        assert self._context is not None
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def handle1(self) -> None:
        pass

    @abstractmethod
    def handle2(self) -> None:
        pass


class ConcreteStateA(State):
    def handle1(self) -> None:
        print("ConcreteStateA handles request1.")
        print("ConcreteStateA wants to change the state of the context.")
        self.context.transition_to(ConcreteStateB())

    def handle2(self) -> None:
        print("ConcreteStateA handles request2.")


class ConcreteStateB(State):
    def handle1(self) -> None:
        print("ConcreteStateB handles request1.")

    def handle2(self) -> None:
        print("ConcreteStateB handles request2.")
        print("ConcreteStateB wants to change the state of the context.")
        self.context.transition_to(ConcreteStateA())


if __name__ == "__main__":
    context = Context(ConcreteStateA())
    context.request1()
    context.request2()
'''

PYTHON310_CODE = '''"""
State - Python 3.10+ Example: Enum & Pattern-Matching State Transitions
"""
from dataclasses import dataclass
from enum import Enum, auto


class State(Enum):
    DRAFT = auto()
    IN_REVIEW = auto()
    PUBLISHED = auto()


@dataclass
class Document:
    title: str
    state: State = State.DRAFT

    def publish(self) -> str:
        match self.state:
            case State.DRAFT:
                self.state = State.IN_REVIEW
                return f"'{self.title}' submitted for review"
            case State.IN_REVIEW:
                self.state = State.PUBLISHED
                return f"'{self.title}' published successfully"
            case State.PUBLISHED:
                return f"'{self.title}' is already published"


if __name__ == "__main__":
    doc = Document("Design Patterns in Python 3.10")
    print(doc.publish())
    print(doc.publish())
    print(doc.publish())
'''

PYTHON312_CODE = '''"""
State - Python 3.12+ Example: PEP 695 Generic Finite State Machine
"""
from typing import Self

type TransitionTable[S, E] = dict[tuple[S, E], S]


class StateMachine[S, E]:
    def __init__(self, initial_state: S, transitions: TransitionTable[S, E]) -> None:
        self.state = initial_state
        self._transitions = transitions

    def trigger(self, event: E) -> Self:
        key = (self.state, event)
        if key in self._transitions:
            self.state = self._transitions[key]
        else:
            raise ValueError(f"Invalid transition from {self.state} with event {event}")
        return self


if __name__ == "__main__":
    table: TransitionTable[str, str] = {
        ("locked", "coin"): "unlocked",
        ("unlocked", "push"): "locked",
    }
    turnstile = StateMachine("locked", table)
    turnstile.trigger("coin")
    print(f"State after coin: {turnstile.state}")
    turnstile.trigger("push")
    print(f"State after push: {turnstile.state}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Object-oriented state hierarchy with circular Context <-> State pointers.",
    "3.10": "Clean state transitions using Python 3.10 match-case on state Enums and dataclasses.",
    "3.12": "Generic table-driven state machine StateMachine[S, E] parameterized via PEP 695.",
}

SCAFFOLD_TEMPLATE = '''"""
State Scaffolding Template
"""
from abc import ABC, abstractmethod


class Context:
    def __init__(self, initial_state: "State") -> None:
        self.state = initial_state

    def change_state(self, state: "State") -> None:
        self.state = state

    def do_action(self) -> None:
        self.state.handle(self)


class State(ABC):
    @abstractmethod
    def handle(self, context: Context) -> None:
        pass
'''

PATTERN = Pattern(
    id="state",
    name="State",
    chinese_name="状态",
    category=Category.BEHAVIORAL,
    intent="允许一个对象在其内部状态改变时改变它的行为。对象看起来似乎修改了它的类。",
    problem="当一个对象的行为严重取决于其当前状态（例如订单状态机、文档流转审批、网络连接状态），如果在方法中大量使用 `if (state == A) ... else if (state == B)` 分支语句，随着新状态增加，条件逻辑将变得难以理解与维护。",
    solution="将所有与特定状态相关的逻辑分别抽取为一个个独立的状态类（State）。主上下文（Context）持有当前状态对象的引用，并将所有状态相关的请求委派给当前状态对象执行；状态转换也可以在状态类内部触发。",
    applicability=[
        "对象需要根据自身当前状态进行不同行为，同时状态数量非常多且状态代码经常改变时",
        "某个类需要根据属性值进行大量条件语句分支判断时",
        "当相似状态和基于条件的状态转换中存在许多重复代码时",
    ],
    symptoms=[
        "giant switch-case on internal state enum",
        "state machine transition logic",
        "object behavior morphs based on mode/status",
        "order or ticket status workflows",
    ],
    pros=[
        "单一职责原则：将与特定状态相关的代码组织进独立的类中",
        "开闭原则：无需修改已有状态类和上下文即可引入新状态",
        "消除庞大的条件状态机分支语句",
    ],
    cons=[
        "如果状态机只有很少的几个状态或者很少改变，应用该模式可能会显得小题大做",
    ],
    relations=[
        "与策略（Strategy）：状态可以被视为策略模式的扩展，区别在于状态模式中的各个状态对象之间彼此知晓并可以主动触发状态转移，而策略对象通常彼此独立且对上下文无感知",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
