"""Facade Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Facade - Conceptual Example (Classic GoF)
"""


class Subsystem1:
    def operation1(self) -> str:
        return "Subsystem1: Ready!"

    def operation_n(self) -> str:
        return "Subsystem1: Go!"


class Subsystem2:
    def operation1(self) -> str:
        return "Subsystem2: Get ready!"

    def operation_z(self) -> str:
        return "Subsystem2: Fire!"


class Facade:
    def __init__(self, subsystem1: Subsystem1 | None = None, subsystem2: Subsystem2 | None = None) -> None:
        self._subsystem1 = subsystem1 or Subsystem1()
        self._subsystem2 = subsystem2 or Subsystem2()

    def operation(self) -> str:
        results = []
        results.append("Facade initializes subsystems:")
        results.append(self._subsystem1.operation1())
        results.append(self._subsystem2.operation1())
        results.append("Facade orders subsystems to perform the action:")
        results.append(self._subsystem1.operation_n())
        results.append(self._subsystem2.operation_z())
        return "\\n".join(results)


def client_code(facade: Facade) -> str:
    return facade.operation()


if __name__ == "__main__":
    facade = Facade()
    print(client_code(facade))
'''

PYTHON310_CODE = '''"""
Facade - Python 3.10+ Example: Dataclass Facade & Multi-Subsystem Coordination
"""
from dataclasses import dataclass, field


class AuthSubsystem:
    def verify_token(self, token: str) -> bool:
        return token == "valid-token"


class PaymentSubsystem:
    def charge(self, amount: float) -> str:
        return f"Charged ${amount:.2f}"


class NotificationSubsystem:
    def send_receipt(self, email: str, details: str) -> str:
        return f"Receipt sent to {email}: {details}"


@dataclass
class CheckoutFacade:
    auth: AuthSubsystem = field(default_factory=AuthSubsystem)
    payment: PaymentSubsystem = field(default_factory=PaymentSubsystem)
    notifier: NotificationSubsystem = field(default_factory=NotificationSubsystem)

    def process_order(self, token: str, email: str, amount: float) -> str:
        if not self.auth.verify_token(token):
            raise PermissionError("Invalid authentication token")
        receipt = self.payment.charge(amount)
        notify_res = self.notifier.send_receipt(email, receipt)
        return f"Order processed: {receipt} | {notify_res}"


if __name__ == "__main__":
    facade = CheckoutFacade()
    result = facade.process_order("valid-token", "user@example.com", 99.99)
    print(result)
'''

PYTHON312_CODE = '''"""
Facade - Python 3.12+ Example: PEP 695 Generic Pipeline Facade
"""
from collections.abc import Callable

type Stage[T, U] = Callable[[T], U]


class PipelineFacade[In, Out]:
    def __init__(self, step1: Stage[In, str], step2: Stage[str, Out]) -> None:
        self._step1 = step1
        self._step2 = step2

    def execute(self, payload: In) -> Out:
        intermediate = self._step1(payload)
        return self._step2(intermediate)


if __name__ == "__main__":
    pipeline = PipelineFacade[dict[str, int], int](
        step1=lambda d: f"Length={len(d)}",
        step2=lambda s: len(s),
    )
    result = pipeline.execute({"a": 1, "b": 2})
    print(f"Pipeline Facade output: {result}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Class-based facade orchestrating multiple subsystem class instances manually.",
    "3.10": "Dataclass default dependencies and clean functional facade methods.",
    "3.12": "Type-safe generic orchestrator PipelineFacade[In, Out] with PEP 695 type aliases.",
}

SCAFFOLD_TEMPLATE = '''"""
Facade Scaffolding Template
"""


class ComplexSubsystemA:
    def step_one(self) -> None:
        pass


class ComplexSubsystemB:
    def step_two(self) -> None:
        pass


class Facade:
    def __init__(self) -> None:
        self.sub_a = ComplexSubsystemA()
        self.sub_b = ComplexSubsystemB()

    def simplified_api(self) -> None:
        self.sub_a.step_one()
        self.sub_b.step_two()
'''

PATTERN = Pattern(
    id="facade",
    name="Facade",
    chinese_name="外观",
    category=Category.STRUCTURAL,
    intent="为复杂的子系统、类库或框架提供一个统一且高度简化的接口。",
    problem="当需要与数十个内部依赖复杂、调用次序严格的子系统对象协作时，客户端代码会与子系统细节深度绑定，导致维护、排错和测试极其困难。",
    solution="提供一个外观类（Facade），只暴露客户端真正关心的简明操作，将复杂的子系统生命周期、配置以及跨模块协调调用封装在外观背后。",
    applicability=[
        "需要为一个复杂子系统提供一个简单接口时",
        "需要将子系统组织为多层结构，通过外观定义每层的入口点以减少层级间依赖时",
    ],
    symptoms=[
        "complex subsystem with too many classes",
        "convoluted initialization sequence",
        "leaky subsystem abstractions",
        "need simplified entry point",
    ],
    pros=[
        "让自己的代码独立于复杂子系统的细枝末节",
        "降低整个系统的耦合度，提高模块复用性",
    ],
    cons=[
        "外观很容易成为与程序中所有类都耦合的“上帝对象（God Object）”",
    ],
    relations=[
        "与适配器（Adapter）：外观为子系统定义新接口；适配器使现有不兼容接口协同工作",
        "与中介者（Mediator）：外观主要用于单向简化外部对子系统的调用；中介者抽取内部组件之间的双向复杂通信",
        "与单例（Singleton）：外观类通常只需要一个实例，因此常被实现为单例",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
