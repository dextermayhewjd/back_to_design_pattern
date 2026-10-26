"""Command Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Command - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass


class SimpleCommand(Command):
    def __init__(self, payload: str) -> None:
        self._payload = payload

    def execute(self) -> None:
        print(f"SimpleCommand: See, I can do simple things like printing ({self._payload})")


class Receiver:
    def do_something(self, a: str) -> None:
        print(f"Receiver: Working on ({a}.)")

    def do_something_else(self, b: str) -> None:
        print(f"Receiver: Also working on ({b}.)")


class ComplexCommand(Command):
    def __init__(self, receiver: Receiver, a: str, b: str) -> None:
        self._receiver = receiver
        self._a = a
        self._b = b

    def execute(self) -> None:
        print("ComplexCommand: Complex stuff should be done by a receiver object")
        self._receiver.do_something(self._a)
        self._receiver.do_something_else(self._b)


class Invoker:
    _on_start: Command | None = None
    _on_finish: Command | None = None

    def set_on_start(self, command: Command) -> None:
        self._on_start = command

    def set_on_finish(self, command: Command) -> None:
        self._on_finish = command

    def do_something_important(self) -> None:
        print("Invoker: Does anybody want something done before I begin?")
        if self._on_start:
            self._on_start.execute()

        print("Invoker: ...doing something really important...")

        print("Invoker: Does anybody want something done after I finish?")
        if self._on_finish:
            self._on_finish.execute()


if __name__ == "__main__":
    invoker = Invoker()
    invoker.set_on_start(SimpleCommand("Say Hi!"))
    receiver = Receiver()
    invoker.set_on_finish(ComplexCommand(receiver, "Send email", "Save report"))

    invoker.do_something_important()
'''

PYTHON310_CODE = '''"""
Command - Python 3.10+ Example: Dataclass Command with Callable & Undo Stack
"""
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class Command:
    execute: Callable[[], None]
    undo: Callable[[], None]
    description: str = ""


class Canvas:
    def __init__(self) -> None:
        self.elements: list[str] = []

    def draw(self, shape: str) -> Command:
        def do() -> None:
            self.elements.append(shape)

        def undo() -> None:
            if self.elements:
                self.elements.pop()

        return Command(execute=do, undo=undo, description=f"Draw {shape}")


@dataclass
class CommandManager:
    _history: list[Command] = field(default_factory=list)

    def execute(self, cmd: Command) -> None:
        cmd.execute()
        self._history.append(cmd)

    def undo(self) -> str | None:
        if not self._history:
            return None
        cmd = self._history.pop()
        cmd.undo()
        return cmd.description


if __name__ == "__main__":
    canvas = Canvas()
    mgr = CommandManager()

    mgr.execute(canvas.draw("Circle"))
    mgr.execute(canvas.draw("Square"))
    print(f"Canvas: {canvas.elements}")

    undone = mgr.undo()
    print(f"Undone: {undone}, Canvas now: {canvas.elements}")
'''

PYTHON312_CODE = '''"""
Command - Python 3.12+ Example: PEP 695 Generic Command & typing.Self
"""
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Action[T]:
    payload: T
    forward: Callable[[T], None]
    backward: Callable[[T], None]

    def apply(self) -> None:
        self.forward(self.payload)

    def revert(self) -> None:
        self.backward(self.payload)


class TextBuffer:
    def __init__(self) -> None:
        self.content: list[str] = []

    def make_append_action(self, text: str) -> Action[str]:
        return Action(
            payload=text,
            forward=lambda t: self.content.append(t),
            backward=lambda _: self.content.pop() if self.content else None,
        )


if __name__ == "__main__":
    buf = TextBuffer()
    act = buf.make_append_action("Hello Python 3.12")
    act.apply()
    print(f"Buffer: {buf.content}")
    act.revert()
    print(f"Buffer after revert: {buf.content}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Single-method Command classes (Java in Python) implementing execute() and undo().",
    "3.10": "Replaced Command classes with first-class Callables and lightweight dataclass Command closures.",
    "3.12": "Type-safe generic command encapsulation Action[T] with PEP 695 type parameters.",
}

SCAFFOLD_TEMPLATE = '''"""
Command Scaffolding Template
"""
from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass


class ConcreteCommand(Command):
    def __init__(self, receiver: object) -> None:
        self.receiver = receiver

    def execute(self) -> None:
        print("Command executed")

    def undo(self) -> None:
        print("Command undone")
'''

PATTERN = Pattern(
    id="command",
    name="Command",
    chinese_name="命令",
    category=Category.BEHAVIORAL,
    intent="将一个请求封装为一个对象，从而使你可用不同的请求对客户进行参数化；对请求排队或记录请求日志，以及支持可撤销的操作。",
    problem="如果用户界面按钮、菜单栏、快捷键直接调用具体的业务逻辑函数，会导致触发端（Invoker）与业务执行端（Receiver）强耦合，且无法实现统一的操作历史撤销、宏命令录制以及请求队列重试。",
    solution="将请求的所有相关细节（接收者对象、方法名以及参数）提取到一个单独的命令类（Command）中，通过统一的 `execute()` 接口调用，将发送者与接收者彻底解耦。",
    applicability=[
        "需要通过操作来参数化对象时（例如将回调函数封装为可传递的命令对象）",
        "需要将操作放入队列中、操作的执行或者远程执行时",
        "需要实现操作的撤销（Undo）与重做（Redo）功能时",
    ],
    symptoms=[
        "undo/redo action history",
        "queue requests for background worker execution",
        "decouple button/UI action from business logic",
        "macro recording of multi-step operations",
    ],
    pros=[
        "单一职责原则：可以将触发操作的类和执行操作的类解耦",
        "开闭原则：可以在不修改现有客户端代码的情况下创建新命令",
        "可以实现撤销和恢复功能",
        "可以实现操作的延迟执行或队列化调度",
    ],
    cons=[
        "代码可能会变得更繁琐，因为在发送者和接收者之间增加了一个全新的中间命令层",
    ],
    relations=[
        "与备忘录（Memento）：命令通常负责执行和记录状态变更，备忘录保存状态快照以支持撤销",
        "与策略（Strategy）：策略通常用来描述实现同一件事的不同算法；命令通常将一个特定行为封装为对象",
        "与责任链（Chain of Responsibility）：责任链的各个环节可以执行传入的命令",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
