"""Command-line interface for soap-calc."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from soap_calc.calculator import calculate
from soap_calc.export import export_markdown, render_markdown
from soap_calc.oils import list_oils, search_oils
from soap_calc.recipe_io import load_recipe, save_recipe, scale_recipe
from soap_calc.validation import validate


def _load_or_exit(path: str) -> "Recipe":  # noqa: F821
    """Load a recipe file, printing a friendly error and exiting on failure.

    Args:
        path: Path to the recipe file (JSON or YAML).

    Returns:
        Loaded Recipe object.

    Raises:
        SystemExit: If the file is not found or cannot be loaded.
    """
    from soap_calc.models import Recipe  # deferred to avoid circular import
    try:
        return load_recipe(path)
    except FileNotFoundError:
        print(f"Error: recipe file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error: could not load recipe: {exc}", file=sys.stderr)
        sys.exit(1)


def _cmd_calculate(args: argparse.Namespace) -> None:
    """Execute the calculate command.

    Loads a recipe, performs saponification calculations, and prints results
    as formatted Markdown to stdout.

    Args:
        args: Parsed command-line arguments containing recipe path and optional
            oil_weight override.
    """
    recipe = _load_or_exit(args.recipe)
    oil_wt = getattr(args, "oil_weight", None)
    result = calculate(recipe, oil_weight=oil_wt)
    print(render_markdown(recipe, result))


def _cmd_export(args: argparse.Namespace) -> None:
    """Execute the export command.

    Loads a recipe, performs calculations, and exports results as a Markdown
    file. If no output path is specified, uses the recipe filename with .md
    extension.

    Args:
        args: Parsed command-line arguments containing recipe path, optional
            output path, and optional oil_weight override.
    """
    recipe = _load_or_exit(args.recipe)
    oil_wt = getattr(args, "oil_weight", None)
    result = calculate(recipe, oil_weight=oil_wt)
    out = args.output or Path(args.recipe).with_suffix(".md")
    export_markdown(recipe, result, out)
    print(f"Exported to {out}")


def _cmd_validate(args: argparse.Namespace) -> None:
    """Execute the validate command.

    Loads a recipe and checks it for formulation warnings (e.g., property
    ranges, missing fields). Prints warnings to stdout and exits with code 1
    if any warnings are found, or prints success message and exits with code 0
    if no warnings are found.

    Args:
        args: Parsed command-line arguments containing recipe path.

    Raises:
        SystemExit: Exits with code 1 if warnings are found, 0 otherwise.
    """
    recipe = _load_or_exit(args.recipe)
    warnings = validate(recipe)
    if warnings:
        for w in warnings:
            print(f"⚠️  {w}")
        sys.exit(1)
    else:
        print("✅ No warnings.")


def _cmd_list_oils(args: argparse.Namespace) -> None:
    """Execute the list-oils command.

    Lists oils from the database in a formatted table showing NaOH SAP, KOH SAP,
    iodine value, and INS value. If a query is provided, performs fuzzy search
    to filter results.

    Args:
        args: Parsed command-line arguments containing optional query string.
    """
    query = args.query
    oils = search_oils(query) if query else list_oils()
    if not oils:
        print("No matching oils found.")
        return
    print(f"{'Oil':<35} {'NaOH SAP':>10} {'KOH SAP':>10} {'Iodine':>8} {'INS':>6}")
    print("-" * 75)
    for o in oils:
        print(f"{o.name:<35} {o.sap_naoh:>10.4f} {o.sap_koh:>10.4f} {o.iodine:>8.0f} {o.ins:>6.0f}")


def _cmd_scale(args: argparse.Namespace) -> None:
    """Execute the scale command.

    Loads a recipe and scales it to a target oil weight. If an output path is
    specified, saves the scaled recipe to file. Otherwise, calculates and prints
    the scaled recipe as formatted Markdown to stdout.

    Args:
        args: Parsed command-line arguments containing recipe path, target_oil
            weight in grams, and optional output path.
    """
    recipe = _load_or_exit(args.recipe)
    new_recipe = scale_recipe(recipe, args.target_oil)
    out = args.output
    if out:
        save_recipe(new_recipe, out)
        print(f"Scaled recipe saved to {out}")
    else:
        result = calculate(new_recipe)
        print(render_markdown(new_recipe, result))


def _add_oil_weight_arg(parser: argparse.ArgumentParser) -> None:
    """Add the --oil-weight argument to a subcommand parser.

    Args:
        parser: ArgumentParser subcommand to add the oil weight argument to.
    """
    parser.add_argument(
        "--oil-weight", type=float, default=None,
        help="Override total oil weight in grams (ignores recipe default / mold).",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the soap-calc CLI.

    Creates the main parser and all subcommand parsers (calculate, export,
    validate, list-oils, scale) with their respective arguments and handlers.

    Returns:
        Configured ArgumentParser with all subcommands registered.
    """
    parser = argparse.ArgumentParser(
        prog="soap-calc",
        description="Saponification calculator for soap makers.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # calculate
    p_calc = sub.add_parser("calculate", aliases=["calc"], help="Calculate a recipe and display results.")
    p_calc.add_argument("recipe", help="Path to recipe file (JSON or YAML).")
    _add_oil_weight_arg(p_calc)
    p_calc.set_defaults(func=_cmd_calculate)

    # export
    p_export = sub.add_parser("export", help="Export recipe to Markdown.")
    p_export.add_argument("recipe", help="Path to recipe file.")
    p_export.add_argument("-o", "--output", help="Output Markdown file path.")
    _add_oil_weight_arg(p_export)
    p_export.set_defaults(func=_cmd_export)

    # validate
    p_val = sub.add_parser("validate", help="Check a recipe for warnings.")
    p_val.add_argument("recipe", help="Path to recipe file.")
    p_val.set_defaults(func=_cmd_validate)

    # list-oils
    p_oils = sub.add_parser("list-oils", help="List oils in the database.")
    p_oils.add_argument("query", nargs="?", default="", help="Optional search query.")
    p_oils.set_defaults(func=_cmd_list_oils)

    # scale
    p_scale = sub.add_parser("scale", help="Scale a recipe to a target oil weight.")
    p_scale.add_argument("recipe", help="Path to recipe file.")
    p_scale.add_argument("target_oil", type=float, help="Target total oil weight in grams.")
    p_scale.add_argument("-o", "--output", help="Output file path (JSON/YAML). If omitted, prints to stdout.")
    p_scale.set_defaults(func=_cmd_scale)

    return parser


def main(argv: list[str] | None = None) -> None:
    """Main entry point for the soap-calc CLI.

    Parses command-line arguments and dispatches to the appropriate subcommand
    handler function.

    Args:
        argv: Command-line arguments to parse. If None, uses sys.argv.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
