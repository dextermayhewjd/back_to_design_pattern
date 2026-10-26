"""Iterator Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Iterator - Conceptual Example: Pythonic __iter__ and __next__
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

REALWORLD_CODE = '''"""
Iterator - Real-World Example: Paginated API Result Traverser
"""
from collections.abc import Iterator


class PaginatedAPIIterator(Iterator):
    def __init__(self, total_pages: int = 3, per_page: int = 2) -> None:
        self.total_pages = total_pages
        self.per_page = per_page
        self.current_page = 0
        self.buffer: list[str] = []

    def _fetch_next_page(self) -> None:
        if self.current_page < self.total_pages:
            self.current_page += 1
            start_id = (self.current_page - 1) * self.per_page + 1
            self.buffer = [f"Item-{start_id + i}" for i in range(self.per_page)]

    def __next__(self) -> str:
        if not self.buffer:
            self._fetch_next_page()
        if not self.buffer:
            raise StopIteration
        return self.buffer.pop(0)


if __name__ == "__main__":
    api_stream = PaginatedAPIIterator(total_pages=2, per_page=3)
    for record in api_stream:
        print("Processed streaming record:", record)
'''

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
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
