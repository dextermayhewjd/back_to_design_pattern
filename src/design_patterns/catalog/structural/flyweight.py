"""Flyweight Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Flyweight - Conceptual Example
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

REALWORLD_CODE = '''"""
Flyweight - Real-World Example: Forest Tree Rendering (Memory Optimization)
"""


class TreeType:
    def __init__(self, name: str, color: str, texture: str) -> None:
        self.name = name
        self.color = color
        self.texture = texture

    def draw(self, x: int, y: int) -> str:
        return f"Drawing tree '{self.name}' [color={self.color}] at coordinate ({x}, {y})"


class TreeFactory:
    _tree_types: dict[str, TreeType] = {}

    @classmethod
    def get_tree_type(cls, name: str, color: str, texture: str) -> TreeType:
        key = f"{name}_{color}_{texture}"
        if key not in cls._tree_types:
            cls._tree_types[key] = TreeType(name, color, texture)
        return cls._tree_types[key]


class Forest:
    def __init__(self) -> None:
        self.trees: list[tuple[int, int, TreeType]] = []

    def plant_tree(self, x: int, y: int, name: str, color: str, texture: str) -> None:
        type_instance = TreeFactory.get_tree_type(name, color, texture)
        self.trees.append((x, y, type_instance))

    def render(self) -> list[str]:
        return [tree_type.draw(x, y) for x, y, tree_type in self.trees]


if __name__ == "__main__":
    forest = Forest()
    forest.plant_tree(10, 20, "Oak", "Green", "OakTexture.png")
    forest.plant_tree(15, 25, "Oak", "Green", "OakTexture.png")
    forest.plant_tree(30, 40, "Pine", "DarkGreen", "PineTexture.png")

    print(f"Total trees planted: {len(forest.trees)}")
    print(f"Distinct TreeType flyweight objects: {len(TreeFactory._tree_types)}")
    print("\\n".join(forest.render()[:2]))
'''

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
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
