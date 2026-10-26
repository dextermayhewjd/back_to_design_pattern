"""Adapter Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Adapter - Conceptual Example (Classic GoF)
"""


class Target:
    def request(self) -> str:
        return "Target: The default target's behavior."


class Adaptee:
    def specific_request(self) -> str:
        return ".eetpadA eht fo roivaheb laicepS"


class Adapter(Target):
    def __init__(self, adaptee: Adaptee) -> None:
        self.adaptee = adaptee

    def request(self) -> str:
        return f"Adapter: (TRANSLATED) {self.adaptee.specific_request()[::-1]}"


def client_code(target: Target) -> str:
    return target.request()


if __name__ == "__main__":
    target = Target()
    print(client_code(target))

    adaptee = Adaptee()
    adapter = Adapter(adaptee)
    print(client_code(adapter))
'''

PYTHON310_CODE = '''"""
Adapter - Python 3.10+ Example: Protocol-based Structural Adapter & Callables
"""
from collections.abc import Callable
from typing import Protocol


class PaymentProcessor(Protocol):
    def process_payment(self, amount_cents: int) -> str: ...


class ModernStripeService:
    def charge(self, total_dollars: float, currency: str = "USD") -> dict[str, str]:
        return {"status": "success", "id": "tx_9988"}


class StripeAdapter:
    def __init__(self, service: ModernStripeService) -> None:
        self._service = service

    def process_payment(self, amount_cents: int) -> str:
        res = self._service.charge(amount_cents / 100.0)
        return f"Paid via Modern Stripe: {res['id']}"


def pay_with_fn(amount_cents: int, gateway: Callable[[float], str]) -> str:
    return gateway(amount_cents / 100.0)


if __name__ == "__main__":
    adapter: PaymentProcessor = StripeAdapter(ModernStripeService())
    print(adapter.process_payment(5000))
    # Functional adaptation
    res = pay_with_fn(3500, lambda amt: f"Lambda adapted: ${amt:.2f}")
    print(res)
'''

PYTHON312_CODE = '''"""
Adapter - Python 3.12+ Example: PEP 695 Generic Adapter & @override
"""
from collections.abc import Callable
from typing import Protocol

type Converter[In, Out] = Callable[[In], Out]


class DataSource(Protocol):
    def fetch_raw_data(self) -> dict[str, str]: ...


class XMLService:
    def get_xml_payload(self) -> str:
        return "<record><id>101</id><name>Alice</name></record>"


class XMLToDictAdapter[T: XMLService]:
    def __init__(self, service: T, parser: Converter[str, dict[str, str]]) -> None:
        self._service = service
        self._parser = parser

    def fetch_raw_data(self) -> dict[str, str]:
        raw = self._service.get_xml_payload()
        return self._parser(raw)


if __name__ == "__main__":
    adapter = XMLToDictAdapter(
        XMLService(),
        lambda xml: {"parsed": xml.replace("<", "[").replace(">", "]")},
    )
    print(f"Adapted output: {adapter.fetch_raw_data()}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Class-based adapter implementing target interface and wrapping adaptee.",
    "3.10": "Structural typing with typing.Protocol and first-class functional wrappers (Callable).",
    "3.12": "Type-safe generic adapter class XMLToDictAdapter[T: XMLService] with PEP 695 type aliases.",
}

SCAFFOLD_TEMPLATE = '''"""
Adapter Scaffolding Template
"""


class TargetInterface:
    def request(self) -> str:
        return "Standard Request"


class IncompatibleService:
    def specific_request(self) -> str:
        return "Specific Legacy Response"


class Adapter(TargetInterface):
    def __init__(self, service: IncompatibleService) -> None:
        self.service = service

    def request(self) -> str:
        data = self.service.specific_request()
        return f"Adapted: {data}"
'''

PATTERN = Pattern(
    id="adapter",
    name="Adapter",
    chinese_name="适配器",
    category=Category.STRUCTURAL,
    intent="使接口不兼容的对象能够相互合作。",
    problem="当需要接入第三方库、遗留代码或具有不兼容接口的系统时，直接改动现有业务代码会破坏已有架构且难以维护。",
    solution="创建一个中间包装类（Adapter），该类实现客户端所期望的接口，并在内部封装原先不兼容的对象调用与数据格式转换。",
    applicability=[
        "当你希望使用某个现有类，但其接口与其他代码不兼容时",
        "当你希望复用几个现有的子类，这些子类缺少某些通用功能，且无法添加到超类中时",
    ],
    symptoms=[
        "incompatible interface",
        "third-party library integration",
        "legacy API wrapper",
        "data format mismatch",
    ],
    pros=[
        "单一职责原则：可以将接口或数据转换代码从主要业务逻辑中分离",
        "开闭原则：只要客户端代码通过客户端接口与适配器进行交互，就能在不修改现有代码的情况下添加新的适配器",
    ],
    cons=[
        "代码整体复杂度增加，需要引入一系列新的接口和类",
    ],
    relations=[
        "与桥接（Bridge）：桥接通常在设计前期定义，让抽象与实现解耦；适配器通常在后期为不兼容的类搭桥",
        "与装饰（Decorator）：适配器改变已有对象的接口，而装饰增强对象功能且不改变其接口",
        "与代理（Proxy）：代理提供相同的接口，适配器提供不同的接口",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
