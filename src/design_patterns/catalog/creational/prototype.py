"""Prototype Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Prototype - Conceptual Example
"""
import copy
from typing import Any


class SelfReferencingEntity:
    def __init__(self) -> None:
        self.parent: Any = None

    def set_parent(self, parent: Any) -> None:
        self.parent = parent


class SomeComponent:
    def __init__(self, some_int: int, some_list_of_objects: list[Any], some_circular_ref: SelfReferencingEntity) -> None:
        self.some_int = some_int
        self.some_list_of_objects = some_list_of_objects
        self.some_circular_ref = some_circular_ref

    def __copy__(self) -> "SomeComponent":
        some_list_of_objects = copy.copy(self.some_list_of_objects)
        some_circular_ref = copy.copy(self.some_circular_ref)

        new = self.__class__(
            self.some_int, some_list_of_objects, some_circular_ref
        )
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo: dict | None = None) -> "SomeComponent":
        if memo is None:
            memo = {}

        some_list_of_objects = copy.deepcopy(self.some_list_of_objects, memo)
        some_circular_ref = copy.deepcopy(self.some_circular_ref, memo)

        new = self.__class__(
            self.some_int, some_list_of_objects, some_circular_ref
        )
        new.__dict__ = copy.deepcopy(self.__dict__, memo)
        return new


if __name__ == "__main__":
    list_of_objects = [1, {1, 2, 3}, [1, 2, 3]]
    circular_ref = SelfReferencingEntity()
    component = SomeComponent(23, list_of_objects, circular_ref)
    circular_ref.set_parent(component)

    shallow_copied_component = copy.copy(component)
    deep_copied_component = copy.deepcopy(component)
    print("Prototype components cloned successfully.")
'''

REALWORLD_CODE = '''"""
Prototype - Real-World Example: Document and Page Template Duplication
"""
import copy


class Page:
    def __init__(self, title: str, content: str, tags: list[str]) -> None:
        self.title = title
        self.content = content
        self.tags = tags

    def clone(self) -> "Page":
        return copy.deepcopy(self)

    def __repr__(self) -> str:
        return f"Page(title={self.title!r}, tags={self.tags!r})"


if __name__ == "__main__":
    original = Page("Landing Page Template", "Hero section...", ["marketing", "q4"])
    cloned = original.clone()
    cloned.title = "Special Campaign Landing Page"
    cloned.tags.append("campaign")

    print("Original:", original)
    print("Cloned:", cloned)
'''

SCAFFOLD_TEMPLATE = '''"""
Prototype Scaffolding Template
"""
import copy
from abc import ABC, abstractmethod


class Prototype(ABC):
    @abstractmethod
    def clone(self) -> "Prototype":
        pass


class ConcretePrototype(Prototype):
    def __init__(self, state: str) -> None:
        self.state = state

    def clone(self) -> "ConcretePrototype":
        return copy.deepcopy(self)
'''

PATTERN = Pattern(
    id="prototype",
    name="Prototype",
    chinese_name="原型",
    category=Category.CREATIONAL,
    intent="用原型实例指定创建对象的种类，并且通过复制这些原型创建新的对象，无需使代码与具体类耦合。",
    problem="直接从外部克隆对象不仅需要知道该对象的具体类，且对象私有成员无法直接访问，此外如果对象有复杂的依赖关系，手动复制十分繁琐。",
    solution="声明通用的克隆接口，将克隆过程委派给正在被克隆的实际对象本身（利用 Python 的 `copy.copy` 或 `copy.deepcopy`）。",
    applicability=[
        "需要复制一些对象，同时又希望代码独立于这些对象的所属类时",
        "如果子类的区别仅在于其对象的初始化方式，希望通过克隆预设原型避免子类激增时",
    ],
    symptoms=[
        "expensive object creation",
        "need deep copy of complex hierarchy",
        "dynamic object cloning",
        "preset template duplication",
    ],
    pros=[
        "克隆预生成原型，避免重复繁重的初始化逻辑",
        "更方便地生成复杂对象",
        "可以用继承以外的方式来处理复杂对象的不同配置",
    ],
    cons=[
        "克隆包含循环引用的复杂对象可能会非常棘手",
    ],
    relations=[
        "与单例（Singleton）：原型通过复制创建新对象，单例保证全局唯一实例",
        "与工厂方法（Factory Method）：原型可以替代工厂方法，避免为不同对象创建子类",
    ],
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
