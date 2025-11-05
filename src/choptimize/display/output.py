"""Display formatting utilities using rich for beautiful terminal output.

This module provides rich formatting for analysis results.
"""

import sys
from typing import Any, Unpack

from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from choptimize.display.handles import cerr, cout
from choptimize.display.types import EchoKwargs
from choptimize.types import AnalysisResult, get_score_assessment


def echo(*objects: Any, **kwargs: Unpack[EchoKwargs]) -> None:
    """Shorthand for ``cout.print``"""
    cout.print(*objects, **kwargs)


def echo_err(
    msg: str,
    msg_sup: str | None = None,
    prefix: str = "Error:",
    then_exit_with: int | None = None,
    **kwargs: Unpack[EchoKwargs],
) -> None:
    """Prints error message (via ``cerr.print``)

    Args:
        msg: Error message to display
        msg_sup: Optional supplementary error message

    Optional Keyword Args:
        prefix: Prefix for error message
        then_exit_with: Call ``sys.exit`` with this code
    """

    msg_common = f"[bold red]{prefix}[/bold red] {msg}"
    errmsg = (
        msg_common
        if msg_sup is None
        else f"{msg_common}\n [bold red]󱞩[/bold red] {msg_sup}"
    )

    cerr.print(errmsg, **kwargs)
    if then_exit_with is not None:
        sys.exit(then_exit_with)


def _get_score_style(score: float) -> str:
    """Get rich style for a score

    Args:
        score: Score value (1-10)

    Returns:
        Rich-styled string
    """
    if score >= 8:
        return "bold green"
    if score >= 6:
        return "bold yellow"
    if score >= 4:
        return "bold magenta"
    return "bold red"


def display_analysis(analysis: AnalysisResult, user_prompt: str) -> None:
    """Display complete analysis

    Args:
        analysis: Analysis results from Gemini
        user_prompt: Original user prompt that was analyzed
    """

    # Display original prompt
    echo("[bold]Your Prompt:[/bold]")
    echo(Panel(user_prompt, border_style="dim"), end="\n\n")

    # Display overall assessment
    overall_style = _get_score_style(analysis.overall_score)
    echo(f"[bold]Overall Score:[/bold] [{overall_style}]{analysis.overall_score}/10[/]")
    echo(analysis.overall_assessment, end="\n\n")

    # Display metrics summary table
    table = Table(
        title="Quality Metrics",
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("Metric", style="cyan", width=15)
    table.add_column("Score", justify="center", width=10)
    table.add_column("Assessment", width=20)

    metrics = [
        ("Specificity", analysis.specificity),
        ("Clarity", analysis.clarity),
        ("Context", analysis.context),
        ("Constraints", analysis.constraints),
        ("Brevity", analysis.brevity),
    ]

    for metric_name, metric in metrics:
        score_text = Text(f"{metric.score}/10", style=_get_score_style(metric.score))
        assessment = get_score_assessment(metric.score)
        table.add_row(metric_name, score_text, assessment)

    echo(table, end="\n\n")

    # Display detailed explanations
    echo("[bold magenta]Detailed Analysis[/bold magenta]\n")

    pad = (0, 0, 0, 2)
    for metric_name, metric in metrics:
        # Metric header
        score_style = _get_score_style(metric.score)
        echo(f"[bold]{metric_name}[/bold] ([{score_style}]{metric.score}/10[/])")

        # Explanation
        echo(Padding(metric.explanation, pad))

        # Suggestions
        if metric.suggestions:
            echo()
            echo("  [dim]Suggestions:[/dim]")
            for i, suggestion in enumerate(metric.suggestions, 1):
                echo(f"    [cyan]{i}.[/cyan] {suggestion}")
            echo()

    # Display improved prompt if available
    if analysis.improved_prompt:
        echo("[bold magenta]Improved Prompt[/bold magenta]")
        echo(Panel(analysis.improved_prompt, border_style="green"), end="\n\n")
