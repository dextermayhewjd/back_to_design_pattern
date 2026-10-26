"""Proxy Design Pattern."""

from design_patterns.models import Category, Pattern

CLASSIC_CODE = '''"""
Proxy - Conceptual Example (Classic GoF)
"""
from abc import ABC, abstractmethod


class Subject(ABC):
    @abstractmethod
    def request(self) -> str:
        pass


class RealSubject(Subject):
    def request(self) -> str:
        return "RealSubject: Handling request."


class Proxy(Subject):
    def __init__(self, real_subject: RealSubject) -> None:
        self._real_subject = real_subject

    def request(self) -> str:
        if self.check_access():
            result = self._real_subject.request()
            self.log_access()
            return f"Proxy: {result}"
        return "Proxy: Access denied."

    def check_access(self) -> bool:
        print("Proxy: Checking access prior to firing a real request.")
        return True

    def log_access(self) -> None:
        print("Proxy: Logging the time of request.")


def client_code(subject: Subject) -> str:
    return subject.request()


if __name__ == "__main__":
    real_subject = RealSubject()
    print("Client: Executing the client code with a real subject:")
    print(client_code(real_subject))

    proxy = Proxy(real_subject)
    print("\\nClient: Executing the same client code with a proxy:")
    print(client_code(proxy))
'''

PYTHON310_CODE = '''"""
Proxy - Python 3.10+ Example: Dynamic Delegation Proxy & Lazy Loading
"""
from collections.abc import Callable
from typing import Any


class HeavyDatabaseService:
    def __init__(self) -> None:
        print("[DB] Initializing heavy connection pool...")

    def query(self, sql: str) -> str:
        return f"Results for: {sql}"


class LazyProxy:
    def __init__(self, factory: Callable[[], Any]) -> None:
        self._factory = factory
        self._instance: Any | None = None

    def _get_target(self) -> Any:
        if self._instance is None:
            self._instance = self._factory()
        return self._instance

    def __getattr__(self, name: str) -> Any:
        target = self._get_target()
        return getattr(target, name)


if __name__ == "__main__":
    proxy = LazyProxy(HeavyDatabaseService)
    print("Proxy created (DB not yet connected)")
    print(proxy.query("SELECT * FROM users"))
'''

PYTHON312_CODE = '''"""
Proxy - Python 3.12+ Example: PEP 695 Generic Lazy Proxy
"""
from collections.abc import Callable


class HeavyResource:
    def fetch_data(self) -> str:
        return "Heavy payload data loaded"


class LazyProxy[T]:
    def __init__(self, factory: Callable[[], T]) -> None:
        self._factory = factory
        self._target: T | None = None

    @property
    def target(self) -> T:
        if self._target is None:
            self._target = self._factory()
        return self._target

    def get_data(self) -> str:
        return getattr(self.target, "fetch_data")()


if __name__ == "__main__":
    proxy: LazyProxy[HeavyResource] = LazyProxy(HeavyResource)
    print("Proxy initialized without loading heavy resource.")
    print(proxy.get_data())
'''

CONCEPTUAL_CODE = CLASSIC_CODE
REALWORLD_CODE = PYTHON310_CODE

MATRIX_NOTES = {
    "classic": "Heavy Subject base class requiring Proxy and RealSubject to implement identical methods.",
    "3.10": "Dynamic attribute delegation via __getattr__ or functools.cached_property for lazy loading.",
    "3.12": "Type-safe generic lazy initialization wrapper LazyProxy[T] using PEP 695.",
}

SCAFFOLD_TEMPLATE = '''"""
Proxy Scaffolding Template
"""
from abc import ABC, abstractmethod


class ServiceInterface(ABC):
    @abstractmethod
    def operation(self) -> str:
        pass


class RealService(ServiceInterface):
    def operation(self) -> str:
        return "Real Service Operation"


class ServiceProxy(ServiceInterface):
    def __init__(self, real_service: RealService) -> None:
        self.real_service = real_service

    def operation(self) -> str:
        result = self.real_service.operation()
        return result
'''

PATTERN = Pattern(
    id="proxy",
    name="Proxy",
    chinese_name="代理",
    category=Category.STRUCTURAL,
    intent="为其他对象提供一种代理以控制对这个对象的访问。",
    problem="当需要对一个重量级对象执行延迟初始化（Lazy Loading）、访问权限控制、网络通信封装或对结果进行缓存时，直接修改原服务类会混杂非核心职责，且客户端无从得知调用时机。",
    solution="创建一个与原服务对象实现相同接口的代理类（Proxy）。客户端只与代理类交互，代理类在将请求委派给真实服务对象之前或之后，执行额外的访问控制、缓存或日志记录。",
    applicability=[
        "延迟初始化（虚拟代理）：有一个偶尔使用的重量级服务对象，无需一直占用内存",
        "访问控制（保护代理）：只希望特定客户端使用服务对象，代理可验证凭据",
        "本地执行远程服务（远程代理）：服务对象位于远程服务器上",
        "记录日志与请求缓存（日志记录与缓存代理）：缓存客户端请求结果以降低服务负载",
    ],
    symptoms=[
        "lazy loading expensive resources",
        "access control check before execution",
        "caching heavy query or API results",
        "remote service stub",
        "request logging / auditing",
    ],
    pros=[
        "可以在客户端毫无察觉的情况下控制服务对象",
        "如果客户端对服务对象的生命周期没有特殊要求，可以由代理全权管理",
        "即使服务对象还未准备好或不可用，代理依然可以运作",
        "开闭原则：无需修改服务或客户端就能引入新代理",
    ],
    cons=[
        "代码可能会变得更复杂，因为需要引入大量新类",
        "服务响应可能会产生延迟",
    ],
    relations=[
        "与装饰（Decorator）：装饰增强对象行为，代理控制对对象的访问与生命周期",
        "与适配器（Adapter）：适配器提供不同的接口，代理提供相同的接口",
        "与外观（Facade）：外观与代理都缓存/封装复杂实体，但外观定义全新的简化接口，代理遵循服务现有接口",
    ],
    classic_code=CLASSIC_CODE,
    python310_code=PYTHON310_CODE,
    python312_code=PYTHON312_CODE,
    matrix_notes=MATRIX_NOTES,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
