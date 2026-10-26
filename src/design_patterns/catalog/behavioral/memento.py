"""Memento Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Memento - Conceptual Example (Classic GoF)
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

PYTHON310_CODE = '''"""
Memento - Python 3.10+ Example: Frozen Dataclass Snapshots
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class EditorSnapshot:
    text: str
    cursor_position: int
    selection_length: int


class TextEditor:
    def __init__(self) -> None:
        self.text: str = ""
        self.cursor: int = 0
        self.selection: int = 0

    def type_text(self, text: str) -> None:
        self.text += text
        self.cursor += len(text)

    def save(self) -> EditorSnapshot:
        return EditorSnapshot(self.text, self.cursor, self.selection)

    def restore(self, snapshot: EditorSnapshot) -> None:
        self.text = snapshot.text
        self.cursor = snapshot.cursor_position
        self.selection = snapshot.selection_length


if __name__ == "__main__":
    editor = TextEditor()
    editor.type_text("Initial text. ")
    saved = editor.save()

    editor.type_text("Draft modifications.")
    print(f"Modified: {editor.text}")

    editor.restore(saved)
    print(f"Restored: {editor.text}")
'''

PYTHON312_CODE = '''"""
Memento - Python 3.12+ Example: PEP 695 Generic Snapshot History
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class GameState:
    level: int
    score: int
    health: int


class History[S]:
    def __init__(self) -> None:
        self._checkpoints: list[S] = []

    def save(self, state: S) -> None:
        self._checkpoints.append(state)

    def rollback(self) -> S | None:
        return self._checkpoints.pop() if self._checkpoints else None


if __name__ == "__main__":
    history: History[GameState] = History()
    current = GameState(level=1, score=100, health=100)
    history.save(current)

    current = GameState(level=2, score=250, health=50)
    print(f"Level 2: {current}")

    prev = history.rollback()
    print(f"Rolled back to: {prev}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Heavy ConcreteMemento class hiding state getters from Caretaker.",
    "3.10": "Zero-overhead snapshots using immutable @dataclass(frozen=True).",
    "3.12": "Type-safe generic checkpoint tracker History[S] using PEP 695.",
}

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
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
