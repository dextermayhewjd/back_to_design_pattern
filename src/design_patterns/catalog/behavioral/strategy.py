"""Strategy Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Strategy - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def do_algorithm(self, data: list[str]) -> list[str]:
        pass


class ConcreteStrategyA(Strategy):
    def do_algorithm(self, data: list[str]) -> list[str]:
        return sorted(data)


class ConcreteStrategyB(Strategy):
    def do_algorithm(self, data: list[str]) -> list[str]:
        return list(reversed(sorted(data)))


class Context:
    def __init__(self, strategy: Strategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy

    def do_some_business_logic(self, data: list[str]) -> str:
        print("Context: Sorting data using the strategy (not sure how it'll do it)")
        result = self._strategy.do_algorithm(data)
        return ", ".join(result)


if __name__ == "__main__":
    context = Context(ConcreteStrategyA())
    data = ["a", "b", "c", "d", "e"]
    print("Client: Strategy is set to normal sorting.")
    print(context.do_some_business_logic(data))

    print("\\nClient: Strategy is set to reverse sorting.")
    context.strategy = ConcreteStrategyB()
    print(context.do_some_business_logic(data))
'''

PYTHON310_CODE = '''"""
Strategy - Python 3.10+ Example: First-Class Callable Strategies
"""
from collections.abc import Callable


# A Strategy in Python is simply a Callable
ShippingStrategy = Callable[[float, float], float]


def standard_shipping(weight_kg: float, distance_km: float) -> float:
    return 5.0 + (weight_kg * 1.5) + (distance_km * 0.05)


def express_shipping(weight_kg: float, distance_km: float) -> float:
    return 20.0 + (weight_kg * 4.0) + (distance_km * 0.15)


def free_economy_shipping(weight_kg: float, distance_km: float) -> float:
    return 0.0


def calculate_shipping(weight_kg: float, distance_km: float, strategy: ShippingStrategy) -> float:
    return strategy(weight_kg, distance_km)


if __name__ == "__main__":
    cost1 = calculate_shipping(2.5, 120, standard_shipping)
    print(f"Standard Shipping: ${cost1:.2f}")

    cost2 = calculate_shipping(2.5, 120, express_shipping)
    print(f"Express Shipping:  ${cost2:.2f}")

    # Ad-hoc strategy via lambda
    cost3 = calculate_shipping(2.5, 120, lambda w, d: w * 2.0)
    print(f"Custom Flat Rate:  ${cost3:.2f}")
'''

PYTHON312_CODE = '''"""
Strategy - Python 3.12+ Example: PEP 695 Generic Strategy
"""
from collections.abc import Callable

type Strategy[T, R] = Callable[[T], R]


class AlgorithmRunner[T, R]:
    def __init__(self, strategy: Strategy[T, R]) -> None:
        self.strategy = strategy

    def run(self, data: T) -> R:
        return self.strategy(data)


if __name__ == "__main__":
    runner = AlgorithmRunner[list[str], list[str]](strategy=lambda items: sorted(items, reverse=True))
    result = runner.run(["apple", "banana", "cherry"])
    print(f"Reversed sort: {result}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Heavy Strategy ABC with ConcreteStrategy subclasses wrapping a single algorithm method.",
    "3.10": "Replaced classes with first-class functions (Callable) passed directly as arguments.",
    "3.12": "Type-safe generic strategy parameterized via PEP 695 type Strategy[T, R] = Callable[[T], R].",
}

SCAFFOLD_TEMPLATE = '''"""
Strategy Scaffolding Template
"""
from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def execute(self, data: object) -> object:
        pass


class Context:
    def __init__(self, strategy: Strategy) -> None:
        self.strategy = strategy

    def perform_action(self, data: object) -> object:
        return self.strategy.execute(data)
'''

PATTERN = Pattern(
    id="strategy",
    name="Strategy",
    chinese_name="策略",
    category=Category.BEHAVIORAL,
    intent="定义一系列算法，把它们一个个封装起来，并且使它们可以相互替换。本模式使得算法可独立于使用它的客户而变化。",
    problem="当一个类有许多相似但在细节上不同的算法行为（如不同格式的数据压缩、不同运输方式的运费计算、不同的支付通道或排序方式），若将所有算法硬编码进同一类中，会产生庞大的条件分支语句且难以扩展新算法。",
    solution="找出负责完成特定算法的所有代码，将其抽取到一组称为策略（Strategy）的独立类中。原始上下文持有策略接口的引用，客户端可在运行时随时向上下文注入具体的策略实例。",
    applicability=[
        "想使用对象中各种不同的算法变体，并希望在运行时能够动态切换算法时",
        "有许多仅在执行某些行为时略有不同的相似类时",
        "如果算法在上下文的逻辑中不是特别重要，使用该模式能将类的业务逻辑与其算法实现细节隔离开来",
    ],
    symptoms=[
        "swap algorithms or business rules at runtime",
        "multiple routing / pricing / sorting variants",
        "branching on type of calculation",
        "pluggable discount or tax rules",
    ],
    pros=[
        "可以在运行时切换对象内的算法",
        "可以将算法的实现细节与使用算法的代码隔离开来",
        "可以使用组合来代替继承",
        "开闭原则：无需对上下文进行修改就能够引入新的策略",
    ],
    cons=[
        "如果算法极少发生改变，没有必要引入额外的类和接口让程序变得复杂",
        "客户端必须了解不同策略之间的区别才能选择合适的策略",
    ],
    relations=[
        "与状态（State）：状态和策略基于相似的接口组合结构，但状态模式中状态类彼此知道并能改变上下文状态；策略模式中各个策略彼此完全独立",
        "与命令（Command）：命令将特定操作封装为对象；策略提供解决相同问题的不同算法互换",
        "与模板方法（Template Method）：模板方法基于继承来改变算法的部分步骤；策略基于组合来改变整个算法",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
