"""Observer Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Observer - Conceptual Example
"""
from abc import ABC, abstractmethod
from random import randrange
from typing import Any


class Subject(ABC):
    @abstractmethod
    def attach(self, observer: "Observer") -> None:
        pass

    @abstractmethod
    def detach(self, observer: "Observer") -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass


class ConcreteSubject(Subject):
    _state: int = 0
    _observers: list["Observer"] = []

    def attach(self, observer: "Observer") -> None:
        print("Subject: Attached an observer.")
        self._observers.append(observer)

    def detach(self, observer: "Observer") -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        print("Subject: Notifying observers...")
        for observer in self._observers:
            observer.update(self)

    def some_business_logic(self) -> None:
        print("\\nSubject: I'm doing something important.")
        self._state = randrange(0, 10)
        print(f"Subject: My state has just changed to: {self._state}")
        self.notify()


class Observer(ABC):
    @abstractmethod
    def update(self, subject: Subject) -> None:
        pass


class ConcreteObserverA(Observer):
    def update(self, subject: Subject) -> None:
        assert isinstance(subject, ConcreteSubject)
        if subject._state < 3:
            print("ConcreteObserverA: Reacted to the event")


class ConcreteObserverB(Observer):
    def update(self, subject: Subject) -> None:
        assert isinstance(subject, ConcreteSubject)
        if subject._state == 0 or subject._state >= 2:
            print("ConcreteObserverB: Reacted to the event")


if __name__ == "__main__":
    subject = ConcreteSubject()
    observer_a = ConcreteObserverA()
    subject.attach(observer_a)

    observer_b = ConcreteObserverB()
    subject.attach(observer_b)

    subject.some_business_logic()
    subject.some_business_logic()

    subject.detach(observer_a)
    subject.some_business_logic()
'''

REALWORLD_CODE = '''"""
Observer - Real-World Example: Event Dispatcher & Notification Bus
"""
from collections import defaultdict
from collections.abc import Callable
from typing import Any


class EventManager:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_type: str, listener: Callable[[Any], None]) -> None:
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: str, listener: Callable[[Any], None]) -> None:
        if listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)

    def notify(self, event_type: str, data: Any) -> None:
        for listener in self._listeners[event_type]:
            listener(data)


if __name__ == "__main__":
    bus = EventManager()

    def email_notifier(user: str) -> None:
        print(f"[Email Service] Sending welcome email to: {user}")

    def audit_logger(user: str) -> None:
        print(f"[Audit Log] User registered in DB: {user}")

    bus.subscribe("user_registered", email_notifier)
    bus.subscribe("user_registered", audit_logger)

    bus.notify("user_registered", "alice@example.com")
'''

SCAFFOLD_TEMPLATE = '''"""
Observer Scaffolding Template
"""
from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, message: str) -> None:
        pass


class Subject:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def notify(self, message: str) -> None:
        for obs in self._observers:
            obs.update(message)
'''

PATTERN = Pattern(
    id="observer",
    name="Observer",
    chinese_name="观察者",
    category=Category.BEHAVIORAL,
    intent="定义对象间的一种一对多的依赖关系，当一个对象的状态发生改变时，所有依赖于它的对象都得到通知并被自动更新。",
    problem="当一个主对象的状态发生改变时，其他相关联的组件需要随之执行更新；若主对象直接维护外部依赖列表，将导致主对象与具体订阅者严重紧密耦合。",
    solution="声明通用的发布者接口（Subject）和订阅者接口（Observer）。发布者提供注册、注销和通知接口，内部维护观察者列表；当事件发生时，遍历通知所有已注册的观察者。",
    applicability=[
        "当一个对象状态的改变需要改变其他对象，或实际对象数量未知、动态变化时",
        "当应用中的一些对象必须观察其他对象，但仅在特定条件下或有限时间内进行观察时",
    ],
    symptoms=[
        "1-to-many event notification",
        "publish/subscribe mechanism",
        "event listener registration",
        "loosely coupled UI event handling",
    ],
    pros=[
        "开闭原则：你无需修改发布者代码就能引入新的订阅者类（反之亦然）",
        "可以在运行时建立对象之间的依赖关系",
    ],
    cons=[
        "订阅者的通知顺序通常是随机的",
        "如果订阅者未及时解绑，可能会导致内存泄漏（失落的监听器问题）",
    ],
    relations=[
        "与中介者（Mediator）：中介者集中消解双向通信，而观察者模式专注于单向从发布者到多个观察者的动态广播",
    ],
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
