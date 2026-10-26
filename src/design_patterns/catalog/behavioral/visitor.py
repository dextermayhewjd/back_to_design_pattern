"""Visitor Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Visitor - Conceptual Example
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

REALWORLD_CODE = '''"""
Visitor - Real-World Example: AST Exporter (XML / JSON Representation)
"""
from abc import ABC, abstractmethod


class Node(ABC):
    @abstractmethod
    def accept(self, visitor: "ASTVisitor") -> str:
        pass


class IdentifierNode(Node):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, visitor: "ASTVisitor") -> str:
        return visitor.visit_identifier(self)


class BinaryOpNode(Node):
    def __init__(self, left: Node, op: str, right: Node) -> None:
        self.left = left
        self.op = op
        self.right = right

    def accept(self, visitor: "ASTVisitor") -> str:
        return visitor.visit_binary_op(self)


class ASTVisitor(ABC):
    @abstractmethod
    def visit_identifier(self, node: IdentifierNode) -> str:
        pass

    @abstractmethod
    def visit_binary_op(self, node: BinaryOpNode) -> str:
        pass


class JSONExportVisitor(ASTVisitor):
    def visit_identifier(self, node: IdentifierNode) -> str:
        return f'{{"type": "Identifier", "name": "{node.name}"}}'

    def visit_binary_op(self, node: BinaryOpNode) -> str:
        left = node.left.accept(self)
        right = node.right.accept(self)
        return f'{{"type": "BinaryOp", "op": "{node.op}", "left": {left}, "right": {right}}}'


if __name__ == "__main__":
    ast = BinaryOpNode(IdentifierNode("x"), "+", IdentifierNode("y"))
    exporter = JSONExportVisitor()
    print("Exported JSON AST:\\n", ast.accept(exporter))
'''

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
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
