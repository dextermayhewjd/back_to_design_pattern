"""Chain of Responsibility Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Chain of Responsibility - Conceptual Example
"""
from abc import ABC, abstractmethod
from typing import Any


class Handler(ABC):
    @abstractmethod
    def set_next(self, handler: "Handler") -> "Handler":
        pass

    @abstractmethod
    def handle(self, request: Any) -> str | None:
        pass


class AbstractHandler(Handler):
    _next_handler: Handler | None = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request: Any) -> str | None:
        if self._next_handler:
            return self._next_handler.handle(request)
        return None


class MonkeyHandler(AbstractHandler):
    def handle(self, request: Any) -> str | None:
        if request == "Banana":
            return f"Monkey: I'll eat the {request}."
        return super().handle(request)


class SquirrelHandler(AbstractHandler):
    def handle(self, request: Any) -> str | None:
        if request == "Nut":
            return f"Squirrel: I'll eat the {request}."
        return super().handle(request)


class DogHandler(AbstractHandler):
    def handle(self, request: Any) -> str | None:
        if request == "MeatBall":
            return f"Dog: I'll eat the {request}."
        return super().handle(request)


def client_code(handler: Handler) -> None:
    for food in ["Nut", "Banana", "Cup of coffee"]:
        result = handler.handle(food)
        if result:
            print(f"  {result}")
        else:
            print(f"  {food} was left untouched.")


if __name__ == "__main__":
    monkey = MonkeyHandler()
    squirrel = SquirrelHandler()
    dog = DogHandler()

    monkey.set_next(squirrel).set_next(dog)
    client_code(monkey)
'''

REALWORLD_CODE = '''"""
Chain of Responsibility - Real-World Example: HTTP Request Middleware Pipeline
"""
from abc import ABC, abstractmethod


class HTTPRequest:
    def __init__(self, path: str, auth_token: str | None, role: str, body: str) -> None:
        self.path = path
        self.auth_token = auth_token
        self.role = role
        self.body = body


class Middleware(ABC):
    def __init__(self) -> None:
        self._next: Middleware | None = None

    def link_with(self, next_middleware: "Middleware") -> "Middleware":
        self._next = next_middleware
        return next_middleware

    def check(self, request: HTTPRequest) -> bool:
        if self._next is None:
            return True
        return self._next.check(request)


class AuthTokenMiddleware(Middleware):
    def check(self, request: HTTPRequest) -> bool:
        if not request.auth_token or request.auth_token != "secret-token":
            print("[Auth Error] Invalid or missing auth token")
            return False
        return super().check(request)


class RolePermissionMiddleware(Middleware):
    def check(self, request: HTTPRequest) -> bool:
        if request.path.startswith("/admin") and request.role != "ADMIN":
            print(f"[Forbidden] User role '{request.role}' cannot access admin path")
            return False
        return super().check(request)


class RateLimitMiddleware(Middleware):
    def check(self, request: HTTPRequest) -> bool:
        print("[RateLimit] Request passed rate limit check")
        return super().check(request)


if __name__ == "__main__":
    pipeline = AuthTokenMiddleware()
    pipeline.link_with(RolePermissionMiddleware()).link_with(RateLimitMiddleware())

    valid_req = HTTPRequest("/admin/dashboard", "secret-token", "ADMIN", "data")
    print("Valid request passed:", pipeline.check(valid_req))

    unauthorized_req = HTTPRequest("/admin/dashboard", "secret-token", "GUEST", "data")
    print("Guest admin request passed:", pipeline.check(unauthorized_req))
'''

SCAFFOLD_TEMPLATE = '''"""
Chain of Responsibility Scaffolding Template
"""
from abc import ABC, abstractmethod


class Handler(ABC):
    def __init__(self) -> None:
        self._next_handler: Handler | None = None

    def set_next(self, handler: "Handler") -> "Handler":
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request: str) -> str | None:
        if self._next_handler:
            return self._next_handler.handle(request)
        return None
'''

PATTERN = Pattern(
    id="chain-of-responsibility",
    name="Chain of Responsibility",
    chinese_name="责任链",
    category=Category.BEHAVIORAL,
    intent="允许你将请求沿着处理者链进行发送。收到请求后，每个处理者均可对请求进行处理，或将其传递给链上的下一个处理者。",
    problem="当需要按特定顺序对请求执行多个过滤或处理步骤（例如顺序检查身份验证、角色权限限制、缓存、限流与数据净化），把所有逻辑塞进一个巨大的请求处理方法中会导致方法难以扩展，任何条件变动都会牵一发而动全身。",
    solution="将每个特定的行为独立抽取为各个处理者类（Handler）。各个处理者通过链式指针相互连接，接收到请求后依次判定自己是否处理，或将请求直接传递给后继处理者。",
    applicability=[
        "当程序需要使用不同方式处理不同种类请求，而且请求类型和顺序预先未知时",
        "当必须按顺序执行多个处理者时",
        "如果所需处理者及其顺序必须在运行时进行动态指定时",
    ],
    symptoms=[
        "sequential request validation / filtering",
        "http middleware pipeline",
        "multi-step approval workflow",
        "long nested if-else checks on request type",
    ],
    pros=[
        "你可以控制请求处理的顺序",
        "单一职责原则：可以将发起操作和执行操作的类解耦",
        "开闭原则：可以在不更改现有代码的情况下在应用中新增处理者",
    ],
    cons=[
        "部分请求可能未被任何处理者接收并处理（掉出链条末端）",
    ],
    relations=[
        "与命令（Command）：责任链处理者可以处理单个命令对象",
        "与中介者（Mediator）：责任链以链式传递请求，中介者集中消解双向网状通信",
        "与组合（Composite）：责任链常与组合模式一起使用，让叶节点沿着父节点链路冒泡传递请求",
    ],
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
