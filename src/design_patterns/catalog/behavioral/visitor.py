"""Visitor Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Visitor - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod


class Component(ABC):
    @abstractmethod
    def accept(self, visitor: "Visitor") -> str:
        pass


class ConcreteComponentA(Component):
    def accept(self, visitor: "Visitor") -> str:
        return visitor.visit_concrete_component_a(self)

    def exclusive_method_of_concrete_component_a(self) -> str:
        return "A"


class ConcreteComponentB(Component):
    def accept(self, visitor: "Visitor") -> str:
        return visitor.visit_concrete_component_b(self)

    def special_method_of_concrete_component_b(self) -> str:
        return "B"


class Visitor(ABC):
    @abstractmethod
    def visit_concrete_component_a(self, element: ConcreteComponentA) -> str:
        pass

    @abstractmethod
    def visit_concrete_component_b(self, element: ConcreteComponentB) -> str:
        pass


class ConcreteVisitor1(Visitor):
    def visit_concrete_component_a(self, element: ConcreteComponentA) -> str:
        return f"{element.exclusive_method_of_concrete_component_a()} + ConcreteVisitor1"

    def visit_concrete_component_b(self, element: ConcreteComponentB) -> str:
        return f"{element.special_method_of_concrete_component_b()} + ConcreteVisitor1"


class ConcreteVisitor2(Visitor):
    def visit_concrete_component_a(self, element: ConcreteComponentA) -> str:
        return f"{element.exclusive_method_of_concrete_component_a()} + ConcreteVisitor2"

    def visit_concrete_component_b(self, element: ConcreteComponentB) -> str:
        return f"{element.special_method_of_concrete_component_b()} + ConcreteVisitor2"


def client_code(components: list[Component], visitor: Visitor) -> None:
    for component in components:
        print(component.accept(visitor))


if __name__ == "__main__":
    components: list[Component] = [ConcreteComponentA(), ConcreteComponentB()]

    print("The client code works with all visitors via the base Visitor interface:")
    visitor1 = ConcreteVisitor1()
    client_code(components, visitor1)

    print("\\nIt allows the same client code to work with different visitors:")
    visitor2 = ConcreteVisitor2()
    client_code(components, visitor2)
'''

PYTHON310_CODE = '''"""
Visitor - Python 3.10+ Example: @functools.singledispatch & Match-Case
"""
from dataclasses import dataclass
from functools import singledispatch


@dataclass
class NumberNode:
    val: float


@dataclass
class AddNode:
    left: object
    right: object


# In Python, @singledispatch eliminates the need for double-dispatch accept() methods!
@singledispatch
def evaluate(node) -> float:
    raise NotImplementedError(f"Unsupported node type: {type(node)}")


@evaluate.register
def _(node: NumberNode) -> float:
    return node.val


@evaluate.register
def _(node: AddNode) -> float:
    return evaluate(node.left) + evaluate(node.right)


def stringify(node) -> str:
    """Alternative visitor implemented purely with pattern matching."""
    match node:
        case NumberNode(val):
            return str(val)
        case AddNode(left, right):
            return f"({stringify(left)} + {stringify(right)})"
        case _:
            return str(node)


if __name__ == "__main__":
    expr = AddNode(NumberNode(10), AddNode(NumberNode(5), NumberNode(3)))
    print("Formula:", stringify(expr))
    print("Evaluated result:", evaluate(expr))
'''

PYTHON312_CODE = '''"""
Visitor - Python 3.12+ Example: PEP 695 Type Alias & Pattern Matching
"""
from dataclasses import dataclass

type Expression = Num | BinOp


@dataclass
class Num:
    value: int


@dataclass
class BinOp:
    left: Expression
    op: str
    right: Expression


def evaluate_expression(expr: Expression) -> int:
    match expr:
        case Num(val):
            return val
        case BinOp(l, "+", r):
            return evaluate_expression(l) + evaluate_expression(r)
        case BinOp(l, "*", r):
            return evaluate_expression(l) * evaluate_expression(r)
        case _:
            raise ValueError(f"Unknown operation: {expr}")


if __name__ == "__main__":
    ast: Expression = BinOp(Num(3), "*", BinOp(Num(4), "+", Num(5)))
    print("Evaluated AST:", evaluate_expression(ast))
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Double-dispatch ceremony requiring accept(visitor) on elements and visit_* on Visitor.",
    "3.10": "Replaced double-dispatch ceremony with @functools.singledispatch and match-case.",
    "3.12": "Clean algebraic expression processing via PEP 695 type Expression = Num | BinOp and match-case.",
}

SCAFFOLD_TEMPLATE = '''"""
Visitor Scaffolding Template
"""
from abc import ABC, abstractmethod


class Element(ABC):
    @abstractmethod
    def accept(self, visitor: "Visitor") -> None:
        pass


class ConcreteElementA(Element):
    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_a(self)


class Visitor(ABC):
    @abstractmethod
    def visit_a(self, element: ConcreteElementA) -> None:
        pass
'''

PATTERN = Pattern(
    id="visitor",
    name="Visitor",
    chinese_name="访问者",
    category=Category.BEHAVIORAL,
    intent="封装一些作用于某种数据结构中的各元素的操作。它可以在不改变各元素的类的前提下定义作用于这些元素的新操作。",
    problem="当一套核心对象结构（例如语法树 AST、报表节点、CAD 图形结构）已经稳定，但经常需要对其执行各种不同的操作（如代码检查、导出 XML、计算累计面积、生成字节码）。如果把这些新操作都塞进各个节点类中，会污染核心类的业务职责并导致频繁修改发布。",
    solution="将新行为抽取到一个独立的访问者类（Visitor）中。让被操作的元素实现 `accept(visitor)` 方法，通过双分派（Double Dispatch）将自身引用作为参数传给访问者的相应访问方法。",
    applicability=[
        "如果你需要对一个复杂对象结构（例如对象树）中的所有元素执行某些操作，可使用访问者模式",
        "可使用访问者模式来清理辅助行为的业务逻辑",
        "当某个行为仅在类层次结构中的一些类中有意义，而在其他类中没有意义时",
    ],
    symptoms=[
        "need new operations on stable complex object structure",
        "ast or report structure traversal and format export",
        "polluting domain entities with reporting / serialization logic",
        "double dispatch requirement",
    ],
    pros=[
        "开闭原则：你可以引入在不同类对象上执行的新行为，且无需对这些类做出修改",
        "单一职责原则：可将同一行为的多个不同版本集中在同一个类中",
        "访问者可以在遍历对象结构的过程中累积状态",
    ],
    cons=[
        "每次在元素层次结构中增加或删除元素类时，都必须更新所有访问者类",
        "在访问者访问私有成员变量和方法时，可能会违反封装原则",
    ],
    relations=[
        "与组合（Composite）：访问者常用于遍历组合树并在各节点执行操作",
        "与命令（Command）：访问者是命令模式的高级版本，其操作可以对不同类的多种对象执行",
        "与迭代器（Iterator）：迭代器专注于遍历，访问者专注于在遍历过程中执行具体逻辑",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
