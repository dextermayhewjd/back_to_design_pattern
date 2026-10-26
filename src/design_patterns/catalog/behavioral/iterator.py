"""Iterator Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Iterator - Conceptual Example: Pythonic __iter__ and __next__ (Classic GoF)
"""
from collections.abc import Iterable, Iterator
from typing import Any


class AlphabeticalOrderIterator(Iterator):
    _position: int = 0
    _reverse: bool = False

    def __init__(self, collection: "WordsCollection", reverse: bool = False) -> None:
        self._collection = collection
        self._reverse = reverse
        self._position = -1 if reverse else 0

    def __next__(self) -> Any:
        try:
            value = self._collection[self._position]
            self._position += -1 if self._reverse else 1
        except IndexError:
            raise StopIteration()
        return value


class WordsCollection(Iterable):
    def __init__(self, collection: list[Any] | None = None) -> None:
        self._collection = collection or []

    def __getitem__(self, index: int) -> Any:
        return self._collection[index]

    def __iter__(self) -> AlphabeticalOrderIterator:
        return AlphabeticalOrderIterator(self)

    def get_reverse_iterator(self) -> AlphabeticalOrderIterator:
        return AlphabeticalOrderIterator(self, reverse=True)

    def add_item(self, item: Any) -> None:
        self._collection.append(item)


if __name__ == "__main__":
    collection = WordsCollection()
    collection.add_item("First")
    collection.add_item("Second")
    collection.add_item("Third")

    print("Straight traversal:")
    print("\\n".join(collection))

    print("\\nReverse traversal:")
    print("\\n".join(collection.get_reverse_iterator()))
'''

PYTHON310_CODE = '''"""
Iterator - Python 3.10+ Example: Generators & yield from
"""
from collections.abc import Iterator


class BinaryTreeNode:
    def __init__(self, value: int, left: "BinaryTreeNode | None" = None, right: "BinaryTreeNode | None" = None) -> None:
        self.value = value
        self.left = left
        self.right = right

    def __iter__(self) -> Iterator[int]:
        """In-order tree traversal via generator."""
        if self.left:
            yield from self.left
        yield self.value
        if self.right:
            yield from self.right


def paginated_fetch(pages: int, per_page: int) -> Iterator[str]:
    """Generator-based streaming pagination."""
    for p in range(1, pages + 1):
        for i in range(1, per_page + 1):
            yield f"Page {p} - Item {i}"


if __name__ == "__main__":
    # Tree traversal using yield from
    root = BinaryTreeNode(10, BinaryTreeNode(5), BinaryTreeNode(15))
    print(f"Tree values in-order: {list(root)}")

    # Streaming items
    for item in paginated_fetch(pages=2, per_page=2):
        print(f"Stream: {item}")
'''

PYTHON312_CODE = '''"""
Iterator - Python 3.12+ Example: PEP 695 Generic Generator & Iterable Protocol
"""
from collections.abc import Iterator


def batch_stream[T](items: list[T], batch_size: int) -> Iterator[list[T]]:
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]


class PipelineSource[T]:
    def __init__(self, data: list[T]) -> None:
        self._data = data

    def __iter__(self) -> Iterator[T]:
        yield from self._data


if __name__ == "__main__":
    src: PipelineSource[int] = PipelineSource([1, 2, 3, 4, 5])
    print(f"Pipelined items: {list(src)}")
    batches = list(batch_stream(["a", "b", "c", "d"], batch_size=2))
    print(f"Batches: {batches}")
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Manual Iterator class with __next__(), StopIteration raising, and state index tracking.",
    "3.10": "Replaced manual iterator classes with Python generators using yield and yield from.",
    "3.12": "Type-safe generic streaming generators batch_stream[T] using PEP 695 syntax.",
}

SCAFFOLD_TEMPLATE = '''"""
Iterator Scaffolding Template
"""
from collections.abc import Iterable, Iterator
from typing import Any


class CustomIterator(Iterator):
    def __init__(self, items: list[Any]) -> None:
        self._items = items
        self._index = 0

    def __next__(self) -> Any:
        if self._index >= len(self._items):
            raise StopIteration
        val = self._items[self._index]
        self._index += 1
        return val


class CustomCollection(Iterable):
    def __init__(self, items: list[Any]) -> None:
        self._items = items

    def __iter__(self) -> CustomIterator:
        return CustomIterator(self._items)
'''

PATTERN = Pattern(
    id="iterator",
    name="Iterator",
    chinese_name="迭代器",
    category=Category.BEHAVIORAL,
    intent="在不暴露集合底层表现形式（列表、栈和树等）的情况下，提供一种顺序访问集合元素的方法。",
    problem="复杂集合（如复杂二叉树、图结构、远程分页集合）具有不同的遍历算法。如果将所有遍历逻辑塞入集合类中，会破坏其存储职责，且客户端需了解集合内部私有结构。",
    solution="将遍历行为抽取为独立的迭代器对象（Iterator）。迭代器封装了遍历算法、当前位置指针以及终止检查，客户端只需通过标准迭代协议（如 Python 的 `__iter__` 与 `__next__`）遍历元素。",
    applicability=[
        "当集合在底层拥有复杂的数据结构，并且你希望对客户端隐藏其复杂性时",
        "使用该模式可以减少程序中重复的遍历代码",
        "如果你希望代码能够遍历不同的甚至无法预知的数据结构时",
    ],
    symptoms=[
        "traverse complex collection without exposing internals",
        "multiple custom traversal algorithms (e.g. depth-first vs breadth-first)",
        "paginated API streaming iteration",
    ],
    pros=[
        "单一职责原则：可以将繁琐的遍历算法从集合业务类中分离",
        "开闭原则：可以实现新型的集合和迭代器并将其传递给现有代码，无需修改已有逻辑",
        "可以并行遍历同一个集合，因为每个迭代器对象都维护自己的迭代状态",
    ],
    cons=[
        "如果应用程序只需处理简单列表，使用迭代器可能会过度设计",
    ],
    relations=[
        "与组合（Composite）：你可以使用迭代器来遍历组合树中的元素",
        "与访问者（Visitor）：你可以同时使用访问者和迭代器来遍历复杂结构并在每个节点执行特定操作",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
