"""Builder Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Builder - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod
from typing import Any


class Product1:
    def __init__(self) -> None:
        self.parts: list[Any] = []

    def add(self, part: Any) -> None:
        self.parts.append(part)

    def list_parts(self) -> str:
        return f"Product parts: {', '.join(self.parts)}"


class Builder(ABC):
    @property
    @abstractmethod
    def product(self) -> Product1:
        pass

    @abstractmethod
    def produce_part_a(self) -> None:
        pass

    @abstractmethod
    def produce_part_b(self) -> None:
        pass

    @abstractmethod
    def produce_part_c(self) -> None:
        pass


class ConcreteBuilder1(Builder):
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._product = Product1()

    @property
    def product(self) -> Product1:
        product = self._product
        self.reset()
        return product

    def produce_part_a(self) -> None:
        self._product.add("PartA1")

    def produce_part_b(self) -> None:
        self._product.add("PartB1")

    def produce_part_c(self) -> None:
        self._product.add("PartC1")


class Director:
    def __init__(self) -> None:
        self._builder: Builder | None = None

    @property
    def builder(self) -> Builder:
        assert self._builder is not None
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:
        self._builder = builder

    def build_minimal_viable_product(self) -> None:
        self.builder.produce_part_a()

    def build_full_featured_product(self) -> None:
        self.builder.produce_part_a()
        self.builder.produce_part_b()
        self.builder.produce_part_c()


if __name__ == "__main__":
    director = Director()
    builder = ConcreteBuilder1()
    director.builder = builder

    print("Standard basic product:")
    director.build_minimal_viable_product()
    print(builder.product.list_parts())

    print("Standard full featured product:")
    director.build_full_featured_product()
    print(builder.product.list_parts())
'''

PYTHON310_CODE = '''"""
Builder - Python 3.10+ Example: Dataclass with kw_only & Fluent Builder
"""
from dataclasses import dataclass, field


@dataclass(kw_only=True)
class ServerConfig:
    host: str = "localhost"
    port: int = 8080
    ssl_enabled: bool = False
    workers: int = 4
    middlewares: list[str] = field(default_factory=list)
    timeout: float | None = 30.0


class ServerConfigBuilder:
    def __init__(self) -> None:
        self._config = ServerConfig()

    def with_host(self, host: str) -> "ServerConfigBuilder":
        self._config.host = host
        return self

    def with_port(self, port: int) -> "ServerConfigBuilder":
        self._config.port = port
        return self

    def enable_ssl(self) -> "ServerConfigBuilder":
        self._config.ssl_enabled = True
        return self

    def add_middleware(self, name: str) -> "ServerConfigBuilder":
        self._config.middlewares.append(name)
        return self

    def build(self) -> ServerConfig:
        return self._config


if __name__ == "__main__":
    # Direct keyword-only instantiation (simplifies parameter explosion)
    cfg1 = ServerConfig(host="0.0.0.0", port=443, ssl_enabled=True)
    print(f"Direct kw_only config: {cfg1}")

    # Fluent builder when step-by-step assembly is needed
    cfg2 = (
        ServerConfigBuilder()
        .with_host("api.internal")
        .with_port(9000)
        .add_middleware("auth")
        .add_middleware("rate_limiter")
        .build()
    )
    print(f"Fluent built config: {cfg2}")
'''

PYTHON312_CODE = '''"""
Builder - Python 3.12+ Example: typing.Self Fluent Builder
"""
from dataclasses import dataclass, field
from typing import Self


@dataclass
class Query:
    table: str = ""
    fields: list[str] = field(default_factory=list)
    filters: list[str] = field(default_factory=list)
    limit: int | None = None


class QueryBuilder:
    def __init__(self) -> None:
        self._query = Query()

    def from_table(self, table: str) -> Self:
        self._query.table = table
        return self

    def select(self, *fields: str) -> Self:
        self._query.fields.extend(fields)
        return self

    def where(self, condition: str) -> Self:
        self._query.filters.append(condition)
        return self

    def take(self, count: int) -> Self:
        self._query.limit = count
        return self

    def build(self) -> Query:
        return self._query


if __name__ == "__main__":
    q = (
        QueryBuilder()
        .from_table("users")
        .select("id", "email")
        .where("active = 1")
        .take(5)
        .build()
    )
    print(f"Built Query: {q}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Verbose GoF Builder and Director hierarchy managing multi-step object creation.",
    "3.10": "Solved constructor parameter explosion using dataclass(kw_only=True) and union types (|).",
    "3.12": "Utilized typing.Self for fluent method chaining without string-forward references.",
}

SCAFFOLD_TEMPLATE = '''"""
Builder Scaffolding Template
"""
from abc import ABC, abstractmethod


class Product:
    def __init__(self) -> None:
        self.parts: list[str] = []


class Builder(ABC):
    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def build_step_a(self) -> None:
        pass

    @abstractmethod
    def build_step_b(self) -> None:
        pass

    @abstractmethod
    def get_result(self) -> Product:
        pass
'''

PATTERN = Pattern(
    id="builder",
    name="Builder",
    chinese_name="生成器",
    category=Category.CREATIONAL,
    intent="分步骤创建复杂对象，允许使用相同的创建代码生成不同类型和形式的对象。",
    problem="复杂对象包含大量字段和可选配置，导致构造函数参数爆炸（重叠构造函数/伸缩构造函数），许多参数传 None 或默认值，可读性和维护性极差。",
    solution="将复杂对象的构建过程抽取为独立的构建步骤，通过 Builder 对象依次调用相应步骤，还可通过主管（Director）类定义标准构建序列。",
    applicability=[
        "使用生成器模式可避免“重叠构造函数（telescoping constructor）”的出现",
        "希望使用代码创建不同形式的产品时（例如不同格式的报告、SQL 查询）",
        "构建复杂的组合树对象或其他复杂对象时",
    ],
    symptoms=[
        "telescoping constructor",
        "constructor parameter explosion",
        "many optional constructor arguments",
        "multi-step object initialization",
        "complex configuration",
    ],
    pros=[
        "可以分步创建对象，暂缓创建步骤或递归运行创建步骤",
        "生成不同形式的产品时可以复用相同的制造代码",
        "单一职责原则：将复杂构造代码与产品的业务逻辑分离",
    ],
    cons=[
        "由于该模式需要创建多个新类，代码整体复杂性会有所增加",
    ],
    relations=[
        "与抽象工厂（Abstract Factory）：抽象工厂侧重于一次性创建产品族，生成器侧重于逐步创建复杂单个对象",
        "与组合（Composite）：生成器常用于逐步构建递归组合树结构",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
