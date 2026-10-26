"""Flyweight Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Flyweight - Conceptual Example (Classic GoF)
"""
import json


class Flyweight:
    def __init__(self, shared_state: list[str]) -> None:
        self._shared_state = shared_state

    def operation(self, unique_state: list[str]) -> str:
        s = json.dumps(self._shared_state)
        u = json.dumps(unique_state)
        return f"Flyweight: Displaying shared ({s}) and unique ({u}) state."


class FlyweightFactory:
    _flyweights: dict[str, Flyweight] = {}

    def __init__(self, initial_flyweights: list[list[str]]) -> None:
        for state in initial_flyweights:
            self._flyweights[self.get_key(state)] = Flyweight(state)

    def get_key(self, state: list[str]) -> str:
        return "_".join(sorted(state))

    def get_flyweight(self, shared_state: list[str]) -> Flyweight:
        key = self.get_key(shared_state)
        if key not in self._flyweights:
            print(f"FlyweightFactory: Can't find a flyweight, creating new one for {shared_state}.")
            self._flyweights[key] = Flyweight(shared_state)
        else:
            print("FlyweightFactory: Reusing existing flyweight.")
        return self._flyweights[key]

    def list_flyweights(self) -> str:
        count = len(self._flyweights)
        return f"FlyweightFactory: I have {count} flyweights: {list(self._flyweights.keys())}"


if __name__ == "__main__":
    factory = FlyweightFactory([
        ["Chevrolet", "Camaro2018", "pink"],
        ["Mercedes Benz", "C300", "black"],
        ["Mercedes Benz", "C500", "red"],
        ["BMW", "M5", "red"],
        ["BMW", "X6", "white"],
    ])
    print(factory.list_flyweights())

    flyweight = factory.get_flyweight(["BMW", "M5", "red"])
    print(flyweight.operation(["CL234IR", "James Doe"]))
'''

PYTHON310_CODE = '''"""
Flyweight - Python 3.10+ Example: Frozen Slots Dataclass & lru_cache Factory
"""
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True, slots=True)
class TreeType:
    name: str
    color: str
    texture: str


@lru_cache(maxsize=128)
def get_tree_type(name: str, color: str, texture: str) -> TreeType:
    """Flyweight factory: returns cached immutable intrinsic state."""
    return TreeType(name=name, color=color, texture=texture)


@dataclass(slots=True)
class Tree:
    x: int
    y: int
    tree_type: TreeType

    def render(self) -> str:
        return f"Tree '{self.tree_type.name}' at ({self.x}, {self.y})"


if __name__ == "__main__":
    t1 = get_tree_type("Oak", "Green", "rough.png")
    t2 = get_tree_type("Oak", "Green", "rough.png")
    print(f"Flyweights identical: {t1 is t2}")

    forest = [Tree(i, i * 2, t1) for i in range(5)]
    print(f"Planted {len(forest)} trees using 1 flyweight instance.")
    print(forest[0].render())
'''

PYTHON312_CODE = '''"""
Flyweight - Python 3.12+ Example: PEP 695 Generic Flyweight Pool
"""
from collections.abc import Hashable
from dataclasses import dataclass


class FlyweightPool[K: Hashable, V]:
    def __init__(self, factory) -> None:
        self._factory = factory
        self._pool: dict[K, V] = {}

    def get(self, key: K) -> V:
        if key not in self._pool:
            self._pool[key] = self._factory(key)
        return self._pool[key]


@dataclass(frozen=True, slots=True)
class FontStyle:
    font_family: str
    size: int


if __name__ == "__main__":
    pool = FlyweightPool[tuple[str, int], FontStyle](
        factory=lambda k: FontStyle(k[0], k[1])
    )
    f1 = pool.get(("Helvetica", 12))
    f2 = pool.get(("Helvetica", 12))
    print(f"Cached font shared: {f1 is f2}, font: {f1}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Manual factory dictionary cache holding mutable intrinsic state objects.",
    "3.10": "Zero-boilerplate flyweights using @functools.lru_cache and dataclass(frozen=True, slots=True).",
    "3.12": "Type-safe generic flyweight pool FlyweightPool[K: Hashable, V] with PEP 695 syntax.",
}

SCAFFOLD_TEMPLATE = '''"""
Flyweight Scaffolding Template
"""


class Flyweight:
    def __init__(self, shared_intrinsic_state: str) -> None:
        self.shared_state = shared_intrinsic_state

    def operation(self, unique_extrinsic_state: str) -> None:
        print(f"Intrinsic: {self.shared_state}, Extrinsic: {unique_extrinsic_state}")


class FlyweightFactory:
    def __init__(self) -> None:
        self._cache: dict[str, Flyweight] = {}

    def get_flyweight(self, key: str) -> Flyweight:
        if key not in self._cache:
            self._cache[key] = Flyweight(key)
        return self._cache[key]
'''

PATTERN = Pattern(
    id="flyweight",
    name="Flyweight",
    chinese_name="享元",
    category=Category.STRUCTURAL,
    intent="通过摒弃在每个对象中保存所有数据的方式，借由共享多个对象所共有的相同状态，让你能在有限的内存容量中载入更多对象。",
    problem="当系统需要创建海量相似粒度较小的对象（如文字处理器的字符、地图瓦片、粒子特效、游戏内成千上万个NPC），每个对象重复存储大量不变数据会导致内存耗尽崩盘。",
    solution="将对象的内部状态（不变、可共享的状态，如树种、颜色、贴图）与外部状态（随上下文变化、不可共享的状态，如当前坐标位置、大小）拆分，通过享元工厂缓存并共享内部状态对象，调用时将外部状态作为参数传入。",
    applicability=[
        "仅在程序必须支持大量对象且没有足够的内存容量时使用享元模式",
    ],
    symptoms=[
        "high memory usage due to millions of objects",
        "duplicate immutable state across instances",
        "cache shared intrinsic object properties",
        "particle system or text character rendering",
    ],
    pros=[
        "如果程序中原本存在大量相似对象，使用享元可以极大程度节省内存空间",
    ],
    cons=[
        "牺牲了部分运行时间代码复杂度换取内存，代码逻辑变得更加晦涩",
        "每次调用享元方法时需要重新计算或传递外部状态",
    ],
    relations=[
        "与单例（Singleton）：享元通常有多个共享实例且状态不可变；单例只有单个全局可变或不可变实例",
        "与组合（Composite）：享元可以与组合模式结合，将组合树中的共享叶子节点实现为享元",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
