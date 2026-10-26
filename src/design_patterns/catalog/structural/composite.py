"""Composite Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Composite - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod


class Component(ABC):
    @property
    def parent(self) -> "Component | None":
        return getattr(self, "_parent", None)

    @parent.setter
    def parent(self, parent: "Component | None") -> None:
        self._parent = parent

    def add(self, component: "Component") -> None:
        pass

    def remove(self, component: "Component") -> None:
        pass

    def is_composite(self) -> bool:
        return False

    @abstractmethod
    def operation(self) -> str:
        pass


class Leaf(Component):
    def operation(self) -> str:
        return "Leaf"


class Composite(Component):
    def __init__(self) -> None:
        self._children: list[Component] = []

    def add(self, component: Component) -> None:
        self._children.append(component)
        component.parent = self

    def remove(self, component: Component) -> None:
        self._children.remove(component)
        component.parent = None

    def is_composite(self) -> bool:
        return True

    def operation(self) -> str:
        results = [child.operation() for child in self._children]
        return f"Branch({'+'.join(results)})"


def client_code(component: Component) -> str:
    return f"RESULT: {component.operation()}"


if __name__ == "__main__":
    simple = Leaf()
    print("Client: I've got a simple component:")
    print(client_code(simple))

    tree = Composite()
    branch1 = Composite()
    branch1.add(Leaf())
    branch1.add(Leaf())

    branch2 = Composite()
    branch2.add(Leaf())

    tree.add(branch1)
    tree.add(branch2)
    print("\\nClient: Now I've got a composite tree:")
    print(client_code(tree))
'''

PYTHON310_CODE = '''"""
Composite - Python 3.10+ Example: Dataclass Tree & Recursive Generator Traversal
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass
class Item:
    name: str
    price: float

    def total(self) -> float:
        return self.price

    def all_items(self) -> Iterator[str]:
        yield f"{self.name} (${self.price:.2f})"


@dataclass
class Box:
    name: str
    children: list[Item | Box] = field(default_factory=list)

    def add(self, child: Item | Box) -> Box:
        self.children.append(child)
        return self

    def total(self) -> float:
        return sum(child.total() for child in self.children)

    def all_items(self) -> Iterator[str]:
        yield f"Box: {self.name}"
        for child in self.children:
            yield from child.all_items()


if __name__ == "__main__":
    order = Box("Order #100")
    electronics = Box("Electronics")
    electronics.add(Item("Phone", 699.0)).add(Item("Headphones", 149.0))
    order.add(electronics).add(Item("Sticker Pack", 4.99))

    print(f"Total: ${order.total():.2f}")
    for entry in order.all_items():
        print(f" - {entry}")
'''

PYTHON312_CODE = '''"""
Composite - Python 3.12+ Example: PEP 695 Generic Tree & Pattern Matching
"""
from dataclasses import dataclass, field

type Tree[T] = Leaf[T] | Group[T]


@dataclass
class Leaf[T]:
    value: T

    def render(self) -> str:
        return f"Leaf({self.value})"


@dataclass
class Group[T]:
    children: list[Tree[T]] = field(default_factory=list)

    def add(self, child: Tree[T]) -> None:
        self.children.append(child)

    def render(self) -> str:
        inner = ", ".join(c.render() for c in self.children)
        return f"Group([{inner}])"


if __name__ == "__main__":
    root: Group[int] = Group()
    sub: Group[int] = Group()
    sub.add(Leaf(10))
    sub.add(Leaf(20))
    root.add(sub)
    root.add(Leaf(30))
    print(root.render())
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Heavy Component base class with empty method stubs for add/remove/getChild.",
    "3.10": "Replaced abstract boilerplate with union types (Item | Box), dataclasses, and yield from generators.",
    "3.12": "Type-safe recursive generic trees via PEP 695 type Tree[T] = Leaf[T] | Group[T].",
}

SCAFFOLD_TEMPLATE = '''"""
Composite Scaffolding Template
"""
from abc import ABC, abstractmethod


class Component(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass


class Leaf(Component):
    def execute(self) -> None:
        print("Leaf executed")


class Composite(Component):
    def __init__(self) -> None:
        self._children: list[Component] = []

    def add(self, child: Component) -> None:
        self._children.append(child)

    def execute(self) -> None:
        for child in self._children:
            child.execute()
'''

PATTERN = Pattern(
    id="composite",
    name="Composite",
    chinese_name="组合",
    category=Category.STRUCTURAL,
    intent="将对象组合成树状结构以表示“部分-整体”的层次结构，使得用户对单个对象和组合对象的使用具有一致性。",
    problem="当核心模型呈现树状结构（例如图形界面节点、组织架构、文件系统或嵌套菜单）时，如果对简单对象和复合容器采用不同的方法处理，客户端代码将充斥大量的类型检查和多层嵌套循环。",
    solution="定义通用的组件抽象接口（Component），让叶子节点（Leaf）与容器节点（Composite）实现相同接口，容器内部递归委派其子节点执行操作。",
    applicability=[
        "需要实现树状对象结构时",
        "希望客户端代码以统一方式处理简单和复杂对象时",
    ],
    symptoms=[
        "part-whole hierarchy",
        "recursive tree structure",
        "nested directories or menus",
        "uniform treatment of leaf and composite",
    ],
    pros=[
        "可以利用多态和递归机制更方便地使用复杂树结构",
        "开闭原则：无需更改现有代码，即可在应用中添加新元素类型",
    ],
    cons=[
        "对于功能差异较大的类，提供公共接口可能会使接口过泛，难以进行类型限制",
    ],
    relations=[
        "与生成器（Builder）：生成器常用于逐步构造复杂的组合树",
        "与访问者（Visitor）：访问者模式常用于在整个组合树结构上执行特定操作",
        "与迭代器（Iterator）：可以使用迭代器遍历组合树中的元素",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
