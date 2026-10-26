"""Singleton Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Singleton - Conceptual Example: Metaclass Implementation
"""
from typing import Any


class SingletonMeta(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    def some_business_logic(self) -> str:
        return "Executing singleton operation"


if __name__ == "__main__":
    s1 = Singleton()
    s2 = Singleton()
    print("Same instance:", s1 is s2)
'''

REALWORLD_CODE = '''"""
Singleton - Real-World Example: Thread-Safe Database Connection Pool
"""
from threading import Lock
from typing import Any


class ThreadSafeSingletonMeta(type):
    _instances: dict[type, Any] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class DatabaseConnection(metaclass=ThreadSafeSingletonMeta):
    def __init__(self) -> None:
        self.connected: bool = True

    def query(self, sql: str) -> str:
        return f"Executing {sql} on shared connection {id(self)}"


if __name__ == "__main__":
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    print(db1.query("SELECT 1"))
    print("Shared instance verification:", db1 is db2)
'''

SCAFFOLD_TEMPLATE = '''"""
Singleton Scaffolding Template
"""
from typing import Any


class SingletonMeta(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AppConfig(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.settings: dict[str, Any] = {}
'''

PATTERN = Pattern(
    id="singleton",
    name="Singleton",
    chinese_name="单例",
    category=Category.CREATIONAL,
    intent="保证一个类只有一个实例，并提供一个访问它的全局访问点。",
    problem="某些系统资源（例如全局配置、日志服务或数据库连接池）在整个生命周期内必须只能存在一个实例，多个实例会导致状态冲突或资源竞争。",
    solution="隐藏默认构造函数，通过元类（Metaclass）或类方法拦截对象创建，确保每次调用均返回同一个内部缓存的实例。",
    applicability=[
        "如果程序中的某个类对于所有客户端只有一个可用的实例（如共享数据库连接、系统配置）",
        "需要严格控制全局变量，防止它们被任意随处重写时",
    ],
    symptoms=[
        "global state sharing",
        "duplicate connections",
        "configuration conflict",
        "resource lock contention",
    ],
    pros=[
        "可以保证一个类只有一个实例",
        "获得指向该实例的全局访问节点",
        "仅在首次请求单例对象时对其进行延迟初始化",
    ],
    cons=[
        "违反了单一职责原则（同时负责自身业务逻辑与控制自身生命周期）",
        "在多线程环境下需要特殊处理，且单元测试较难进行 Mock",
    ],
    relations=[
        "与外观（Facade）：外观通常只需一个外观对象，因此常作为单例实现",
        "与抽象工厂（Abstract Factory）：抽象工厂实现通常是单例",
    ],
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
