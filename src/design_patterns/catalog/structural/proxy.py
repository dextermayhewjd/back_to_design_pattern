"""Proxy Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
Proxy - Conceptual Example
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

REALWORLD_CODE = '''"""
Proxy - Real-World Example: Lazy Loading and Caching Video Downloader
"""
from abc import ABC, abstractmethod


class VideoDownloader(ABC):
    @abstractmethod
    def get_video_data(self, video_id: str) -> str:
        pass


class RealNetworkVideoDownloader(VideoDownloader):
    def get_video_data(self, video_id: str) -> str:
        # Simulate network latency and heavy download
        return f"Heavy binary payload for video {video_id} downloaded from network"


class CachedVideoDownloaderProxy(VideoDownloader):
    def __init__(self, service: VideoDownloader) -> None:
        self._service = service
        self._cache: dict[str, str] = {}

    def get_video_data(self, video_id: str) -> str:
        if video_id not in self._cache:
            print(f"[CACHE MISS] Fetching video {video_id} via network...")
            self._cache[video_id] = self._service.get_video_data(video_id)
        else:
            print(f"[CACHE HIT] Returning video {video_id} from memory.")
        return self._cache[video_id]


if __name__ == "__main__":
    real_service = RealNetworkVideoDownloader()
    proxy = CachedVideoDownloaderProxy(real_service)

    print(proxy.get_video_data("v_101"))
    print(proxy.get_video_data("v_101"))
'''

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
        # Pre-processing (auth, caching, logging)
        result = self.real_service.operation()
        # Post-processing
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
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
