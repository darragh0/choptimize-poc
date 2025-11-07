"""Display formatting utilities using rich for beautiful terminal output.

This module provides rich formatting for analysis results.
"""

import sys
from typing import Any, Unpack

from rich.console import Group
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from choptimize.display.handles import cerr, cout
from choptimize.display.theme import ICONS
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

    msg_common = f"[status.error]{prefix}[/status.error] {msg}"
    errmsg = (
        msg_common
        if msg_sup is None
        else f"{msg_common}\n [status.error]󱞩[/status.error] {msg_sup}"
    )

    cerr.print(errmsg, **kwargs)
    if then_exit_with is not None:
        sys.exit(then_exit_with)


def _get_display_width() -> int:
    """Calculate consistent display width for all elements.

    Returns:
        Display width in characters.
    """
    terminal_width = cout.width

    if terminal_width >= 120:
        # Large terminals: use max 100 chars with margins
        return min(100, terminal_width - 20)
    elif terminal_width >= 80:
        # Medium terminals: leave 10-char margin
        return terminal_width - 10
    else:
        # Small terminals: leave 4-char margin
        return terminal_width - 4


def _get_score_style(score: float) -> str:
    """Get rich theme style for a score.

    Args:
        score: Score value (1-10)

    Returns:
        Rich theme style name.
    """
    if score >= 9:
        return "score.excellent"
    if score >= 7:
        return "score.good"
    if score >= 5:
        return "score.fair"
    if score >= 3:
        return "score.poor"
    return "score.very_poor"


def _create_section_header(title: str, icon: str | None = None) -> Rule:
    """Create a consistent section header with horizontal rule.

    Args:
        title: Section title
        icon: Optional emoji/icon prefix

    Returns:
        Rich Rule object.
    """
    text = f"{icon} {title}" if icon else title
    return Rule(text, style="heading.primary", align="left")


def _safe_render_markup(text: str) -> Text:
    """Safely render text with markup, falling back to escaped text on error.

    Args:
        text: Text potentially containing rich markup

    Returns:
        Rich Text object.
    """
    try:
        return Text.from_markup(text)
    except Exception:
        # If markup parsing fails, escape and display as-is
        return Text(escape(text))


def _create_overall_score_display(score: float) -> Text:
    """Create formatted overall score display.

    Args:
        score: Overall score (1-10)

    Returns:
        Rich Text object.
    """
    style = _get_score_style(score)
    assessment = get_score_assessment(score)

    text = Text()
    text.append("Overall Score: ", style="label")
    text.append(f"{score}/10", style=style)
    text.append(f" • {assessment}", style="value")

    return text


def _create_metrics_table(analysis: AnalysisResult, width: int) -> Table:
    """Create the quality metrics table.

    Args:
        analysis: Analysis results
        width: Table width

    Returns:
        Rich Table object.
    """
    table = Table(
        show_header=True,
        header_style="table.header",
        border_style="border.accent",
        width=width,
        expand=False,
        show_edge=False,
        pad_edge=False,
    )

    table.add_column("Metric", style="label", no_wrap=True)
    table.add_column("Score", justify="center", style="value")
    table.add_column("Assessment", style="value")

    metrics = [
        ("Specificity", analysis.specificity),
        ("Clarity", analysis.clarity),
        ("Context", analysis.context),
        ("Constraints", analysis.constraints),
        ("Brevity", analysis.brevity),
    ]

    for metric_name, metric in metrics:
        score_style = _get_score_style(metric.score)
        score_text = Text(f"{metric.score}/10", style=score_style)
        assessment = get_score_assessment(metric.score)
        table.add_row(metric_name, score_text, assessment)

    return table


def _create_recommendations_list(recommendations: list[str]) -> Group:
    """Create formatted recommendations list.

    Args:
        recommendations: List of recommendation strings

    Returns:
        Rich Group object.
    """
    items = []
    for i, rec in enumerate(recommendations, 1):
        # Render recommendation with markup enabled
        items.append(_safe_render_markup(f"  [label]{i}.[/label] {rec}"))

    return Group(*items)


def display_analysis(analysis: AnalysisResult, user_prompt: str) -> None:
    """Display complete analysis with improved formatting.

    Args:
        analysis: Analysis results from Gemini
        user_prompt: Original user prompt that was analyzed
    """
    width = _get_display_width()

    # Section 1: Your Prompt
    echo(_create_section_header("Your Prompt", ICONS["prompt"]))
    echo(Panel(
        user_prompt,
        border_style="border.default",
        width=width,
        padding=(0, 1),
    ))
    echo()

    # Section 2: Quality Analysis (Score + Metrics Table)
    echo(_create_section_header("Quality Analysis", ICONS["analysis"]))

    # Create grouped content: score + table
    score_display = _create_overall_score_display(analysis.overall_score)
    metrics_table = _create_metrics_table(analysis, width - 4)  # Account for panel padding

    analysis_group = Group(
        Padding(score_display, (1, 0, 1, 0)),  # Top/bottom padding around score
        metrics_table,
        Padding("", (1, 0, 0, 0)),  # Bottom padding
    )

    echo(Panel(
        analysis_group,
        border_style="border.accent",
        width=width,
        padding=(0, 1),
    ))
    echo()

    # Section 3: Detailed Assessment
    echo(_create_section_header("Detailed Assessment", ICONS["assessment"]))
    echo(Panel(
        _safe_render_markup(analysis.overall_assessment),  # Enable markup rendering
        border_style="border.default",
        width=width,
        padding=(0, 1),
    ))
    echo()

    # Section 4: Recommendations
    if analysis.recommendations:
        echo(_create_section_header("Recommendations", ICONS["recommendations"]))
        recommendations_display = _create_recommendations_list(analysis.recommendations)
        echo(Panel(
            recommendations_display,
            border_style="border.default",
            width=width,
            padding=(0, 1),
        ))
        echo()

    # Section 5: Improved Prompt
    if analysis.improved_prompt:
        echo(_create_section_header("Improved Prompt", ICONS["improved"]))
        echo(Panel(
            _safe_render_markup(analysis.improved_prompt),  # Enable markup rendering
            border_style="border.success",
            width=width,
            padding=(0, 1),
        ))
        echo()
