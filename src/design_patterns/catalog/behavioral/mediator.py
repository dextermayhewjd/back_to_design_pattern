"""Mediator Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Mediator - Conceptual Example
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

REALWORLD_CODE = '''"""
Mediator - Real-World Example: UI Dialog Component Coordinator
"""
from abc import ABC, abstractmethod


class DialogMediator(ABC):
    @abstractmethod
    def notify(self, sender: str, event: str) -> None:
        pass


class AuthenticationDialog(DialogMediator):
    def __init__(self) -> None:
        self.is_registration: bool = False
        self.username: str = ""
        self.password: str = ""
        self.remember_me: bool = False

    def notify(self, sender: str, event: str) -> None:
        if sender == "toggle_register":
            self.is_registration = (event == "checked")
            print(f"[Dialog] Switched mode: {'Registration' if self.is_registration else 'Login'}")
        elif sender == "submit_button" and event == "clicked":
            action = "Registering user" if self.is_registration else "Logging in user"
            print(f"[Dialog] Executing {action} with credentials...")


if __name__ == "__main__":
    auth_form = AuthenticationDialog()
    auth_form.notify("toggle_register", "checked")
    auth_form.notify("submit_button", "clicked")
'''

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
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
