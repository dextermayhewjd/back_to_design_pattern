"""Bridge Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Bridge - Conceptual Example
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

REALWORLD_CODE = '''"""
Bridge - Real-World Example: Remotes and Devices
"""
from abc import ABC, abstractmethod


class Device(ABC):
    @abstractmethod
    def is_enabled(self) -> bool:
        pass

    @abstractmethod
    def enable(self) -> None:
        pass

    @abstractmethod
    def disable(self) -> None:
        pass

    @abstractmethod
    def get_volume(self) -> int:
        pass

    @abstractmethod
    def set_volume(self, percent: int) -> None:
        pass


class Radio(Device):
    def __init__(self) -> None:
        self._on: bool = False
        self._volume: int = 30

    def is_enabled(self) -> bool:
        return self._on

    def enable(self) -> None:
        self._on = True

    def disable(self) -> None:
        self._on = False

    def get_volume(self) -> int:
        return self._volume

    def set_volume(self, percent: int) -> None:
        self._volume = max(0, min(100, percent))


class TV(Device):
    def __init__(self) -> None:
        self._on: bool = False
        self._volume: int = 50

    def is_enabled(self) -> bool:
        return self._on

    def enable(self) -> None:
        self._on = True

    def disable(self) -> None:
        self._on = False

    def get_volume(self) -> int:
        return self._volume

    def set_volume(self, percent: int) -> None:
        self._volume = max(0, min(100, percent))


class RemoteControl:
    def __init__(self, device: Device) -> None:
        self.device = device

    def toggle_power(self) -> str:
        if self.device.is_enabled():
            self.device.disable()
            return "Device turned OFF"
        else:
            self.device.enable()
            return "Device turned ON"

    def volume_up(self) -> str:
        self.device.set_volume(self.device.get_volume() + 10)
        return f"Volume set to {self.device.get_volume()}%"


class AdvancedRemoteControl(RemoteControl):
    def mute(self) -> str:
        self.device.set_volume(0)
        return "Device muted"


if __name__ == "__main__":
    tv = TV()
    remote = AdvancedRemoteControl(tv)
    print(remote.toggle_power())
    print(remote.volume_up())
    print(remote.mute())
'''

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
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
