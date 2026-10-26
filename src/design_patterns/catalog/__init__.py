"""Design patterns catalog and master registry loader."""

from design_patterns.catalog.behavioral import BEHAVIORAL_PATTERNS
from design_patterns.catalog.creational import CREATIONAL_PATTERNS
from design_patterns.catalog.structural import STRUCTURAL_PATTERNS
from design_patterns.models import Pattern
from design_patterns.registry import PatternRegistry

ALL_PATTERNS: list[Pattern] = (
    CREATIONAL_PATTERNS + STRUCTURAL_PATTERNS + BEHAVIORAL_PATTERNS
)


def load_default_registry() -> PatternRegistry:
    registry = PatternRegistry()
    for pattern in ALL_PATTERNS:
        registry.register(pattern)
    return registry
