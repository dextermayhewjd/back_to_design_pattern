"""Behavioral patterns collection."""

from design_patterns.catalog.behavioral.chain_of_responsibility import PATTERN as CHAIN_OF_RESPONSIBILITY
from design_patterns.catalog.behavioral.command import PATTERN as COMMAND
from design_patterns.catalog.behavioral.iterator import PATTERN as ITERATOR
from design_patterns.catalog.behavioral.mediator import PATTERN as MEDIATOR
from design_patterns.catalog.behavioral.memento import PATTERN as MEMENTO
from design_patterns.catalog.behavioral.observer import PATTERN as OBSERVER
from design_patterns.catalog.behavioral.state import PATTERN as STATE
from design_patterns.catalog.behavioral.strategy import PATTERN as STRATEGY
from design_patterns.catalog.behavioral.template_method import PATTERN as TEMPLATE_METHOD
from design_patterns.catalog.behavioral.visitor import PATTERN as VISITOR
from design_patterns.models import Pattern

BEHAVIORAL_PATTERNS: list[Pattern] = [
    CHAIN_OF_RESPONSIBILITY,
    COMMAND,
    ITERATOR,
    MEDIATOR,
    MEMENTO,
    OBSERVER,
    STATE,
    STRATEGY,
    TEMPLATE_METHOD,
    VISITOR,
]
