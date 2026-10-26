"""Adapter Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Adapter - Conceptual Example
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

REALWORLD_CODE = '''"""
Adapter - Real-World Example: Third-Party Payment Gateway
"""


class InternalPaymentProcessor:
    def process_payment(self, amount_cents: int) -> str:
        return f"Processed ${amount_cents / 100:.2f} via Internal System"


class StripeSDK:
    def charge(self, total_dollars: float, currency: str) -> dict[str, str]:
        return {"status": "success", "charge_id": "ch_12345", "currency": currency}


class StripeAdapter(InternalPaymentProcessor):
    def __init__(self, stripe_sdk: StripeSDK) -> None:
        self.stripe = stripe_sdk

    def process_payment(self, amount_cents: int) -> str:
        dollars = amount_cents / 100.0
        response = self.stripe.charge(total_dollars=dollars, currency="USD")
        return f"Processed ${dollars:.2f} via Stripe (id={response['charge_id']})"


if __name__ == "__main__":
    processor: InternalPaymentProcessor = StripeAdapter(StripeSDK())
    print(processor.process_payment(2500))
'''

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
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
