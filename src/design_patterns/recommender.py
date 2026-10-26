"""Pattern recommendation engine and diagnostic wizard."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional
from design_patterns.models import Category, Pattern
from design_patterns.registry import PatternRegistry


@dataclass
class RecommendationResult:
    pattern: Pattern
    score: float
    matched_symptoms: list[str]
    rationale: str


class PatternRecommender:
    def __init__(self, registry: PatternRegistry) -> None:
        self.registry = registry

    def _tokenize(self, text: str) -> set[str]:
        # Split on whitespace and non-alphanumeric (handling English words and Chinese terms)
        words = re.findall(r"[\w]+", text.lower())
        # Filter common English stopwords
        stopwords = {
            "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or",
            "is", "are", "be", "with", "by", "from", "as", "into", "that", "this",
            "my", "our", "their", "want", "need", "like", "how", "what", "which",
            "code", "class", "object", "objects", "classes", "system",
        }
        return {w for w in words if len(w) > 1 and w not in stopwords}

    def recommend(self, query: str, top_k: int = 3) -> list[RecommendationResult]:
        if not query or not query.strip():
            return []

        query_tokens = self._tokenize(query)
        scored_results: list[RecommendationResult] = []

        for pattern in self.registry.list_all():
            score = 0.0
            matched: list[str] = []

            # 1. Full query substring match for Chinese name (e.g. unspaced Chinese sentences)
            if pattern.chinese_name and pattern.chinese_name in query:
                score += 15.0
                matched.append(f"Chinese name match: {pattern.chinese_name}")

            # 2. Direct name match (weight: 15)
            for token in query_tokens:
                if token in pattern.id.lower() or token in pattern.name.lower():
                    score += 15.0
                    matched.append(f"Name match: {token}")
                if token in pattern.chinese_name and f"Chinese name match: {pattern.chinese_name}" not in matched:
                    score += 15.0
                    matched.append(f"Chinese name match: {token}")

            # 3. Symptoms match (weight: 5.0)
            for symptom in pattern.symptoms:
                symptom_tokens = self._tokenize(symptom)
                overlap = query_tokens.intersection(symptom_tokens)
                if overlap:
                    score += 5.0 * len(overlap)
                    for term in overlap:
                        if term not in matched:
                            matched.append(term)

            # 4. Problem text match (weight: 2.0)
            problem_tokens = self._tokenize(pattern.problem)
            problem_overlap = query_tokens.intersection(problem_tokens)
            if problem_overlap:
                score += 2.0 * len(problem_overlap)

            # 5. Intent match (weight: 2.5)
            intent_tokens = self._tokenize(pattern.intent)
            intent_overlap = query_tokens.intersection(intent_tokens)
            if intent_overlap:
                score += 2.5 * len(intent_overlap)

            # 6. Applicability match (weight: 1.5)
            for app in pattern.applicability:
                app_tokens = self._tokenize(app)
                app_overlap = query_tokens.intersection(app_tokens)
                if app_overlap:
                    score += 1.5 * len(app_overlap)

            if score > 0:
                rationale = (
                    f"Matched {len(matched)} key indicators ({', '.join(matched[:3])}) "
                    f"addressing: {pattern.intent[:60]}..."
                )
                scored_results.append(
                    RecommendationResult(
                        pattern=pattern,
                        score=score,
                        matched_symptoms=matched,
                        rationale=rationale,
                    )
                )

        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results[:top_k]

    def run_interactive_wizard(
        self,
        input_fn: Callable[[str], str] | None = None,
        print_fn: Callable[[Any], None] | None = None,
    ) -> list[RecommendationResult]:
        if input_fn is None:
            input_fn = input
        if print_fn is None:
            print_fn = print

        print_fn("=== Design Pattern Diagnostic Wizard ===")
        print_fn("Answer 2-3 quick questions to diagnose the ideal pattern for your design challenge.\n")

        print_fn("Step 1: What is your primary design tension?")
        print_fn("  [1] Object Creation & Initialization (Creational)")
        print_fn("  [2] Class & Object Structure / Compatibility (Structural)")
        print_fn("  [3] Algorithms, Communication & Responsibility Flow (Behavioral)")

        cat_choice = input_fn("Select [1-3]: ").strip()
        category_map = {
            "1": Category.CREATIONAL,
            "2": Category.STRUCTURAL,
            "3": Category.BEHAVIORAL,
        }
        category = category_map.get(cat_choice, Category.BEHAVIORAL)

        pattern_id = "strategy"

        if category == Category.CREATIONAL:
            print_fn("\nStep 2: What is the object creation challenge?")
            print_fn("  [1] Need to create families of related products without concrete classes")
            print_fn("  [2] Delegate instantiation to subclasses based on context")
            print_fn("  [3] Multi-step construction of complex object with many optional fields")
            print_fn("  [4] Clone complex objects dynamically without tight coupling")
            print_fn("  [5] Ensure strictly one global instance with controlled access")
            choice = input_fn("Select [1-5]: ").strip()
            mapping = {
                "1": "abstract-factory",
                "2": "factory-method",
                "3": "builder",
                "4": "prototype",
                "5": "singleton",
            }
            pattern_id = mapping.get(choice, "factory-method")

        elif category == Category.STRUCTURAL:
            print_fn("\nStep 2: What structural issue are you solving?")
            print_fn("  [1] Convert incompatible interface to match target system")
            print_fn("  [2] Decouple abstraction and implementation along independent dimensions")
            print_fn("  [3] Represent part-whole recursive tree hierarchy")
            print_fn("  [4] Dynamically attach additional responsibilities without subclassing")
            print_fn("  [5] Provide a simplified unified entry point to complex subsystem")
            print_fn("  [6] Optimize memory by sharing immutable state across millions of objects")
            print_fn("  [7] Control access, lazy load, or cache results for a heavy service")
            choice = input_fn("Select [1-7]: ").strip()
            mapping = {
                "1": "adapter",
                "2": "bridge",
                "3": "composite",
                "4": "decorator",
                "5": "facade",
                "6": "flyweight",
                "7": "proxy",
            }
            pattern_id = mapping.get(choice, "adapter")

        else:
            print_fn("\nStep 2: What behavioral workflow do you need?")
            print_fn("  [1] Encapsulate interchangeable algorithm variants at runtime")
            print_fn("  [2] Pass request sequentially through a chain of handlers")
            print_fn("  [3] Encapsulate actions with undo/redo/queue capabilities")
            print_fn("  [4] Define algorithm skeleton in base class with customizable hooks")
            print_fn("  [5] 1-to-many publish/subscribe event broadcasting")
            print_fn("  [6] Object behavior changes dynamically when its state changes")
            print_fn("  [7] Save and restore snapshot of internal state without breaking encapsulation")
            print_fn("  [8] Eliminate complex spiderweb dependencies with centralized coordinator")
            print_fn("  [9] Sequentially traverse elements of complex collection without exposing details")
            print_fn("  [10] Execute new operations across stable object structure without altering classes")
            choice = input_fn("Select [1-10]: ").strip()
            mapping = {
                "1": "strategy",
                "2": "chain-of-responsibility",
                "3": "command",
                "4": "template-method",
                "5": "observer",
                "6": "state",
                "7": "memento",
                "8": "mediator",
                "9": "iterator",
                "10": "visitor",
            }
            pattern_id = mapping.get(choice, "strategy")

        pattern = self.registry.get(pattern_id)
        if pattern is None:
            return []

        return [
            RecommendationResult(
                pattern=pattern,
                score=100.0,
                matched_symptoms=["interactive wizard diagnosis"],
                rationale=f"Diagnosed directly via interactive workflow: {pattern.intent}",
            )
        ]
