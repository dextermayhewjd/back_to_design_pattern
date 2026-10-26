"""Template Method Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Template Method - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod


class AbstractClass(ABC):
    def template_method(self) -> None:
        self.base_operation1()
        self.required_operations1()
        self.base_operation2()
        self.hook1()
        self.required_operation2()
        self.base_operation3()
        self.hook2()

    def base_operation1(self) -> None:
        print("AbstractClass says: I am doing the bulk of the work")

    def base_operation2(self) -> None:
        print("AbstractClass says: But I let subclasses override some operations")

    def base_operation3(self) -> None:
        print("AbstractClass says: But I am doing the bulk of the work anyway")

    @abstractmethod
    def required_operations1(self) -> None:
        pass

    @abstractmethod
    def required_operation2(self) -> None:
        pass

    def hook1(self) -> None:
        pass

    def hook2(self) -> None:
        pass


class ConcreteClass1(AbstractClass):
    def required_operations1(self) -> None:
        print("ConcreteClass1 says: Implemented Operation1")

    def required_operation2(self) -> None:
        print("ConcreteClass1 says: Implemented Operation2")


class ConcreteClass2(AbstractClass):
    def required_operations1(self) -> None:
        print("ConcreteClass2 says: Implemented Operation1")

    def required_operation2(self) -> None:
        print("ConcreteClass2 says: Implemented Operation2")

    def hook1(self) -> None:
        print("ConcreteClass2 says: Overridden Hook1")


def client_code(abstract_class: AbstractClass) -> None:
    abstract_class.template_method()


if __name__ == "__main__":
    print("Same client code can work with different subclasses:")
    client_code(ConcreteClass1())
    print("")
    client_code(ConcreteClass2())
'''

PYTHON310_CODE = '''"""
Template Method - Python 3.10+ Example: Higher-Order Function Workflow with Hooks
"""
from collections.abc import Callable
from typing import Any


def process_pipeline(
    raw_data: str,
    parser: Callable[[str], dict[str, Any]],
    formatter: Callable[[dict[str, Any]], str] | None = None,
) -> str:
    """Template workflow: load -> parse -> format -> deliver."""
    print("Pipeline: Validating raw input data...")
    parsed = parser(raw_data)

    print("Pipeline: Processing internal business rules...")
    if formatter:
        return formatter(parsed)
    return f"Standard Output: {parsed}"


if __name__ == "__main__":
    def json_parser(data: str) -> dict[str, Any]:
        return {"type": "json", "content": data.strip("{}")}

    result = process_pipeline(
        raw_data="{user: 'Alice'}",
        parser=json_parser,
        formatter=lambda d: f"Custom JSON Report -> {d['content']}",
    )
    print(result)
'''

PYTHON312_CODE = '''"""
Template Method - Python 3.12+ Example: PEP 695 Generic Workflow & @override
"""
from typing import override


class BaseWorkflow[T, R]:
    def execute(self, payload: T) -> R:
        cleaned = self.sanitize(payload)
        return self.process(cleaned)

    def sanitize(self, payload: T) -> T:
        return payload

    def process(self, payload: T) -> R:
        raise NotImplementedError


class TextWorkflow(BaseWorkflow[str, int]):
    @override
    def sanitize(self, payload: str) -> str:
        return payload.strip()

    @override
    def process(self, payload: str) -> int:
        return len(payload)


if __name__ == "__main__":
    wf = TextWorkflow()
    count = wf.execute("   Hello World   ")
    print(f"Workflow processed count: {count}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Subclass inheritance tree with abstract steps and hook methods in AbstractClass.",
    "3.10": "Replaced inheritance hierarchy with higher-order functions and optional hook Callables.",
    "3.12": "Type-safe generic pipeline BaseWorkflow[T, R] with @override and PEP 695 type parameters.",
}

SCAFFOLD_TEMPLATE = '''"""
Template Method Scaffolding Template
"""
from abc import ABC, abstractmethod


class AlgorithmBase(ABC):
    def execute_algorithm(self) -> None:
        self.step_one()
        self.step_two()
        self.hook()

    def step_one(self) -> None:
        print("Common Step 1")

    @abstractmethod
    def step_two(self) -> None:
        pass

    def hook(self) -> None:
        pass
'''

PATTERN = Pattern(
    id="template-method",
    name="Template Method",
    chinese_name="模板方法",
    category=Category.BEHAVIORAL,
    intent="在超类中定义一个算法的框架，允许子类在不修改结构的情况下重写算法的特定步骤。",
    problem="当多个类实现相同的整体算法流程（例如数据导入流水线：打开文件 -> 提取原始数据 -> 解析数据 -> 输出报告 -> 关闭文件），但各个子类在某些特定步骤的处理细节上有所不同。如果让每个子类各自实现完整流程，会导致算法骨架和通用步骤代码大量重复。",
    solution="在超类中将算法分解为一系列步骤，并将这些步骤转换为方法；在基类中通过一个骨架方法（模板方法）按次序依次调用这些步骤。通用步骤在基类中提供默认实现，具体差异步骤声明为抽象方法或钩子（Hook）交由子类覆盖。",
    applicability=[
        "只希望客户端扩展某个特定算法步骤，而不是整个算法或其结构时",
        "当多个类的算法大体相同，仅在某些特定细节上略有差异时",
    ],
    symptoms=[
        "duplicated overall algorithm workflow across subclasses",
        "invariant steps interspersed with variant steps",
        "pipeline with customizable hooks",
        "code reuse in data processing or build steps",
    ],
    pros=[
        "你只允许客户端重写一个庞大算法中的特定部分，使得算法其他部分不会被轻易破坏",
        "你可以将相同的代码提取到超类中，消除代码重复",
    ],
    cons=[
        "部分客户端可能会受到算法框架现有结构的限制",
        "通过子类重写默认步骤可能违反里氏替换原则",
        "模板方法中的步骤越多，其维护工作就越繁琐",
    ],
    relations=[
        "与工厂方法（Factory Method）：工厂方法常作为大型模板方法模式的一个特定步骤存在",
        "与策略（Strategy）：模板方法基于类继承来改变算法的部分步骤；策略基于对象组合来改变整个算法",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
