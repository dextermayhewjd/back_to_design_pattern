"""Decorator Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Decorator - Conceptual Example
"""


class Component:
    def operation(self) -> str:
        return "ConcreteComponent"


class Decorator(Component):
    def __init__(self, component: Component) -> None:
        self._component = component

    @property
    def component(self) -> Component:
        return self._component

    def operation(self) -> str:
        return self._component.operation()


class ConcreteDecoratorA(Decorator):
    def operation(self) -> str:
        return f"ConcreteDecoratorA({self.component.operation()})"


class ConcreteDecoratorB(Decorator):
    def operation(self) -> str:
        return f"ConcreteDecoratorB({self.component.operation()})"


def client_code(component: Component) -> str:
    return f"RESULT: {component.operation()}"


if __name__ == "__main__":
    simple = Component()
    print("Client: I've got a simple component:")
    print(client_code(simple))

    decorator1 = ConcreteDecoratorA(simple)
    decorator2 = ConcreteDecoratorB(decorator1)
    print("\\nClient: Now I've got a decorated component:")
    print(client_code(decorator2))
'''

REALWORLD_CODE = '''"""
Decorator - Real-World Example: Data Stream Compression & Encryption
"""
from abc import ABC, abstractmethod


class DataSource(ABC):
    @abstractmethod
    def write_data(self, data: str) -> None:
        pass

    @abstractmethod
    def read_data(self) -> str:
        pass


class MemoryDataSource(DataSource):
    def __init__(self) -> None:
        self._data: str = ""

    def write_data(self, data: str) -> None:
        self._data = data

    def read_data(self) -> str:
        return self._data


class DataSourceDecorator(DataSource):
    def __init__(self, source: DataSource) -> None:
        self._wrappee = source

    def write_data(self, data: str) -> None:
        self._wrappee.write_data(data)

    def read_data(self) -> str:
        return self._wrappee.read_data()


class EncryptionDecorator(DataSourceDecorator):
    def write_data(self, data: str) -> None:
        encrypted = f"ENCRYPTED({data})"
        super().write_data(encrypted)

    def read_data(self) -> str:
        raw = super().read_data()
        return raw.replace("ENCRYPTED(", "").rstrip(")")


class CompressionDecorator(DataSourceDecorator):
    def write_data(self, data: str) -> None:
        compressed = f"COMPRESSED({data})"
        super().write_data(compressed)

    def read_data(self) -> str:
        raw = super().read_data()
        return raw.replace("COMPRESSED(", "").rstrip(")")


if __name__ == "__main__":
    source = MemoryDataSource()
    secured = CompressionDecorator(EncryptionDecorator(source))
    secured.write_data("Secret payroll records")
    print("Underlying storage:", source.read_data())
    print("Decoded through stack:", secured.read_data())
'''

SCAFFOLD_TEMPLATE = '''"""
Decorator Scaffolding Template
"""
from abc import ABC, abstractmethod


class Component(ABC):
    @abstractmethod
    def execute(self) -> str:
        pass


class BaseDecorator(Component):
    def __init__(self, component: Component) -> None:
        self._component = component

    def execute(self) -> str:
        return self._component.execute()


class ExtraBehaviorDecorator(BaseDecorator):
    def execute(self) -> str:
        base_result = super().execute()
        return f"{base_result} + extra behavior"
'''

PATTERN = Pattern(
    id="decorator",
    name="Decorator",
    chinese_name="装饰",
    category=Category.STRUCTURAL,
    intent="允许向一个现有的对象添加新的功能，同时又不改变其结构，通过将对象放入包含新行为的包装对象中来实现。",
    problem="如果采用继承来扩展对象行为，类继承是在编译时静态绑定的，子类无法在运行时动态添加或移除功能，且不同特性的任意排列组合会导致子类数量爆炸。",
    solution="将目标对象放置在包装器（Decorator）对象中。包装器实现与目标对象相同的接口，并在委派目标对象方法前后添加自身特定的行为。",
    applicability=[
        "在无需修改代码的情况下即可使用对象，且希望在运行时为对象新增额外行为时",
        "如果用继承来扩展对象行为的方案难以实现或者根本不可行时",
    ],
    symptoms=[
        "dynamically attach extra responsibilities",
        "wrapping object behavior",
        "combinatorial explosion of subclasses for feature variants",
        "runtime feature composition",
    ],
    pros=[
        "无需创建新子类即可扩展对象的行为",
        "可以在运行时添加或删除职责",
        "用多个装饰封装对象来组合几种行为",
        "单一职责原则：可以将大类中各个不同职责拆分为小类",
    ],
    cons=[
        "在装饰栈中删除特定装饰器比较困难",
        "代码的外观会充满大量小类，配置和调试排查调用栈相对复杂",
    ],
    relations=[
        "与适配器（Adapter）：适配器改变已有对象的接口，装饰增强对象功能且不改变其接口",
        "与代理（Proxy）：装饰与代理结构相似，但目的不同：装饰增强服务功能，代理控制对服务的访问与生命周期",
        "与责任链（Chain of Responsibility）：两者均基于递归组合，但责任链按需中断传递，装饰器通常透明全链执行",
    ],
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
