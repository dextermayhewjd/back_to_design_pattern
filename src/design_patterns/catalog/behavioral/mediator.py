"""Mediator Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Mediator - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod


class Mediator(ABC):
    @abstractmethod
    def notify(self, sender: object, event: str) -> None:
        pass


class BaseComponent:
    def __init__(self, mediator: Mediator | None = None) -> None:
        self._mediator = mediator

    @property
    def mediator(self) -> Mediator:
        assert self._mediator is not None
        return self._mediator

    @mediator.setter
    def mediator(self, mediator: Mediator) -> None:
        self._mediator = mediator


class Component1(BaseComponent):
    def do_a(self) -> None:
        print("Component 1 does A.")
        self.mediator.notify(self, "A")

    def do_b(self) -> None:
        print("Component 1 does B.")
        self.mediator.notify(self, "B")


class Component2(BaseComponent):
    def do_c(self) -> None:
        print("Component 2 does C.")
        self.mediator.notify(self, "C")

    def do_d(self) -> None:
        print("Component 2 does D.")
        self.mediator.notify(self, "D")


class ConcreteMediator(Mediator):
    def __init__(self, c1: Component1, c2: Component2) -> None:
        self._c1 = c1
        self._c1.mediator = self
        self._c2 = c2
        self._c2.mediator = self

    def notify(self, sender: object, event: str) -> None:
        if event == "A":
            print("Mediator reacts on A and triggers following operations:")
            self._c2.do_c()
        elif event == "D":
            print("Mediator reacts on D and triggers following operations:")
            self._c1.do_b()
            self._c2.do_c()


if __name__ == "__main__":
    c1 = Component1()
    c2 = Component2()
    mediator = ConcreteMediator(c1, c2)

    print("Client triggers operation A.")
    c1.do_a()

    print("\\nClient triggers operation D.")
    c2.do_d()
'''

PYTHON310_CODE = '''"""
Mediator - Python 3.10+ Example: Event-Driven Hub with Match-Case
"""
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Event:
    topic: str
    sender: str
    data: dict[str, str] = field(default_factory=dict)


class EventMediator:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[[Event], None]]] = {}

    def subscribe(self, topic: str, listener: Callable[[Event], None]) -> None:
        self._listeners.setdefault(topic, []).append(listener)

    def publish(self, event: Event) -> None:
        match event.topic:
            case "auth:login":
                print(f"[Mediator Audit] User login triggered by {event.sender}")
            case "cart:checkout":
                print(f"[Mediator Audit] Checkout initiated with items {event.data}")
            case _:
                pass

        for listener in self._listeners.get(event.topic, []):
            listener(event)


if __name__ == "__main__":
    hub = EventMediator()
    hub.subscribe("cart:checkout", lambda e: print(f"Inventory reserve notified: {e.data}"))
    hub.publish(Event(topic="cart:checkout", sender="WebClient", data={"sku": "PROD-1", "qty": "2"}))
'''

PYTHON312_CODE = '''"""
Mediator - Python 3.12+ Example: PEP 695 Generic Event Mediator
"""
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class UIAction:
    widget_id: str
    payload: str


class Mediator[Msg]:
    def __init__(self) -> None:
        self._handlers: list[Callable[[Msg], None]] = []

    def register(self, handler: Callable[[Msg], None]) -> None:
        self._handlers.append(handler)

    def broadcast(self, message: Msg) -> None:
        for handler in self._handlers:
            handler(message)


if __name__ == "__main__":
    mediator: Mediator[UIAction] = Mediator()
    mediator.register(lambda a: print(f"Handler 1 received action from {a.widget_id}: {a.payload}"))
    mediator.register(lambda a: print(f"Handler 2 logging {a.payload}"))
    mediator.broadcast(UIAction("btn_submit", "Click event triggered"))
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Bi-directional object coupling with abstract Mediator and concrete colleague references.",
    "3.10": "Centralized event hub using frozen dataclass Event and match-case topic routing.",
    "3.12": "Type-safe generic event dispatch hub Mediator[Msg] parameterized with PEP 695.",
}

SCAFFOLD_TEMPLATE = '''"""
Mediator Scaffolding Template
"""
from abc import ABC, abstractmethod


class Mediator(ABC):
    @abstractmethod
    def notify(self, sender: object, event: str) -> None:
        pass


class Colleague:
    def __init__(self, mediator: Mediator) -> None:
        self.mediator = mediator

    def send(self, event: str) -> None:
        self.mediator.notify(self, event)
'''

PATTERN = Pattern(
    id="mediator",
    name="Mediator",
    chinese_name="中介者",
    category=Category.BEHAVIORAL,
    intent="用一个中介对象来封装一系列的对象交互，中介者使各对象不需要显式地相互引用，从而使其耦合松散，而且可以独立地改变它们之间的交互。",
    problem="当多个对象之间存在复杂的网状交叉引用（例如表单中的各个输入框、校验器、复选框和提交按钮相互依赖），任何组件的小修改都会波及其他组件，导致难以复用。",
    solution="让组件之间不再直接相互调用，而是仅依赖于一个中介者接口（Mediator）。所有相互通信都发送给中介者，由中介者决定通知哪些组件以及调用顺序。",
    applicability=[
        "当一些对象和其他对象紧密耦合以致难以对其进行修改时",
        "当组件因过于依赖其他组件而无法在不同应用中复用时",
        "如果为了在不同情景下复用一些基本行为而导致需要创建大量组件子类时",
    ],
    symptoms=[
        "tight coupling between multiple UI components",
        "spiderweb / mesh of object communications",
        "circular dependencies between collaborating objects",
        "chat room or centralized hub dispatch",
    ],
    pros=[
        "单一职责原则：可以将多个组件间的通信抽取到单一位置，更易于理解和维护",
        "开闭原则：无需修改实际组件就能增加新的中介者",
        "可以减轻应用中多个组件之间的高耦合度",
    ],
    cons=[
        "随着时间推移，中介者很容易演变为无所不知的“上帝对象（God Object）”",
    ],
    relations=[
        "与外观（Facade）：外观通常是单向简化外部对子系统的调用；中介者集中内部组件之间的双向复杂通信",
        "与观察者（Observer）：中介者可以利用观察者模式实现动态订阅与事件通知",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
