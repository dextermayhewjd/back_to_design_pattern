"""Abstract Factory Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Abstract Factory - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod


class AbstractProductA(ABC):
    @abstractmethod
    def useful_function_a(self) -> str:
        pass


class ConcreteProductA1(AbstractProductA):
    def useful_function_a(self) -> str:
        return "The result of the product A1."


class ConcreteProductA2(AbstractProductA):
    def useful_function_a(self) -> str:
        return "The result of the product A2."


class AbstractProductB(ABC):
    @abstractmethod
    def useful_function_b(self) -> str:
        pass

    @abstractmethod
    def another_useful_function_b(self, collaborator: AbstractProductA) -> str:
        pass


class ConcreteProductB1(AbstractProductB):
    def useful_function_b(self) -> str:
        return "The result of the product B1."

    def another_useful_function_b(self, collaborator: AbstractProductA) -> str:
        result = collaborator.useful_function_a()
        return f"The result of the B1 collaborating with the ({result})"


class ConcreteProductB2(AbstractProductB):
    def useful_function_b(self) -> str:
        return "The result of the product B2."

    def another_useful_function_b(self, collaborator: AbstractProductA) -> str:
        result = collaborator.useful_function_a()
        return f"The result of the B2 collaborating with the ({result})"


class AbstractFactory(ABC):
    @abstractmethod
    def create_product_a(self) -> AbstractProductA:
        pass

    @abstractmethod
    def create_product_b(self) -> AbstractProductB:
        pass


class ConcreteFactory1(AbstractFactory):
    def create_product_a(self) -> AbstractProductA:
        return ConcreteProductA1()

    def create_product_b(self) -> AbstractProductB:
        return ConcreteProductB1()


class ConcreteFactory2(AbstractFactory):
    def create_product_a(self) -> AbstractProductA:
        return ConcreteProductA2()

    def create_product_b(self) -> AbstractProductB:
        return ConcreteProductB2()


def client_code(factory: AbstractFactory) -> str:
    product_a = factory.create_product_a()
    product_b = factory.create_product_b()
    return f"{product_b.useful_function_b()} | {product_b.another_useful_function_b(product_a)}"


if __name__ == "__main__":
    print(client_code(ConcreteFactory1()))
    print(client_code(ConcreteFactory2()))
'''

PYTHON310_CODE = '''"""
Abstract Factory - Python 3.10+ Example: Protocols & Dataclass Product Families
"""
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Button:
    theme: str

    def render(self) -> str:
        return f"[{self.theme} Button]"


@dataclass(frozen=True)
class Checkbox:
    theme: str

    def render(self) -> str:
        return f"[{self.theme} Checkbox]"


class GUIFactory(Protocol):
    def create_button(self) -> Button: ...
    def create_checkbox(self) -> Checkbox: ...


class DarkThemeFactory:
    def create_button(self) -> Button:
        return Button(theme="Dark")

    def create_checkbox(self) -> Checkbox:
        return Checkbox(theme="Dark")


class LightThemeFactory:
    def create_button(self) -> Button:
        return Button(theme="Light")

    def create_checkbox(self) -> Checkbox:
        return Checkbox(theme="Light")


def get_factory(theme: str) -> GUIFactory:
    match theme:
        case "dark":
            return DarkThemeFactory()
        case "light":
            return LightThemeFactory()
        case _:
            raise ValueError(f"Unknown theme: {theme}")


if __name__ == "__main__":
    factory = get_factory("dark")
    print(factory.create_button().render(), factory.create_checkbox().render())
'''

PYTHON312_CODE = '''"""
Abstract Factory - Python 3.12+ Example: PEP 695 Generic Family Factory
"""
from dataclasses import dataclass
from typing import Protocol

type ComponentPair[B, C] = tuple[B, C]


@dataclass(frozen=True)
class Button:
    label: str


@dataclass(frozen=True)
class Checkbox:
    checked: bool


class Factory[B: Button, C: Checkbox](Protocol):
    def create_button(self) -> B: ...
    def create_checkbox(self) -> C: ...


class StandardFactory:
    def create_button(self) -> Button:
        return Button(label="Standard")

    def create_checkbox(self) -> Checkbox:
        return Checkbox(checked=True)


def build_ui[B: Button, C: Checkbox](factory: Factory[B, C]) -> ComponentPair[B, C]:
    return factory.create_button(), factory.create_checkbox()


if __name__ == "__main__":
    b, c = build_ui(StandardFactory())
    print(f"UI Created: {b}, {c}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Heavy multi-level inheritance tree with AbstractFactory and AbstractProduct ABCs.",
    "3.10": "Structural typing with typing.Protocol, frozen dataclasses, and match-case theme dispatch.",
    "3.12": "Type-safe product families with PEP 695 type parameters Factory[B: Button, C: Checkbox] and type alias ComponentPair.",
}

SCAFFOLD_TEMPLATE = '''"""
Abstract Factory Scaffolding Template
"""
from abc import ABC, abstractmethod


class AbstractProductA(ABC):
    @abstractmethod
    def action_a(self) -> None:
        pass


class AbstractProductB(ABC):
    @abstractmethod
    def action_b(self) -> None:
        pass


class AbstractFactory(ABC):
    @abstractmethod
    def create_product_a(self) -> AbstractProductA:
        pass

    @abstractmethod
    def create_product_b(self) -> AbstractProductB:
        pass


class ConcreteFactory1(AbstractFactory):
    def create_product_a(self) -> AbstractProductA:
        raise NotImplementedError

    def create_product_b(self) -> AbstractProductB:
        raise NotImplementedError
'''

PATTERN = Pattern(
    id="abstract-factory",
    name="Abstract Factory",
    chinese_name="抽象工厂",
    category=Category.CREATIONAL,
    intent="创建一系列相关的或相互依赖的对象，而无需指定它们具体的类。",
    problem="当代码需要与多个不同系列的相关产品协同工作，但你不希望代码依赖于这些产品的具体类时，硬编码构造会导致系列对象不匹配且难以替换整个产品族。",
    solution="声明一个抽象工厂接口，其中包含创建产品系列中每种产品的方法。客户端代码仅通过抽象接口与具体工厂和产品进行交互。",
    applicability=[
        "如果代码需要与多个不同系列的相关产品交互，但是由于无法预知对象确切类别而无法直接依赖具体产品时",
        "如果有一个基于一组工厂方法实现的类，并且其职责变得过重时",
    ],
    symptoms=[
        "family of products",
        "cross-platform compatibility",
        "incompatible product combinations",
        "theme switching",
        "multi-vendor integration",
    ],
    pros=[
        "确保同一工厂产出的产品相互兼容",
        "避免客户端和具体产品之间的紧密耦合",
        "单一职责原则：产品生成代码抽取到单一接口",
        "开闭原则：引入新产品族时无需修改客户端代码",
    ],
    cons=[
        "在引入新产品类型（增加新的产品等级结构）时，需要修改抽象工厂接口及其所有子类实现",
    ],
    relations=[
        "与生成器（Builder）：生成器重点在于分步创建复杂对象，抽象工厂重点在于创建相关产品系列",
        "与单例（Singleton）：抽象工厂通常作为单例实现",
        "与工厂方法（Factory Method）：抽象工厂类通常由一组工厂方法组成",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
