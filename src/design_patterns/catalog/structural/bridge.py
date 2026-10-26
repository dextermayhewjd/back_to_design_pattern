"""Bridge Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Bridge - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod


class Implementation(ABC):
    @abstractmethod
    def operation_implementation(self) -> str:
        pass


class ConcreteImplementationA(Implementation):
    def operation_implementation(self) -> str:
        return "ConcreteImplementationA on platform A."


class ConcreteImplementationB(Implementation):
    def operation_implementation(self) -> str:
        return "ConcreteImplementationB on platform B."


class Abstraction:
    def __init__(self, implementation: Implementation) -> None:
        self.implementation = implementation

    def operation(self) -> str:
        return f"Abstraction: Base operation with:\\n{self.implementation.operation_implementation()}"


class ExtendedAbstraction(Abstraction):
    def operation(self) -> str:
        return f"ExtendedAbstraction: Extended operation with:\\n{self.implementation.operation_implementation()}"


def client_code(abstraction: Abstraction) -> str:
    return abstraction.operation()


if __name__ == "__main__":
    impl_a = ConcreteImplementationA()
    abs_1 = Abstraction(impl_a)
    print(client_code(abs_1))

    impl_b = ConcreteImplementationB()
    abs_2 = ExtendedAbstraction(impl_b)
    print(client_code(abs_2))
'''

PYTHON310_CODE = '''"""
Bridge - Python 3.10+ Example: Protocol Device & Dataclass Controllers
"""
from dataclasses import dataclass
from typing import Protocol


class Device(Protocol):
    def turn_on(self) -> str: ...
    def turn_off(self) -> str: ...
    def set_channel(self, channel: int) -> str: ...


class SmartTV:
    def turn_on(self) -> str:
        return "SmartTV display waking up"

    def turn_off(self) -> str:
        return "SmartTV entering standby"

    def set_channel(self, channel: int) -> str:
        return f"SmartTV streaming channel {channel}"


class Radio:
    def turn_on(self) -> str:
        return "Radio power amp engaged"

    def turn_off(self) -> str:
        return "Radio powered down"

    def set_channel(self, channel: int) -> str:
        return f"Radio tuned to FM {channel}MHz"


@dataclass
class BasicRemote:
    device: Device

    def power(self) -> str:
        return self.device.turn_on()


@dataclass
class VoiceRemote(BasicRemote):
    def voice_command(self, cmd: str) -> str:
        match cmd:
            case "on":
                return self.device.turn_on()
            case "off":
                return self.device.turn_off()
            case _:
                return f"Voice unrecognized: {cmd}"


if __name__ == "__main__":
    tv = SmartTV()
    remote = VoiceRemote(tv)
    print(remote.power())
    print(remote.voice_command("off"))
'''

PYTHON312_CODE = '''"""
Bridge - Python 3.12+ Example: PEP 695 Generic Bridge & @override
"""
from dataclasses import dataclass
from typing import Protocol, override


class RenderBackend(Protocol):
    def draw_primitive(self, name: str) -> str: ...


class VectorRenderer:
    def draw_primitive(self, name: str) -> str:
        return f"Vector drawing of {name}"


class RasterRenderer:
    def draw_primitive(self, name: str) -> str:
        return f"Raster pixels for {name}"


@dataclass
class Shape[R: RenderBackend]:
    renderer: R

    def draw(self) -> str:
        return self.renderer.draw_primitive("generic_shape")


class Circle[R: RenderBackend](Shape[R]):
    @override
    def draw(self) -> str:
        return self.renderer.draw_primitive("circle")


if __name__ == "__main__":
    c = Circle(VectorRenderer())
    print(c.draw())
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Dual abstract inheritance hierarchies for Abstraction and Implementor using abc.ABC.",
    "3.10": "Structural typing with Protocol for implementors and dataclass compositions.",
    "3.12": "PEP 695 type parameters Shape[R: RenderBackend] providing type-safe renderer binding and @override.",
}

SCAFFOLD_TEMPLATE = '''"""
Bridge Scaffolding Template
"""
from abc import ABC, abstractmethod


class Implementor(ABC):
    @abstractmethod
    def execute_low_level(self) -> None:
        pass


class Abstraction:
    def __init__(self, implementor: Implementor) -> None:
        self.implementor = implementor

    def execute_high_level(self) -> None:
        self.implementor.execute_low_level()
'''

PATTERN = Pattern(
    id="bridge",
    name="Bridge",
    chinese_name="桥接",
    category=Category.STRUCTURAL,
    intent="将一个大类或一系列紧密相关的类拆分为抽象和实现两个独立的层次结构，从而能在两个维度上独立扩展。",
    problem="当一个类在多个正交维度上扩展时（例如形状 Shape 和颜色 Color，或者控制端 Remote 与设备 Device），传统继承会导致类数量呈笛卡尔积爆炸式增长（如 RedCircle, BlueCircle, RedSquare 等）。",
    solution="将继承机制替换为组合机制，将其中一个维度抽取为独立的实现层接口（Implementor），抽象层持有该接口的引用并委派具体操作。",
    applicability=[
        "如果你想要拆分或重组一个具有多重维度的庞杂类时",
        "如果你希望在几个独立维度上扩展一个类时",
        "需要在运行时切换不同实现时",
    ],
    symptoms=[
        "cartesian product class explosion",
        "multi-dimensional class hierarchies",
        "tight coupling between abstraction and platform",
        "cross-platform device controllers",
    ],
    pros=[
        "可以创建与平台无关的类和程序",
        "客户端代码仅与高层抽象进行交互，不触及平台细节",
        "开闭原则：可以独立新增抽象和实现",
        "单一职责原则：抽象专注高层逻辑，实现专注底层细节",
    ],
    cons=[
        "对高内聚的类使用该模式可能会使代码变得更加复杂",
    ],
    relations=[
        "与适配器（Adapter）：适配器通常用于后期让不兼容的接口协同，桥接在系统设计前期解耦独立演化维度",
        "与抽象工厂（Abstract Factory）：抽象工厂常与桥接模式结合，负责构建特定的桥接结构",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
