"""AST Pattern and Code Smell Analyzer Engine.

Detects classic design patterns and "Java-in-Python" anti-patterns across
Python source code using Python's standard library ast module.
"""

from __future__ import annotations

import ast
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class PatternMatch:
    """Represents a detected design pattern occurrence."""

    pattern_id: str
    pattern_name: str
    category: str
    file_path: str
    line_number: int
    evidence: str
    confidence: str = "high"  # "high" | "medium"


@dataclass
class CodeSmell:
    """Represents a detected code smell or anti-pattern."""

    smell_type: str  # e.g. "SINGLE_METHOD_CLASS", "PARAMETER_EXPLOSION", "COMPLEX_BRANCHING", "MANUAL_ITERATOR"
    file_path: str
    line_number: int
    description: str
    recommended_pattern: str
    target_version_baseline: str  # e.g. "Python 3.10+ (Structural Pattern Matching match-case)"
    refactoring_tip: str


@dataclass
class AnalysisReport:
    """Consolidated report of codebase patterns and code smells."""

    files_scanned: int
    total_lines: int
    detected_patterns: list[PatternMatch] = field(default_factory=list)
    code_smells: list[CodeSmell] = field(default_factory=list)
    syntax_errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "files_scanned": self.files_scanned,
            "total_lines": self.total_lines,
            "detected_patterns": [asdict(p) for p in self.detected_patterns],
            "code_smells": [asdict(s) for s in self.code_smells],
            "syntax_errors": self.syntax_errors,
        }


