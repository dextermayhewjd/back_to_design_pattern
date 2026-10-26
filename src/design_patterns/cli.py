"""Command line interface for Design Patterns."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from design_patterns.catalog import load_default_registry
from design_patterns.models import Category
from design_patterns.recommender import PatternRecommender
from design_patterns.registry import PatternRegistry


def _pattern_not_found_error(pattern_id: str, registry: PatternRegistry) -> str:
    all_ids = [p.id for p in registry.list_all()]
    matches = difflib.get_close_matches(pattern_id, all_ids, n=3, cutoff=0.6)
    msg = f"Error: Pattern '{pattern_id}' not found.\n"
    if matches:
        msg += f"Did you mean: {', '.join(matches)}?\n"
    msg += "Run 'pat list' to see all available patterns.\n"
    return msg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pat",
        description="Python Design Patterns CLI - RefactoringGuru-faithful patterns, recommender, and code generator.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # list
    list_p = subparsers.add_parser("list", help="List design patterns")
    list_p.add_argument(
        "--category", "-c",
        choices=["creational", "structural", "behavioral"],
        help="Filter by category",
    )
    list_p.add_argument("--json", action="store_true", help="Output as JSON")

    # show
    show_p = subparsers.add_parser("show", help="Show pattern details")
    show_p.add_argument("pattern", help="Pattern identifier (e.g. abstract-factory, strategy)")
    show_p.add_argument("--summary", action="store_true", help="Display a concise summary")
    show_p.add_argument("--json", action="store_true", help="Output as JSON")

    # code
    code_p = subparsers.add_parser("code", help="Print Python implementation code")
    code_p.add_argument("pattern", help="Pattern identifier")
    code_p.add_argument(
        "--type", "-t",
        choices=["conceptual", "realworld"],
        default="conceptual",
        help="Code variant to display (default: conceptual)",
    )
    code_p.add_argument("--json", action="store_true", help="Output code as JSON")

    # scaffold
    scaffold_p = subparsers.add_parser("scaffold", help="Generate boilerplate template")
    scaffold_p.add_argument("pattern", help="Pattern identifier")
    scaffold_p.add_argument("--out", "-o", help="Target output file path")
    scaffold_p.add_argument(
        "--overwrite", "--force",
        dest="overwrite",
        action="store_true",
        help="Overwrite existing destination file",
    )
    scaffold_p.add_argument("--json", action="store_true", help="Output scaffold template as JSON")

    # recommend
    rec_p = subparsers.add_parser("recommend", help="Recommend design patterns based on problem query")
    rec_p.add_argument("--query", "-q", help="Problem description or design symptom")
    rec_p.add_argument("--interactive", "-i", action="store_true", help="Launch interactive diagnostic wizard")
    rec_p.add_argument("--top", type=int, default=3, help="Max recommendations to return (default: 3)")
    rec_p.add_argument("--json", action="store_true", help="Output recommendations as JSON")

    # search (alias to recommend --query)
    search_p = subparsers.add_parser("search", help="Search patterns by problem description or keywords")
    search_p.add_argument("query", help="Problem description or search keyword")
    search_p.add_argument("--top", type=int, default=3, help="Max recommendations to return (default: 3)")
    search_p.add_argument("--json", action="store_true", help="Output recommendations as JSON")
    search_p.set_defaults(interactive=False)

    # diagnose (alias to recommend --interactive)
    diagnose_p = subparsers.add_parser("diagnose", help="Launch interactive diagnostic wizard")
    diagnose_p.add_argument("--json", action="store_true", help="Output recommendations as JSON")
    diagnose_p.set_defaults(interactive=True, query=None, top=3)

    # run
    run_p = subparsers.add_parser("run", help="Execute runnable pattern example")
    run_p.add_argument("pattern", help="Pattern identifier")
    run_p.add_argument(
        "--type", "-t",
        choices=["conceptual", "realworld"],
        default="conceptual",
        help="Example variant to run (default: conceptual)",
    )

    return parser


def handle_list(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    category = Category(args.category) if args.category else None
    patterns = registry.list_all(category)

    if args.json:
        data = [
            {
                "id": p.id,
                "name": p.name,
                "chinese_name": p.chinese_name,
                "category": p.category.value,
                "intent": p.intent,
            }
            for p in patterns
        ]
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print(f"\n{'=' * 75}")
    print(f"{'ID':<26} {'NAME (中文)':<24} {'CATEGORY':<14}")
    print(f"{'=' * 75}")
    for p in patterns:
        display_name = f"{p.name} ({p.chinese_name})"
        print(f"{p.id:<26} {display_name:<24} {p.category.value:<14}")
        print(f"  └─ {p.intent}")
    print(f"{'=' * 75}")
    print(f"Total: {len(patterns)} patterns\n")
    return 0


def handle_show(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    pattern = registry.get(args.pattern)
    if not pattern:
        sys.stderr.write(_pattern_not_found_error(args.pattern, registry))
        return 1

    if getattr(args, "summary", False):
        if args.json:
            data = {
                "id": pattern.id,
                "name": pattern.name,
                "chinese_name": pattern.chinese_name,
                "category": pattern.category.value,
                "intent": pattern.intent,
            }
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return 0
        print(f"\n# {pattern.name} / {pattern.chinese_name} [{pattern.category.value.upper()}]")
        print(f"\n## 意图 (Intent)\n{pattern.intent}\n")
        return 0

    if args.json:
        data = {
            "id": pattern.id,
            "name": pattern.name,
            "chinese_name": pattern.chinese_name,
            "category": pattern.category.value,
            "intent": pattern.intent,
            "problem": pattern.problem,
            "solution": pattern.solution,
            "applicability": pattern.applicability,
            "symptoms": pattern.symptoms,
            "pros": pattern.pros,
            "cons": pattern.cons,
            "relations": pattern.relations,
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print(f"\n# {pattern.name} / {pattern.chinese_name} [{pattern.category.value.upper()}]")
    print(f"\n## 意图 (Intent)\n{pattern.intent}")
    print(f"\n## 问题 (Problem)\n{pattern.problem}")
    print(f"\n## 解决方案 (Solution)\n{pattern.solution}")
    print("\n## 适合应用场景 (Applicability):")
    for app in pattern.applicability:
        print(f"  • {app}")
    print("\n## 优缺点 (Pros & Cons):")
    print("  [优点]")
    for pro in pattern.pros:
        print(f"    ✔ {pro}")
    print("  [缺点]")
    for con in pattern.cons:
        print(f"    ✖ {con}")
    print("\n## 与其他模式的关系 (Relations):")
    for rel in pattern.relations:
        print(f"  → {rel}")
    print("")
    return 0


def handle_code(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    pattern = registry.get(args.pattern)
    if not pattern:
        sys.stderr.write(_pattern_not_found_error(args.pattern, registry))
        return 1

    code = pattern.conceptual_code if args.type == "conceptual" else pattern.realworld_code
    if getattr(args, "json", False):
        data = {
            "id": pattern.id,
            "name": pattern.name,
            "type": args.type,
            "code": code,
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print(code)
    return 0


def handle_scaffold(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    pattern = registry.get(args.pattern)
    if not pattern:
        sys.stderr.write(_pattern_not_found_error(args.pattern, registry))
        return 1

    template = pattern.scaffold_template
    if not args.out:
        if getattr(args, "json", False):
            data = {
                "id": pattern.id,
                "name": pattern.name,
                "scaffold_template": template,
            }
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return 0
        print(template)
        return 0

    target = Path(args.out)
    if target.is_dir():
        sys.stderr.write(f"Error: Target path '{args.out}' is a directory, not a file.\n")
        return 1
    if target.exists() and not args.overwrite:
        sys.stderr.write(f"Error: Target file '{args.out}' already exists. Use --overwrite to replace it.\n")
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template, encoding="utf-8")
    print(f"Successfully generated scaffold for {pattern.name} at: {args.out}")
    return 0


def handle_recommend(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    recommender = PatternRecommender(registry)

    if getattr(args, "interactive", False):
        try:
            results = recommender.run_interactive_wizard()
        except (KeyboardInterrupt, EOFError):
            print("\nDiagnostic cancelled.")
            return 0
    elif getattr(args, "query", None) is not None:
        if not args.query.strip():
            sys.stderr.write("Error: Please provide a query describing your design problem.\n")
            return 1
        results = recommender.recommend(args.query, top_k=getattr(args, "top", 3))
    else:
        sys.stderr.write("Error: Specify a query with -q/--query or run --interactive.\n")
        return 1

    if getattr(args, "json", False):
        data = [
            {
                "id": r.pattern.id,
                "name": r.pattern.name,
                "chinese_name": r.pattern.chinese_name,
                "category": r.pattern.category.value,
                "score": round(r.score, 2),
                "rationale": r.rationale,
                "intent": r.pattern.intent,
            }
            for r in results
        ]
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    if not results:
        print("\nNo matching design pattern found with high confidence.")
        print("Try rephrasing your problem or run 'pat list' to browse all 22 patterns.\n")
        return 0

    print(f"\n{'=' * 75}")
    print("RECOMMENDED DESIGN PATTERNS")
    print(f"{'=' * 75}")
    for idx, r in enumerate(results, 1):
        p = r.pattern
        print(f"[{idx}] {p.name} ({p.chinese_name}) [{p.category.value}] (Score: {r.score:.1f})")
        print(f"    Intent: {p.intent}")
        print(f"    Rationale: {r.rationale}")
        print(f"    Quick view: pat show {p.id}")
        print(f"    Scaffold:   pat scaffold {p.id} --out my_module.py")
        print("-" * 75)
    print("")
    return 0


def handle_run(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    pattern = registry.get(args.pattern)
    if not pattern:
        sys.stderr.write(_pattern_not_found_error(args.pattern, registry))
        return 1

    code = pattern.conceptual_code if args.type == "conceptual" else pattern.realworld_code
    print(f"--- Running {pattern.name} ({args.type}) ---")
    exec_scope: dict = {"__name__": "__main__"}
    try:
        exec(code, exec_scope)
    except Exception as e:
        sys.stderr.write(f"Execution error: {e}\n")
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    handlers = {
        "list": handle_list,
        "show": handle_show,
        "code": handle_code,
        "scaffold": handle_scaffold,
        "recommend": handle_recommend,
        "search": handle_recommend,
        "diagnose": handle_recommend,
        "run": handle_run,
    }

    handler = handlers.get(args.command)
    if not handler:
        parser.print_help()
        return 1

    try:
        return handler(args)
    except (KeyboardInterrupt, EOFError):
        return 0


if __name__ == "__main__":
    sys.exit(main())
