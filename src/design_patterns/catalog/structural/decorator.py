"""Decorator Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Decorator - Conceptual Example (Classic GoF)
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

PYTHON310_CODE = '''"""
Decorator - Python 3.10+ Example: Pythonic Function & Method Decorators
"""
from collections.abc import Callable
import functools
import time
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def timer(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"[{func.__name__}] executed in {duration:.6f}s")
        return result
    return wrapper


def retry(times: int = 3):
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_err = None
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_err = e
            raise RuntimeError(f"Failed after {times} attempts: {last_err}")
        return wrapper
    return decorator


@timer
@retry(times=2)
def calculate_metrics(count: int) -> int:
    return sum(i * i for i in range(count))


if __name__ == "__main__":
    res = calculate_metrics(1000)
    print(f"Result: {res}")
'''

PYTHON312_CODE = '''"""
Decorator - Python 3.12+ Example: PEP 695 Generic Decorator with ParamSpec
"""
from collections.abc import Callable
import functools


def logged[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling: {func.__name__}")
        res = func(*args, **kwargs)
        print(f"Finished: {func.__name__}")
        return res
    return wrapper


@logged
def greet(name: str) -> str:
    return f"Hello, {name}!"


if __name__ == "__main__":
    msg = greet("World")
    print(msg)
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Heavy object-oriented wrapper class hierarchy conforming to Component interface.",
    "3.10": "Idiomatic Python @decorator syntax with functools.wraps and ParamSpec type safety.",
    "3.12": "Clean generic decorator definition using PEP 695 def logged[**P, R](func: Callable[P, R]).",
}

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
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
