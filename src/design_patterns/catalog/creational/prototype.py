"""Prototype Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Prototype - Conceptual Example (Classic GoF)
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

PYTHON310_CODE = '''"""
Prototype - Python 3.10+ Example: Dataclass Cloning & dataclasses.replace
"""
from dataclasses import dataclass, field, replace


@dataclass
class GraphicElement:
    shape: str
    color: str
    metadata: dict[str, str] = field(default_factory=dict)

    def clone(self, **overrides) -> "GraphicElement":
        return replace(self, **overrides)


if __name__ == "__main__":
    proto = GraphicElement(shape="circle", color="red", metadata={"layer": "1"})
    clone1 = proto.clone(color="blue")
    print(f"Original: {proto}")
    print(f"Cloned:   {clone1}")
'''

PYTHON312_CODE = '''"""
Prototype - Python 3.12+ Example: typing.Self Type-Safe Cloning
"""
from dataclasses import dataclass, replace
from typing import Self

type Properties = dict[str, str | int]


@dataclass(frozen=True)
class DocumentTemplate:
    title: str
    content: str
    properties: Properties

    def clone_with(self, **changes) -> Self:
        return replace(self, **changes)


if __name__ == "__main__":
    base_doc = DocumentTemplate(
        title="Report Template",
        content="Standard body text",
        properties={"version": 1, "status": "draft"},
    )
    custom_doc = base_doc.clone_with(title="Q4 Financial Report")
    print(f"Base: {base_doc.title}")
    print(f"Copy: {custom_doc.title}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Manual __copy__ and __deepcopy__ dunder implementation handling dict state copying.",
    "3.10": "Built-in dataclasses.replace eliminates manual cloning methods and field copy logic.",
    "3.12": "Utilized typing.Self return types for seamless derived-class cloning with PEP 695 type alias.",
}

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
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
