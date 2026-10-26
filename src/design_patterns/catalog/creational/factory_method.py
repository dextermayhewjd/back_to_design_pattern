"""Factory Method Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Factory Method - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod


class Product(ABC):
    @abstractmethod
    def operation(self) -> str:
        pass


class ConcreteProduct1(Product):
    def operation(self) -> str:
        return "{Result of ConcreteProduct1}"


class ConcreteProduct2(Product):
    def operation(self) -> str:
        return "{Result of ConcreteProduct2}"


class Creator(ABC):
    @abstractmethod
    def factory_method(self) -> Product:
        pass

    def some_operation(self) -> str:
        product = self.factory_method()
        return f"Creator: The same creator's code has just worked with {product.operation()}"


class ConcreteCreator1(Creator):
    def factory_method(self) -> Product:
        return ConcreteProduct1()


class ConcreteCreator2(Creator):
    def factory_method(self) -> Product:
        return ConcreteProduct2()


def client_code(creator: Creator) -> str:
    return creator.some_operation()


if __name__ == "__main__":
    print(client_code(ConcreteCreator1()))
    print(client_code(ConcreteCreator2()))
'''

PYTHON310_CODE = '''"""
Factory Method - Python 3.10+ Example: Registry & Match-Case Factory
"""
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Button:
    label: str
    action: str

    def render(self) -> str:
        return f"[{self.label} -> {self.action}]"


def create_button(dialog_type: str) -> Button:
    match dialog_type:
        case "windows":
            return Button(label="OK", action="windows_click")
        case "web":
            return Button(label="Submit", action="http_post")
        case "mobile":
            return Button(label="Tap", action="touch_event")
        case _:
            raise ValueError(f"Unknown dialog type: {dialog_type}")


class Dialog:
    def __init__(self, factory: Callable[[], Button] | None = None) -> None:
        self.factory = factory or (lambda: create_button("web"))

    def render_window(self) -> str:
        button = self.factory()
        return f"Dialog rendering: {button.render()}"


if __name__ == "__main__":
    win_dialog = Dialog(lambda: create_button("windows"))
    print(win_dialog.render_window())
    web_dialog = Dialog()
    print(web_dialog.render_window())
'''

PYTHON312_CODE = '''"""
Factory Method - Python 3.12+ Example: PEP 695 Generic Factory & Type Alias
"""
from collections.abc import Callable
from dataclasses import dataclass
from typing import override

type Factory[T] = Callable[[], T]


@dataclass
class Button:
    label: str

    def render(self) -> str:
        return f"Button({self.label})"


class HTMLButton(Button):
    @override
    def render(self) -> str:
        return f"<button>{self.label}</button>"


class Dialog[T: Button]:
    def __init__(self, factory: Factory[T]) -> None:
        self._factory = factory

    def render(self) -> str:
        btn = self._factory()
        return f"Dialog container with: {btn.render()}"


if __name__ == "__main__":
    html_dialog = Dialog(lambda: HTMLButton("Submit"))
    print(html_dialog.render())
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Classic GoF inheritance hierarchy with abstract Creator and Product base classes using abc.ABC.",
    "3.10": "Replaced heavy Creator class hierarchy with Callable factories, dataclasses, and match-case dispatch.",
    "3.12": "Leveraged PEP 695 generic classes Dialog[T: Button], parameterized type alias Factory[T], and @override.",
}

SCAFFOLD_TEMPLATE = '''"""
Factory Method Scaffolding Template
"""
from abc import ABC, abstractmethod


class Product(ABC):
    @abstractmethod
    def do_work(self) -> None:
        pass


class ConcreteProductA(Product):
    def do_work(self) -> None:
        print("ConcreteProductA working")


class Creator(ABC):
    @abstractmethod
    def create_product(self) -> Product:
        pass

    def execute(self) -> None:
        product = self.create_product()
        product.do_work()


class ConcreteCreatorA(Creator):
    def create_product(self) -> Product:
        return ConcreteProductA()
'''

PATTERN = Pattern(
    id="factory-method",
    name="Factory Method",
    chinese_name="工厂方法",
    category=Category.CREATIONAL,
    intent="在父类中提供一个创建对象的接口以允许子类决定实例化对象的类型。",
    problem="直接在代码中使用具体类的构造函数会导致核心业务逻辑与具体类型强耦合，当需要新增产品类型或调整创建逻辑时必须修改现有业务代码。",
    solution="用特殊的工厂方法调用替代对于直接对象构造过程的调用，子类可以重写该方法并创建不同的产品实例。",
    applicability=[
        "在编写代码的过程中，如果无法预知对象确切的类别及其依赖关系时",
        "希望复用现有对象来节省系统资源，而不是每次都重新创建对象时",
        "希望为库或框架的用户提供扩展其内部组件语言接口的方式时",
    ],
    symptoms=[
        "tight coupling",
        "new operator proliferation",
        "subclass instantiation",
        "conditional object creation",
        "product family extension",
    ],
    pros=[
        "避免创建者和具体产品之间的紧密耦合",
        "单一职责原则：可以将产品创建代码独立到单一位置",
        "开闭原则：无需更改现有客户端代码即可引入新的产品类型",
    ],
    cons=[
        "应用工厂方法模式需要引入许多新的子类，代码可能会因此变得更复杂",
    ],
    relations=[
        "与抽象工厂（Abstract Factory）：工厂方法是基于继承的，而抽象工厂通常基于组合并且由一组工厂方法组成",
        "与原型（Prototype）：原型不需要子类化，但需要初始化克隆；工厂方法依赖子类继承",
        "与模板方法（Template Method）：工厂方法常作为大型模板方法的一个步骤存在",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
