"""Main prompt analyzer orchestrator.

This module coordinates the analysis of coding prompts.
"""

from choptimize.api import gemini_client as client
from choptimize.types import AnalysisResult


class PromptAnalysisError(Exception):
    """Raised when there's an error analyzing a prompt"""


def analyze_prompt(
    user_prompt: str,
) -> AnalysisResult:
    """Analyze a user's coding prompt

    Args:
        user_prompt: Prompt to analyze
        config: Optional Gemini configuration. If None, creates new config.

    Returns:
        AnalysisResult with complete analysis.

    Raises:
        PromptAnalysisError: If the prompt is not coding-related (and not skipped)
                           or if there's an error during analysis.
    """
    try:
        config = client.create_gemini_config()
    except KeyError as e:
        raise PromptAnalysisError(f"Configuration error: {e}") from e

    # Single API call that handles both validation and analysis
    # The SYSTEM_INSTRUCTIONS already include validation logic
    try:
        analysis_dict = client.analyze_prompt(config, user_prompt)
    except client.GeminiClientError as e:
        raise PromptAnalysisError(f"Error analyzing prompt: {e}") from e

    # Convert to typed dataclass (validates structure automatically)
    try:
        result = AnalysisResult.from_dict(analysis_dict)
    except ValueError as e:
        raise PromptAnalysisError(
            f"Received invalid analysis format from Gemini: {e}"
        ) from e

    # Check validation result (unless skipped)
    if not result.is_coding_related:
        raise PromptAnalysisError(
            f"This prompt does not appear to be coding-related\n\n"
            f"[bold yellow]Reason:[/bold yellow] {result.validation_reason}"
        )

    return result
