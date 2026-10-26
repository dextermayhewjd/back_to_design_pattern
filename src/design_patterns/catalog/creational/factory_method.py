"""Factory Method Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Factory Method - Conceptual Example
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

REALWORLD_CODE = '''"""
Factory Method - Real-World Example: Cross-Platform UI Dialogs
"""
from abc import ABC, abstractmethod


class Button(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

    @abstractmethod
    def on_click(self) -> str:
        pass


class WindowsButton(Button):
    def render(self) -> str:
        return "<WindowsButton>OK</WindowsButton>"

    def on_click(self) -> str:
        return "Windows click event emitted"


class HTMLButton(Button):
    def render(self) -> str:
        return "<button type='submit'>OK</button>"

    def on_click(self) -> str:
        return "HTML form submitted"


class Dialog(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass

    def render_window(self) -> str:
        button = self.create_button()
        return f"Rendering window with button: {button.render()} -> {button.on_click()}"


class WindowsDialog(Dialog):
    def create_button(self) -> Button:
        return WindowsButton()


class WebDialog(Dialog):
    def create_button(self) -> Button:
        return HTMLButton()


if __name__ == "__main__":
    dialog = WebDialog()
    print(dialog.render_window())
'''

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
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
