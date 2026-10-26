"""Structural patterns collection."""

from design_patterns.catalog.structural.adapter import PATTERN as ADAPTER
from design_patterns.catalog.structural.bridge import PATTERN as BRIDGE
from design_patterns.catalog.structural.composite import PATTERN as COMPOSITE
from design_patterns.catalog.structural.decorator import PATTERN as DECORATOR
from design_patterns.catalog.structural.facade import PATTERN as FACADE
from design_patterns.catalog.structural.flyweight import PATTERN as FLYWEIGHT
from design_patterns.catalog.structural.proxy import PATTERN as PROXY
from design_patterns.models import Pattern

STRUCTURAL_PATTERNS: list[Pattern] = [
    ADAPTER,
    BRIDGE,
    COMPOSITE,
    DECORATOR,
    FACADE,
    FLYWEIGHT,
    PROXY,
]