class _ASTAnalyzerVisitor(ast.NodeVisitor):
    """Internal AST visitor to extract patterns and code smells."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.patterns: list[PatternMatch] = []
        self.smells: list[CodeSmell] = []
        self._seen_elifs: set[ast.If] = set()

    # ------------------------------------------------------------------
    # Class-level Analysis
    # ------------------------------------------------------------------

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        methods = [
            m for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        public_methods = [m for m in methods if not m.name.startswith("_")]
        method_names = {m.name for m in methods}

        # Check for smells
        self._check_single_method_class(node, methods, public_methods, method_names)
        self._check_manual_iterator(node, method_names)

        # Check for patterns - Creational
        self._check_factory_method_pattern(node, methods, method_names)
        self._check_abstract_factory_pattern(node, methods, method_names)
        self._check_builder_pattern(node, methods, method_names)
        self._check_prototype_pattern(node, methods, method_names)
        self._check_singleton_pattern(node, methods)

        # Check for patterns - Structural
        self._check_adapter_pattern(node, methods)
        self._check_bridge_pattern(node, methods)
        self._check_composite_pattern(node, methods, method_names)
        self._check_decorator_proxy_pattern(node, methods)
        self._check_facade_pattern(node, methods)
        self._check_flyweight_pattern(node, methods, method_names)

        # Check for patterns - Behavioral
        self._check_chain_of_responsibility_pattern(node, methods, method_names)
        self._check_command_pattern(node, methods, method_names)
        self._check_iterator_pattern(node, method_names)
        self._check_mediator_pattern(node, methods, method_names)
        self._check_memento_pattern(node, method_names)
        self._check_observer_pattern(node, method_names)
        self._check_state_pattern(node, methods, method_names)
        self._check_strategy_pattern(node, methods)
        self._check_template_method_pattern(node, methods)
        self._check_visitor_pattern(node, methods)

        # Continue traversing children
        self.generic_visit(node)

    # ------------------------------------------------------------------
    # Function-level Analysis
    # ------------------------------------------------------------------

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._analyze_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._analyze_function(node)
        self.generic_visit(node)

    def _analyze_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._check_parameter_explosion(node)
        self._check_complex_branching(node)

    # ------------------------------------------------------------------
    # Smell Checkers
    # ------------------------------------------------------------------

    def _check_single_method_class(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        public_methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        # Exclude exception classes and test cases
        is_exception_or_test = any(
            isinstance(b, ast.Name) and b.id in ("Exception", "BaseException", "TestCase")
            for b in node.bases
        )
        if is_exception_or_test:
            return

        # Exclude manual iterators (which define __iter__ and __next__)
        if "__iter__" in method_names and "__next__" in method_names:
            return

        # Exclude classes decorated with @dataclass or @dataclass(...)
        def _is_dataclass(dec: ast.AST) -> bool:
            if isinstance(dec, ast.Name) and dec.id == "dataclass":
                return True
            if isinstance(dec, ast.Attribute) and dec.attr == "dataclass":
                return True
            if isinstance(dec, ast.Call):
                return _is_dataclass(dec.func)
            return False

        if any(_is_dataclass(dec) for dec in node.decorator_list):
            return

        # Exclude classes that contain class-level type annotations (indicating data fields)
        if any(isinstance(stmt, ast.AnnAssign) for stmt in node.body):
            return

        # Class with exactly 1 public method (excluding visitor accept method)
        if len(public_methods) == 1:
            method_name = public_methods[0].name
            if method_name == "accept":
                return

            self.smells.append(
                CodeSmell(
                    smell_type="SINGLE_METHOD_CLASS",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    description=(
                        f"Class '{node.name}' has only 1 public method ('{method_name}'). "
                        "In Python, this is often better expressed as a plain function or Callable strategy."
                    ),
                    recommended_pattern="strategy",
                    target_version_baseline="Python 3.10+ (first-class functions / Callable)",
                    refactoring_tip="Replace single-method class with a plain function or Callable strategy.",
                )
            )

    def _check_parameter_explosion(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        posonly = [a.arg for a in node.args.posonlyargs]
        args = [a.arg for a in node.args.args]
        kwonly = [a.arg for a in node.args.kwonlyargs]
        all_params = posonly + args + kwonly

        # Exclude self and cls receiver parameters
        if all_params and all_params[0] in ("self", "cls"):
            params = all_params[1:]
        else:
            params = all_params

        if len(params) > 5:
            self.smells.append(
                CodeSmell(
                    smell_type="PARAMETER_EXPLOSION",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    description=f"Function/Method '{node.name}' has {len(params)} parameters (> 5).",
                    recommended_pattern="builder",
                    target_version_baseline="Python 3.10+ (dataclass(kw_only=True))",
                    refactoring_tip="Group parameters into a @dataclass with kw_only=True or use Builder.",
                )
            )

    def _check_complex_branching(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        # Collect if statements directly in this function (avoiding nested functions/classes)
        direct_ifs: list[ast.If] = []
        stack: list[ast.AST] = list(ast.iter_child_nodes(node))
        while stack:
            item = stack.pop()
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(item, ast.If):
                direct_ifs.append(item)
            stack.extend(ast.iter_child_nodes(item))

        for if_node in direct_ifs:
            if if_node in self._seen_elifs:
                continue

            # Trace if-elif chain
            branches = 1
            curr = if_node
            while len(curr.orelse) == 1 and isinstance(curr.orelse[0], ast.If):
                branches += 1
                curr = curr.orelse[0]
                self._seen_elifs.add(curr)

            if curr.orelse:
                branches += 1

            if branches > 3:
                self.smells.append(
                    CodeSmell(
                        smell_type="COMPLEX_BRANCHING",
                        file_path=self.file_path,
                        line_number=if_node.lineno,
                        description=f"Function '{node.name}' has complex branching with {branches} branches (> 3).",
                        recommended_pattern="strategy",
                        target_version_baseline="Python 3.10+ (Structural Pattern Matching match-case)",
                        refactoring_tip="Replace chained if-elif branches with match-case or Strategy pattern.",
                    )
                )

    def _check_manual_iterator(
        self, node: ast.ClassDef, method_names: set[str]
    ) -> None:
        if "__iter__" in method_names and "__next__" in method_names:
            self.smells.append(
                CodeSmell(
                    smell_type="MANUAL_ITERATOR",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    description=(
                        f"Class '{node.name}' implements manual iterator protocol (__iter__ and __next__). "
                        "Replace with generator yield."
                    ),
                    recommended_pattern="iterator",
                    target_version_baseline="Python 3.10+ (generator yield / yield from)",
                    refactoring_tip="Replace manual __iter__/__next__ class with a generator function using yield.",
                )
            )

    # ------------------------------------------------------------------
    # Pattern Checkers
    # ------------------------------------------------------------------

    def _check_visitor_pattern(
        self, node: ast.ClassDef, methods: list[ast.FunctionDef | ast.AsyncFunctionDef]
    ) -> None:
        has_accept = any(m.name == "accept" for m in methods)
        has_visit_methods = any(m.name.startswith("visit_") for m in methods)
        inherits_visitor = any(
            (isinstance(b, ast.Name) and "visitor" in b.id.lower())
            or (isinstance(b, ast.Attribute) and "visitor" in b.attr.lower())
            for b in node.bases
        )

        if has_accept or has_visit_methods or inherits_visitor:
            self.patterns.append(
                PatternMatch(
                    pattern_id="visitor",
                    pattern_name="Visitor",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' implements visitor interface (accept method or visit_* methods)",
                    confidence="high",
                )
            )

    def _check_singleton_pattern(
        self, node: ast.ClassDef, methods: list[ast.FunctionDef | ast.AsyncFunctionDef]
    ) -> None:
        # Check __new__ override with instance caching
        new_methods = [m for m in methods if m.name == "__new__"]
        has_singleton_new = False
        if new_methods:
            for sub in ast.walk(new_methods[0]):
                if isinstance(sub, ast.Name) and sub.id in (
                    "_instance",
                    "_instances",
                    "instance",
                    "instances",
                ):
                    has_singleton_new = True
                    break
                if isinstance(sub, ast.Attribute) and sub.attr in (
                    "_instance",
                    "_instances",
                    "instance",
                ):
                    has_singleton_new = True
                    break

            if not has_singleton_new:
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign):
                        for t in stmt.targets:
                            if isinstance(t, ast.Name) and t.id in ("_instance", "_instances"):
                                has_singleton_new = True
                                break

        # Check metaclass singleton
        is_metaclass = any(isinstance(b, ast.Name) and b.id == "type" for b in node.bases)
        has_call = any(m.name == "__call__" for m in methods)
        has_singleton_meta = is_metaclass and has_call

        # Check metaclass usage
        has_singleton_meta_kw = any(
            kw.arg == "metaclass"
            and isinstance(kw.value, ast.Name)
            and "singleton" in kw.value.id.lower()
            for kw in node.keywords
        )

        if has_singleton_new or has_singleton_meta or has_singleton_meta_kw:
            self.patterns.append(
                PatternMatch(
                    pattern_id="singleton",
                    pattern_name="Singleton",
                    category="creational",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' controls instance creation via __new__ or metaclass caching",
                    confidence="high",
                )
            )

    def _check_composite_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        has_add = bool(method_names & {"add", "add_child", "add_component", "append"})
        has_remove = bool(method_names & {"remove", "remove_child", "remove_component"})

        if not (has_add and has_remove):
            return

        has_children_attr = False
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for t in stmt.targets:
                    if isinstance(t, ast.Name) and any(
                        k in t.id.lower() for k in ("child", "children", "component")
                    ):
                        has_children_attr = True

        init_methods = [m for m in methods if m.name == "__init__"]
        if init_methods:
            for sub in ast.walk(init_methods[0]):
                if isinstance(sub, ast.Attribute) and any(
                    k in sub.attr.lower() for k in ("child", "children", "component", "items")
                ):
                    has_children_attr = True
                    break

        name_lower = node.name.lower()
        if has_children_attr or "composite" in name_lower or "group" in name_lower:
            self.patterns.append(
                PatternMatch(
                    pattern_id="composite",
                    pattern_name="Composite",
                    category="structural",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' implements Composite pattern with add/remove child components",
                    confidence="high",
                )
            )

    def _check_decorator_proxy_pattern(
        self, node: ast.ClassDef, methods: list[ast.FunctionDef | ast.AsyncFunctionDef]
    ) -> None:
        wrapped_attrs: set[str] = set()
        init_methods = [m for m in methods if m.name == "__init__"]
        if init_methods:
            for sub in ast.walk(init_methods[0]):
                if isinstance(sub, ast.Assign):
                    for target in sub.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                        ):
                            attr_lower = target.attr.lower()
                            if any(
                                w in attr_lower
                                for w in (
                                    "wrapped",
                                    "component",
                                    "real_subject",
                                    "subject",
                                    "inner",
                                    "target",
                                    "decorated",
                                )
                            ):
                                wrapped_attrs.add(target.attr)

        delegates = False
        if wrapped_attrs:
            for m in methods:
                if m.name.startswith("__"):
                    continue
                for sub in ast.walk(m):
                    if (
                        isinstance(sub, ast.Attribute)
                        and isinstance(sub.value, ast.Attribute)
                        and isinstance(sub.value.value, ast.Name)
                        and sub.value.value.id == "self"
                        and sub.value.attr in wrapped_attrs
                    ):
                        delegates = True
                        break
                if delegates:
                    break

        has_getattr_forwarding = any(m.name == "__getattr__" for m in methods) and bool(
            wrapped_attrs
        )

        if wrapped_attrs and (delegates or has_getattr_forwarding):
            is_proxy = any(
                "proxy" in w or "subject" in w or "target" in w for w in wrapped_attrs
            ) or "proxy" in node.name.lower()

            pattern_id = "proxy" if is_proxy else "decorator"
            pattern_name = "Proxy" if is_proxy else "Decorator"
            evidence = (
                f"Class '{node.name}' wraps and controls access to inner target"
                if is_proxy
                else f"Class '{node.name}' decorates and delegates calls to inner component"
            )

            self.patterns.append(
                PatternMatch(
                    pattern_id=pattern_id,
                    pattern_name=pattern_name,
                    category="structural",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=evidence,
                    confidence="high",
                )
            )

    def _check_observer_pattern(
        self, node: ast.ClassDef, method_names: set[str]
    ) -> None:
        has_subscribe = bool(
            method_names
            & {
                "subscribe",
                "attach",
                "register",
                "add_observer",
                "register_observer",
                "add_listener",
            }
        )
        has_notify = bool(
            method_names
            & {
                "notify",
                "notify_observers",
                "publish",
                "emit",
                "dispatch",
            }
        )

        if has_subscribe and has_notify:
            self.patterns.append(
                PatternMatch(
                    pattern_id="observer",
                    pattern_name="Observer",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' implements Observer pattern with registration and notification methods",
                    confidence="high",
                )
            )

    def _check_template_method_pattern(
        self, node: ast.ClassDef, methods: list[ast.FunctionDef | ast.AsyncFunctionDef]
    ) -> None:
        abstract_methods: set[str] = set()
        for m in methods:
            is_abstract = False
            for dec in m.decorator_list:
                if (isinstance(dec, ast.Name) and dec.id == "abstractmethod") or (
                    isinstance(dec, ast.Attribute) and dec.attr == "abstractmethod"
                ):
                    is_abstract = True
                    break

            if len(m.body) == 1 and isinstance(m.body[0], ast.Raise):
                exc = m.body[0].exc
                if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                    is_abstract = True
                elif isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) and exc.func.id == "NotImplementedError":
                    is_abstract = True

            if is_abstract:
                abstract_methods.add(m.name)

        has_template_call = False
        template_method_name = ""
        if abstract_methods:
            for m in methods:
                if m.name in abstract_methods or m.name.startswith("__"):
                    continue
                for sub in ast.walk(m):
                    if (
                        isinstance(sub, ast.Call)
                        and isinstance(sub.func, ast.Attribute)
                        and isinstance(sub.func.value, ast.Name)
                        and sub.func.value.id == "self"
                        and sub.func.attr in abstract_methods
                    ):
                        has_template_call = True
                        template_method_name = m.name
                        break
                if has_template_call:
                    break

        if has_template_call:
            self.patterns.append(
                PatternMatch(
                    pattern_id="template_method",
                    pattern_name="Template Method",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' defines template method '{template_method_name}' coordinating abstract/hook methods",
                    confidence="high",
                )
            )

    def _check_strategy_pattern(
        self, node: ast.ClassDef, methods: list[ast.FunctionDef | ast.AsyncFunctionDef]
    ) -> None:
        strategy_param_found = False
        init_methods = [m for m in methods if m.name == "__init__"]
        if init_methods:
            init_m = init_methods[0]
            for arg in init_m.args.args + init_m.args.kwonlyargs:
                if arg.arg in ("self", "cls"):
                    continue
                if "strategy" in arg.arg.lower() or "algorithm" in arg.arg.lower():
                    strategy_param_found = True
                    break
                if arg.annotation:
                    try:
                        ann_str = ast.unparse(arg.annotation)
                        if "Callable" in ann_str or "Strategy" in ann_str:
                            strategy_param_found = True
                            break
                    except Exception:
                        pass

        has_strategy_delegation = False
        if strategy_param_found:
            for m in methods:
                if m.name.startswith("__"):
                    continue
                for sub in ast.walk(m):
                    if isinstance(sub, ast.Call):
                        if (
                            isinstance(sub.func, ast.Attribute)
                            and isinstance(sub.func.value, ast.Name)
                            and sub.func.value.id == "self"
                            and any(s in sub.func.attr.lower() for s in ("strategy", "algorithm"))
                        ):
                            has_strategy_delegation = True
                            break
                        if (
                            isinstance(sub.func, ast.Attribute)
                            and isinstance(sub.func.value, ast.Attribute)
                            and isinstance(sub.func.value.value, ast.Name)
                            and sub.func.value.value.id == "self"
                            and any(s in sub.func.value.attr.lower() for s in ("strategy", "algorithm"))
                        ):
                            has_strategy_delegation = True
                            break
                if has_strategy_delegation:
                    break

        name_lower = node.name.lower()
        if strategy_param_found and (
            has_strategy_delegation
            or "strategy" in name_lower
            or "context" in name_lower
        ):
            self.patterns.append(
                PatternMatch(
                    pattern_id="strategy",
                    pattern_name="Strategy",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' uses Strategy pattern accepting interchangeable Callable or algorithm",
                    confidence="high",
                )
            )

    # ------------------------------------------------------------------
    # Additional GoF Pattern Checkers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_abstract_method(m: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        for dec in m.decorator_list:
            if (isinstance(dec, ast.Name) and dec.id == "abstractmethod") or (
                isinstance(dec, ast.Attribute) and dec.attr == "abstractmethod"
            ):
                return True
        if len(m.body) == 1 and isinstance(m.body[0], ast.Raise):
            exc = m.body[0].exc
            if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                return True
            elif (
                isinstance(exc, ast.Call)
                and isinstance(exc.func, ast.Name)
                and exc.func.id == "NotImplementedError"
            ):
                return True
        return False

    @staticmethod
    def _method_returns_self(m: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        for sub in ast.walk(m):
            if (
                isinstance(sub, ast.Return)
                and isinstance(sub.value, ast.Name)
                and sub.value.id == "self"
            ):
                return True
        return False

    def _check_factory_method_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        creation_methods = [
            m
            for m in methods
            if (
                m.name == "factory_method"
                or (
                    m.name.startswith(("create_", "make_"))
                    and m.name not in ("create_memento",)
                )
            )
        ]
        if not creation_methods:
            return

        abstract_creations = [m for m in creation_methods if self._is_abstract_method(m)]
        # If class has 2+ abstract creation methods, it is handled as Abstract Factory
        if len(abstract_creations) >= 2:
            return

        has_explicit = "factory_method" in method_names
        has_abstract_creation = bool(abstract_creations)
        name_lower = node.name.lower()
        inherits_creator = any(
            (isinstance(b, ast.Name) and ("creator" in b.id.lower() or "factory" in b.id.lower()))
            or (isinstance(b, ast.Attribute) and ("creator" in b.attr.lower() or "factory" in b.attr.lower()))
            for b in node.bases
        )
        is_creator_name = "creator" in name_lower or "factory" in name_lower

        if has_explicit or has_abstract_creation or inherits_creator or (is_creator_name and len(creation_methods) == 1):
            method_name = creation_methods[0].name
            self.patterns.append(
                PatternMatch(
                    pattern_id="factory_method",
                    pattern_name="Factory Method",
                    category="creational",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' defines factory method '{method_name}' for deferred object creation",
                    confidence="medium",
                )
            )

    def _check_abstract_factory_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        creation_methods = [
            m
            for m in methods
            if (
                m.name.startswith(("create_", "make_", "produce_"))
                and m.name not in ("create_memento",)
            )
        ]
        abstract_creation = [m for m in creation_methods if self._is_abstract_method(m)]
        inherits_abstract_factory = any(
            (isinstance(b, ast.Name) and "factory" in b.id.lower() and "abstract" in b.id.lower())
            or (isinstance(b, ast.Attribute) and "factory" in b.attr.lower() and "abstract" in b.attr.lower())
            for b in node.bases
        )
        name_lower = node.name.lower()
        is_factory_name = "factory" in name_lower and ("abstract" in name_lower or len(creation_methods) >= 2)

        if len(abstract_creation) >= 2 or (inherits_abstract_factory and len(creation_methods) >= 2) or (is_factory_name and len(creation_methods) >= 2):
            self.patterns.append(
                PatternMatch(
                    pattern_id="abstract_factory",
                    pattern_name="Abstract Factory",
                    category="creational",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' declares multiple factory methods for families of related objects",
                    confidence="medium",
                )
            )

    def _check_builder_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        has_build = bool(method_names & {"build", "get_result", "get_product"})
        has_chaining = any(self._method_returns_self(m) for m in methods)
        has_step_methods = any(
            m.name.startswith(("set_", "with_", "add_", "produce_")) for m in methods
        )
        name_lower = node.name.lower()
        is_builder_name = "builder" in name_lower

        has_construct = bool(method_names & {"construct", "build_minimal", "build_full"})
        takes_builder = False
        init_methods = [m for m in methods if m.name in ("__init__", "construct")]
        for im in init_methods:
            for arg in im.args.args + im.args.kwonlyargs:
                if "builder" in arg.arg.lower():
                    takes_builder = True
                    break

        is_director = (has_construct and takes_builder) or ("director" in name_lower and (has_construct or has_build))

        if (has_build and (has_chaining or has_step_methods or is_builder_name)) or is_director:
            self.patterns.append(
                PatternMatch(
                    pattern_id="builder",
                    pattern_name="Builder",
                    category="creational",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' implements Builder pattern with step-by-step construction and build() method",
                    confidence="medium",
                )
            )

    def _check_prototype_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        has_clone = "clone" in method_names
        has_copy_dunder = bool(method_names & {"__copy__", "__deepcopy__"})
        has_copy_call = False
        for m in methods:
            for sub in ast.walk(m):
                if isinstance(sub, ast.Call):
                    if isinstance(sub.func, ast.Attribute) and sub.func.attr in ("copy", "deepcopy"):
                        has_copy_call = True
                        break
            if has_copy_call:
                break

        name_lower = node.name.lower()
        if has_clone or has_copy_dunder or (has_copy_call and ("prototype" in name_lower or "component" in name_lower or "record" in name_lower)):
            evidence = (
                f"Class '{node.name}' implements clone() method for prototype replication"
                if has_clone
                else f"Class '{node.name}' implements prototype replication (__copy__/__deepcopy__ or copy module)"
            )
            self.patterns.append(
                PatternMatch(
                    pattern_id="prototype",
                    pattern_name="Prototype",
                    category="creational",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=evidence,
                    confidence="high",
                )
            )

    def _check_adapter_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
    ) -> None:
        adaptee_attrs: set[str] = set()
        init_methods = [m for m in methods if m.name == "__init__"]
        if init_methods:
            im = init_methods[0]
            for sub in ast.walk(im):
                if isinstance(sub, ast.Assign):
                    for target in sub.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                        ):
                            attr_lower = target.attr.lower()
                            if any(
                                a in attr_lower
                                for a in ("adaptee", "legacy", "old_", "external", "third_party", "backend")
                            ):
                                adaptee_attrs.add(target.attr)
            for arg in im.args.args + im.args.kwonlyargs:
                if any(a in arg.arg.lower() for a in ("adaptee", "legacy")):
                    adaptee_attrs.add(arg.arg)

        delegates = False
        if adaptee_attrs:
            for m in methods:
                if m.name.startswith("__"):
                    continue
                for sub in ast.walk(m):
                    if (
                        isinstance(sub, ast.Attribute)
                        and isinstance(sub.value, ast.Attribute)
                        and isinstance(sub.value.value, ast.Name)
                        and sub.value.value.id == "self"
                        and (
                            sub.value.attr in adaptee_attrs
                            or any(a in sub.value.attr.lower() for a in ("adaptee", "legacy"))
                        )
                    ):
                        delegates = True
                        break
                if delegates:
                    break

        name_lower = node.name.lower()
        is_adapter_name = "adapter" in name_lower

        if (is_adapter_name and (adaptee_attrs or delegates or len(methods) >= 2)) or (adaptee_attrs and delegates):
            self.patterns.append(
                PatternMatch(
                    pattern_id="adapter",
                    pattern_name="Adapter",
                    category="structural",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' adapts incompatible interface of adaptee to target interface",
                    confidence="medium",
                )
            )

    def _check_bridge_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
    ) -> None:
        impl_attrs: set[str] = set()
        init_methods = [m for m in methods if m.name == "__init__"]
        if init_methods:
            im = init_methods[0]
            for sub in ast.walk(im):
                if isinstance(sub, ast.Assign):
                    for target in sub.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                        ):
                            attr_lower = target.attr.lower()
                            if any(
                                k in attr_lower
                                for k in ("impl", "implementor", "implementation", "device", "renderer", "platform")
                            ):
                                impl_attrs.add(target.attr)
            for arg in im.args.args + im.args.kwonlyargs:
                if any(k in arg.arg.lower() for k in ("impl", "implementor", "implementation", "device")):
                    impl_attrs.add(arg.arg)

        delegates = False
        if impl_attrs:
            for m in methods:
                if m.name.startswith("__"):
                    continue
                for sub in ast.walk(m):
                    if (
                        isinstance(sub, ast.Attribute)
                        and isinstance(sub.value, ast.Attribute)
                        and isinstance(sub.value.value, ast.Name)
                        and sub.value.value.id == "self"
                        and (
                            sub.value.attr in impl_attrs
                            or any(k in sub.value.attr.lower() for k in ("impl", "device"))
                        )
                    ):
                        delegates = True
                        break
                if delegates:
                    break

        name_lower = node.name.lower()
        is_bridge_name = "bridge" in name_lower or "abstraction" in name_lower

        if (impl_attrs and delegates) or (is_bridge_name and (impl_attrs or delegates)):
            self.patterns.append(
                PatternMatch(
                    pattern_id="bridge",
                    pattern_name="Bridge",
                    category="structural",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' decouples abstraction from implementation via delegated implementor",
                    confidence="medium",
                )
            )

    def _check_facade_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
    ) -> None:
        name_lower = node.name.lower()
        is_facade_name = "facade" in name_lower

        subsystem_attrs: set[str] = set()
        init_methods = [m for m in methods if m.name == "__init__"]
        if init_methods:
            im = init_methods[0]
            for sub in ast.walk(im):
                if isinstance(sub, ast.Assign):
                    for target in sub.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                        ):
                            attr_name = target.attr
                            if "subsystem" in attr_name.lower() or "service" in attr_name.lower():
                                subsystem_attrs.add(attr_name)
                            elif isinstance(sub.value, ast.Call) and not attr_name.startswith("__"):
                                subsystem_attrs.add(attr_name)
                            elif isinstance(sub.value, ast.BoolOp):
                                subsystem_attrs.add(attr_name)
            for arg in im.args.args + im.args.kwonlyargs:
                if "subsystem" in arg.arg.lower() or "service" in arg.arg.lower():
                    subsystem_attrs.add(arg.arg)

        used_subsystems: set[str] = set()
        if len(subsystem_attrs) >= 2:
            for m in methods:
                if m.name.startswith("__"):
                    continue
                for sub in ast.walk(m):
                    if (
                        isinstance(sub, ast.Call)
                        and isinstance(sub.func, ast.Attribute)
                        and isinstance(sub.func.value, ast.Attribute)
                        and isinstance(sub.func.value.value, ast.Name)
                        and sub.func.value.value.id == "self"
                        and sub.func.value.attr in subsystem_attrs
                    ):
                        used_subsystems.add(sub.func.value.attr)

        orchestrates = len(used_subsystems) >= 2

        if is_facade_name or orchestrates:
            self.patterns.append(
                PatternMatch(
                    pattern_id="facade",
                    pattern_name="Facade",
                    category="structural",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' provides a unified facade interface coordinating multiple subsystems",
                    confidence="medium",
                )
            )

    def _check_flyweight_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        has_pool_attr = False
        name_lower = node.name.lower()
        is_flyweight_name = "flyweight" in name_lower

        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for t in stmt.targets:
                    if isinstance(t, ast.Name) and any(
                        k in t.id.lower() for k in ("_pool", "pool", "_cache", "_flyweights", "flyweights")
                    ):
                        has_pool_attr = True
            elif isinstance(stmt, ast.AnnAssign):
                if isinstance(stmt.target, ast.Name) and any(
                    k in stmt.target.id.lower() for k in ("_pool", "pool", "_cache", "_flyweights", "flyweights")
                ):
                    has_pool_attr = True

        init_methods = [m for m in methods if m.name in ("__init__", "__new__")]
        if init_methods:
            for sub in ast.walk(init_methods[0]):
                if isinstance(sub, ast.Attribute) and any(
                    k in sub.attr.lower() for k in ("_pool", "pool", "_cache", "_flyweights", "flyweights")
                ):
                    has_pool_attr = True

        has_cache_lookup = False
        for m in methods:
            for sub in ast.walk(m):
                if isinstance(sub, ast.Compare):
                    for comp in sub.comparators:
                        if isinstance(comp, ast.Attribute) and any(
                            k in comp.attr.lower() for k in ("pool", "flyweights", "cache")
                        ):
                            has_cache_lookup = True
                            break
                        elif isinstance(comp, ast.Name) and any(
                            k in comp.id.lower() for k in ("pool", "flyweights", "cache")
                        ):
                            has_cache_lookup = True
                            break

        has_get_flyweight = bool(method_names & {"get_flyweight", "list_flyweights"}) or any(
            m.name.startswith("get_") and "flyweight" in m.name.lower() for m in methods
        )

        if (has_pool_attr and (has_cache_lookup or is_flyweight_name)) or (is_flyweight_name and (has_pool_attr or has_get_flyweight)):
            self.patterns.append(
                PatternMatch(
                    pattern_id="flyweight",
                    pattern_name="Flyweight",
                    category="structural",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' manages shared intrinsic state pool/cache for Flyweight instances",
                    confidence="high",
                )
            )

    def _check_chain_of_responsibility_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        has_set_next = "set_next" in method_names
        has_next_attr = False

        for stmt in node.body:
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                target = stmt.targets[0] if isinstance(stmt, ast.Assign) else stmt.target
                if isinstance(target, ast.Name) and any(
                    k in target.id.lower() for k in ("_next_handler", "next_handler", "_next", "successor")
                ):
                    has_next_attr = True

        init_methods = [m for m in methods if m.name in ("__init__", "set_next")]
        for im in init_methods:
            for sub in ast.walk(im):
                if isinstance(sub, ast.Attribute) and any(
                    k in sub.attr.lower() for k in ("_next_handler", "next_handler", "_next", "successor")
                ):
                    has_next_attr = True

        forwards_to_next = False
        for m in methods:
            for sub in ast.walk(m):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                    if sub.func.attr == "handle":
                        forwards_to_next = True
                        break

        name_lower = node.name.lower()
        is_handler_name = "handler" in name_lower or "chain" in name_lower

        if has_set_next or (has_next_attr and forwards_to_next) or (is_handler_name and has_next_attr):
            self.patterns.append(
                PatternMatch(
                    pattern_id="chain_of_responsibility",
                    pattern_name="Chain of Responsibility",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' implements Chain of Responsibility with sequential handler passing",
                    confidence="high",
                )
            )

    def _check_command_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        has_execute = "execute" in method_names
        has_undo = bool(method_names & {"undo", "redo"})
        inherits_command = any(
            (isinstance(b, ast.Name) and "command" in b.id.lower())
            or (isinstance(b, ast.Attribute) and "command" in b.attr.lower())
            for b in node.bases
        )
        name_lower = node.name.lower()
        is_command_name = name_lower.endswith("command") or name_lower == "command"
        has_invoker_methods = bool(method_names & {"set_command", "execute_command", "add_command"})

        if (has_execute and has_undo) or (inherits_command and has_execute) or (is_command_name and has_execute) or has_invoker_methods:
            self.patterns.append(
                PatternMatch(
                    pattern_id="command",
                    pattern_name="Command",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' encapsulates request as Command with execute() and undo() methods",
                    confidence="high",
                )
            )

    def _check_iterator_pattern(
        self,
        node: ast.ClassDef,
        method_names: set[str],
    ) -> None:
        has_iter = "__iter__" in method_names
        has_next = "__next__" in method_names
        inherits_iterator = any(
            (isinstance(b, ast.Name) and b.id in ("Iterator", "Iterable"))
            or (isinstance(b, ast.Attribute) and b.attr in ("Iterator", "Iterable"))
            for b in node.bases
        )

        if (has_iter and has_next) or (inherits_iterator and has_next):
            self.patterns.append(
                PatternMatch(
                    pattern_id="iterator",
                    pattern_name="Iterator",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' implements iterator protocol (__iter__ and __next__)",
                    confidence="high",
                )
            )

    def _check_mediator_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        name_lower = node.name.lower()
        is_mediator_name = "mediator" in name_lower

        has_mediator_notify = False
        for m in methods:
            if m.name == "notify" and len(m.args.args) >= 3:
                has_mediator_notify = True
                break

        calls_mediator_notify = False
        for m in methods:
            for sub in ast.walk(m):
                if (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Attribute)
                    and sub.func.attr == "notify"
                    and isinstance(sub.func.value, ast.Attribute)
                    and isinstance(sub.func.value.value, ast.Name)
                    and sub.func.value.value.id == "self"
                    and "mediator" in sub.func.value.attr.lower()
                ):
                    calls_mediator_notify = True
                    break
            if calls_mediator_notify:
                break

        has_mediator_attr = False
        init_methods = [m for m in methods if m.name == "__init__"]
        if init_methods:
            for arg in init_methods[0].args.args + init_methods[0].args.kwonlyargs:
                if "mediator" in arg.arg.lower():
                    has_mediator_attr = True

        if (is_mediator_name and (has_mediator_notify or len(methods) >= 1)) or has_mediator_notify or (calls_mediator_notify and has_mediator_attr):
            self.patterns.append(
                PatternMatch(
                    pattern_id="mediator",
                    pattern_name="Mediator",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' coordinates component communication via Mediator pattern",
                    confidence="high",
                )
            )

    def _check_memento_pattern(
        self,
        node: ast.ClassDef,
        method_names: set[str],
    ) -> None:
        has_save = bool(method_names & {"save", "create_memento", "save_state", "backup"})
        has_restore = bool(method_names & {"restore", "restore_memento", "restore_state", "undo"})

        name_lower = node.name.lower()
        is_memento_name = "memento" in name_lower or "caretaker" in name_lower or "originator" in name_lower

        if (has_save and has_restore) or (is_memento_name and (has_save or has_restore or "get_state" in method_names)):
            self.patterns.append(
                PatternMatch(
                    pattern_id="memento",
                    pattern_name="Memento",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' captures and restores internal state snapshots (Memento pattern)",
                    confidence="high",
                )
            )

    def _check_state_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        has_transition = bool(method_names & {"transition_to", "change_state", "set_state"})

        has_state_attr = False
        init_methods = [m for m in methods if m.name == "__init__"]
        if init_methods:
            for sub in ast.walk(init_methods[0]):
                if isinstance(sub, ast.Attribute) and sub.attr.lower() in ("_state", "state"):
                    has_state_attr = True

        for stmt in node.body:
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                target = stmt.targets[0] if isinstance(stmt, ast.Assign) else stmt.target
                if isinstance(target, ast.Name) and target.id.lower() in ("_state", "state"):
                    has_state_attr = True

        inherits_state = any(
            (isinstance(b, ast.Name) and "state" in b.id.lower())
            or (isinstance(b, ast.Attribute) and "state" in b.attr.lower())
            for b in node.bases
        )
        name_lower = node.name.lower()
        is_state_name = name_lower.endswith("state") or name_lower == "state"

        delegates_to_state = False
        for m in methods:
            if m.name.startswith("__"):
                continue
            for sub in ast.walk(m):
                if (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Attribute)
                    and isinstance(sub.func.value, ast.Attribute)
                    and isinstance(sub.func.value.value, ast.Name)
                    and sub.func.value.value.id == "self"
                    and sub.func.value.attr in ("_state", "state")
                ):
                    delegates_to_state = True
                    break
            if delegates_to_state:
                break

        has_abstract = any(self._is_abstract_method(m) for m in methods)

        if (
            (has_transition and (has_state_attr or delegates_to_state))
            or (has_state_attr and delegates_to_state)
            or (is_state_name and has_abstract)
            or (inherits_state and not is_state_name)
            or (is_state_name and inherits_state)
        ):
            self.patterns.append(
                PatternMatch(
                    pattern_id="state",
                    pattern_name="State",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' alters behavior when its internal state changes (State pattern)",
                    confidence="medium",
                )
            )


class CodebaseAnalyzer:
    """AST analyzer that detects design patterns and anti-patterns."""

    def analyze_source(
        self, source: str, file_path: str = "<memory>"
    ) -> tuple[list[PatternMatch], list[CodeSmell]]:
        """Parse source code string and detect patterns and code smells.

        Raises SyntaxError if source has invalid syntax.
        """
        tree = ast.parse(source, filename=file_path)
        visitor = _ASTAnalyzerVisitor(file_path=file_path)
        visitor.visit(tree)
        return visitor.patterns, visitor.smells

    def analyze_path(self, path: Path | str) -> AnalysisReport:
        """Analyze a file or directory recursively and return an AnalysisReport.

        Ignores hidden directories/files (starting with .) and __pycache__.
        Recovers gracefully from SyntaxError and UnicodeDecodeError.
        Raises FileNotFoundError if path does not exist.
        """
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        report = AnalysisReport(files_scanned=0, total_lines=0)

        if target.is_file():
            self._scan_file(target, report)
            return report

        for root, dirs, files in os.walk(target):
            # Exclude hidden directories and __pycache__ in-place
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d != "__pycache__"
            ]

            for file_name in sorted(files):
                if file_name.startswith(".") or not file_name.endswith(".py"):
                    continue

                file_path = Path(root) / file_name
                self._scan_file(file_path, report)

        return report

    def _scan_file(self, file_path: Path, report: AnalysisReport) -> None:
        try:
            source = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            report.syntax_errors.append(f"{file_path}: {e}")
            return

        lines = len(source.splitlines())
        report.total_lines += lines
        report.files_scanned += 1

        try:
            patterns, smells = self.analyze_source(source, file_path=str(file_path))
            report.detected_patterns.extend(patterns)
            report.code_smells.extend(smells)
        except SyntaxError as e:
            report.syntax_errors.append(f"{file_path}: {e}")
