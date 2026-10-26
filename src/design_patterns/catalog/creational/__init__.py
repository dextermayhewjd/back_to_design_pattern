"""Creational patterns collection."""

from design_patterns.catalog.creational.abstract_factory import PATTERN as ABSTRACT_FACTORY
from design_patterns.catalog.creational.builder import PATTERN as BUILDER
from design_patterns.catalog.creational.factory_method import PATTERN as FACTORY_METHOD
from design_patterns.catalog.creational.prototype import PATTERN as PROTOTYPE
from design_patterns.catalog.creational.singleton import PATTERN as SINGLETON
from design_patterns.models import Pattern

CREATIONAL_PATTERNS: list[Pattern] = [
    FACTORY_METHOD,
    ABSTRACT_FACTORY,
    BUILDER,
    PROTOTYPE,
    SINGLETON,
]
