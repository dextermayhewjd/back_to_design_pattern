"""State Design Pattern."""

from design_patterns.models import Category, Pattern

CONCEPTUAL_CODE = '''"""
State - Conceptual Example
"""
from abc import ABC, abstractmethod


class Context:
    _state: "State | None" = None

    def __init__(self, state: "State") -> None:
        self.transition_to(state)

    def transition_to(self, state: "State") -> None:
        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def request1(self) -> None:
        assert self._state is not None
        self._state.handle1()

    def request2(self) -> None:
        assert self._state is not None
        self._state.handle2()


class State(ABC):
    @property
    def context(self) -> Context:
        assert self._context is not None
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def handle1(self) -> None:
        pass

    @abstractmethod
    def handle2(self) -> None:
        pass


class ConcreteStateA(State):
    def handle1(self) -> None:
        print("ConcreteStateA handles request1.")
        print("ConcreteStateA wants to change the state of the context.")
        self.context.transition_to(ConcreteStateB())

    def handle2(self) -> None:
        print("ConcreteStateA handles request2.")


class ConcreteStateB(State):
    def handle1(self) -> None:
        print("ConcreteStateB handles request1.")

    def handle2(self) -> None:
        print("ConcreteStateB handles request2.")
        print("ConcreteStateB wants to change the state of the context.")
        self.context.transition_to(ConcreteStateA())


if __name__ == "__main__":
    context = Context(ConcreteStateA())
    context.request1()
    context.request2()
'''

REALWORLD_CODE = '''"""
State - Real-World Example: Order Processing Lifecycle
"""
from abc import ABC, abstractmethod


class OrderContext:
    def __init__(self) -> None:
        self.state: OrderState = PendingPaymentState()

    def set_state(self, state: "OrderState") -> None:
        self.state = state

    def pay(self) -> str:
        return self.state.pay(self)

    def ship(self) -> str:
        return self.state.ship(self)

    def cancel(self) -> str:
        return self.state.cancel(self)


class OrderState(ABC):
    @abstractmethod
    def pay(self, order: OrderContext) -> str:
        pass

    @abstractmethod
    def ship(self, order: OrderContext) -> str:
        pass

    @abstractmethod
    def cancel(self, order: OrderContext) -> str:
        pass


class PendingPaymentState(OrderState):
    def pay(self, order: OrderContext) -> str:
        order.set_state(PaidState())
        return "Payment processed successfully. Order is now PAID."

    def ship(self, order: OrderContext) -> str:
        return "Cannot ship unpaid order."

    def cancel(self, order: OrderContext) -> str:
        order.set_state(CancelledState())
        return "Order cancelled before payment."


class PaidState(OrderState):
    def pay(self, order: OrderContext) -> str:
        return "Order is already paid."

    def ship(self, order: OrderContext) -> str:
        order.set_state(ShippedState())
        return "Order dispatched for delivery."

    def cancel(self, order: OrderContext) -> str:
        return "Order already paid. Refunding and cancelling."


class ShippedState(OrderState):
    def pay(self, order: OrderContext) -> str:
        return "Order already delivered."

    def ship(self, order: OrderContext) -> str:
        return "Order already shipped."

    def cancel(self, order: OrderContext) -> str:
        return "Cannot cancel order that has already shipped."


class CancelledState(OrderState):
    def pay(self, order: OrderContext) -> str:
        return "Cannot pay cancelled order."

    def ship(self, order: OrderContext) -> str:
        return "Cannot ship cancelled order."

    def cancel(self, order: OrderContext) -> str:
        return "Order is already cancelled."


if __name__ == "__main__":
    order = OrderContext()
    print(order.ship())
    print(order.pay())
    print(order.ship())
'''

SCAFFOLD_TEMPLATE = '''"""
State Scaffolding Template
"""
from abc import ABC, abstractmethod


class Context:
    def __init__(self, initial_state: "State") -> None:
        self.state = initial_state

    def change_state(self, state: "State") -> None:
        self.state = state

    def do_action(self) -> None:
        self.state.handle(self)


class State(ABC):
    @abstractmethod
    def handle(self, context: Context) -> None:
        pass
'''

PATTERN = Pattern(
    id="state",
    name="State",
    chinese_name="状态",
    category=Category.BEHAVIORAL,
    intent="允许一个对象在其内部状态改变时改变它的行为。对象看起来似乎修改了它的类。",
    problem="当一个对象的行为严重取决于其当前状态（例如订单状态机、文档流转审批、网络连接状态），如果在方法中大量使用 `if (state == A) ... else if (state == B)` 分支语句，随着新状态增加，条件逻辑将变得难以理解与维护。",
    solution="将所有与特定状态相关的逻辑分别抽取为一个个独立的状态类（State）。主上下文（Context）持有当前状态对象的引用，并将所有状态相关的请求委派给当前状态对象执行；状态转换也可以在状态类内部触发。",
    applicability=[
        "对象需要根据自身当前状态进行不同行为，同时状态数量非常多且状态代码经常改变时",
        "某个类需要根据属性值进行大量条件语句分支判断时",
        "当相似状态和基于条件的状态转换中存在许多重复代码时",
    ],
    symptoms=[
        "giant switch-case on internal state enum",
        "state machine transition logic",
        "object behavior morphs based on mode/status",
        "order or ticket status workflows",
    ],
    pros=[
        "单一职责原则：将与特定状态相关的代码组织进独立的类中",
        "开闭原则：无需修改已有状态类和上下文即可引入新状态",
        "消除庞大的条件状态机分支语句",
    ],
    cons=[
        "如果状态机只有很少的几个状态或者很少改变，应用该模式可能会显得小题大做",
    ],
    relations=[
        "与策略（Strategy）：状态可以被视为策略模式的扩展，区别在于状态模式中的各个状态对象之间彼此知晓并可以主动触发状态转移，而策略对象通常彼此独立且对上下文无感知",
    ],
    conceptual_code=CONCEPTUAL_CODE,
    realworld_code=REALWORLD_CODE,
    scaffold_template=SCAFFOLD_TEMPLATE,
)
