"""Memento Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Memento - Conceptual Example
"""
from abc import ABC, abstractmethod
from datetime import datetime


class Memento(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_date(self) -> str:
        pass


class ConcreteMemento(Memento):
    def __init__(self, state: str) -> None:
        self._state = state
        self._date = str(datetime.now())[:19]

    def get_state(self) -> str:
        return self._state

    def get_name(self) -> str:
        return f"{self._date} / ({self._state[0:9]}...)"

    def get_date(self) -> str:
        return self._date


class Originator:
    _state: str = ""

    def __init__(self, state: str) -> None:
        self._state = state
        print(f"Originator: My initial state is: {self._state}")

    def do_something(self) -> None:
        print("Originator: I'm doing something important.")
        self._state = f"State_{datetime.now().microsecond}"
        print(f"Originator: and my state has changed to: {self._state}")

    def save(self) -> Memento:
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento) -> None:
        assert isinstance(memento, ConcreteMemento)
        self._state = memento.get_state()
        print(f"Originator: My state has changed to: {self._state}")


class Caretaker:
    def __init__(self, originator: Originator) -> None:
        self._mementos: list[Memento] = []
        self._originator = originator

    def backup(self) -> None:
        print("\\nCaretaker: Saving Originator's state...")
        self._mementos.append(self._originator.save())

    def undo(self) -> None:
        if not self._mementos:
            return
        memento = self._mementos.pop()
        print(f"Caretaker: Restoring state to: {memento.get_name()}")
        try:
            self._originator.restore(memento)
        except Exception:
            self.undo()


if __name__ == "__main__":
    originator = Originator("Super-duper-super-puper-super.")
    caretaker = Caretaker(originator)

    caretaker.backup()
    originator.do_something()

    caretaker.backup()
    originator.do_something()

    caretaker.undo()
    caretaker.undo()
'''

REALWORLD_CODE = '''"""
Memento - Real-World Example: Canvas Shape State Rollback
"""
import copy


class CanvasState:
    def __init__(self, shapes: list[str], zoom: float) -> None:
        self.shapes = copy.deepcopy(shapes)
        self.zoom = zoom


class GraphicCanvas:
    def __init__(self) -> None:
        self.shapes: list[str] = []
        self.zoom: float = 1.0

    def add_shape(self, shape: str) -> None:
        self.shapes.append(shape)

    def create_snapshot(self) -> CanvasState:
        return CanvasState(self.shapes, self.zoom)

    def restore(self, state: CanvasState) -> None:
        self.shapes = copy.deepcopy(state.shapes)
        self.zoom = state.zoom


if __name__ == "__main__":
    canvas = GraphicCanvas()
    canvas.add_shape("Circle")
    snapshot = canvas.create_snapshot()

    canvas.add_shape("Rectangle")
    print("Shapes after edit:", canvas.shapes)

    canvas.restore(snapshot)
    print("Shapes after rollback:", canvas.shapes)
'''

SCAFFOLD_TEMPLATE = '''"""
Memento Scaffolding Template
"""


class Memento:
    def __init__(self, state: dict) -> None:
        self._state = state

    def get_state(self) -> dict:
        return self._state


class Originator:
    def __init__(self) -> None:
        self.state: dict = {}

    def save(self) -> Memento:
        return Memento(dict(self.state))

    def restore(self, memento: Memento) -> None:
        self.state = memento.get_state()
'''

PATTERN = Pattern(
    id="memento",
    name="Memento",
    chinese_name="备忘录",
    category=Category.BEHAVIORAL,
    intent="在不破坏封装性的前提下，捕获一个对象的内部状态，并在该对象之外保存这个状态，以便以后当需要时能将该对象恢复到原先保存的状态。",
    problem="直接从外部复制对象的状态进行快照会导致对象的私有字段被迫暴露给外部管理者，彻底破坏面向对象的封装性。",
    solution="将快照生成的职责委托给原发器（Originator）自身。原发器将自身状态序列化进备忘录（Memento）对象中，管理者（Caretaker）仅持有备忘录引用，无法查看或修改其内部私有状态。",
    applicability=[
        "当你需要创建对象状态快照来恢复其之前的状态时（例如撤销操作）",
        "当直接访问对象的成员变量、获取器或设置器导致封装原则被破坏时",
    ],
    symptoms=[
        "state snapshot and restore",
        "undo history without exposing private state",
        "rollback to previous checkpoint",
        "transactions / savepoints",
    ],
    pros=[
        "可以在不破坏对象封装性的前提下创建对象状态快照",
        "可以通过让负责人维护原发器状态历史记录来简化原发器代码",
    ],
    cons=[
        "如果客户端频繁创建备忘录，程序可能会消耗大量的内存",
        "负责人必须完整跟踪原发器的生命周期，以便能够销毁过期的备忘录",
    ],
    relations=[
        "与命令（Command）：命令模式常与备忘录配合使用，命令执行状态变化前生成备忘录用于撤销操作",
        "与原型（Prototype）：原型的重点在于完整克隆可独立运行的新对象；备忘录仅用于保存和恢复历史快照",
    ],
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
