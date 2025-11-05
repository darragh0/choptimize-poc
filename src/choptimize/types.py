"""Type definitions for choptimize.

Central location for all dataclasses and type definitions used throughout the app.
"""

from dataclasses import dataclass
from typing import Any

from google import genai


@dataclass(frozen=True)
class GeminiConfig:
    """Configuration for Gemini API client."""

    client: genai.Client
    model_name: str = "gemini-2.5-flash"


@dataclass(frozen=True)
class Metric:
    """Analysis metric with score, explanation, & suggestions"""

    score: float
    explanation: str
    suggestions: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Metric":
        """Create Metric from dictionary

        Args:
            data: Dictionary with 'score', 'explanation', 'suggestions' keys.

        Returns:
            Metric instance.

        Raises:
            ValueError: If required fields are missing.
        """
        try:
            return cls(
                score=float(data["score"]),
                explanation=str(data["explanation"]),
                suggestions=list(data.get("suggestions", [])),
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid metric data: {e}") from e


@dataclass(frozen=True)
class AnalysisResult:
    """Complete analysis result for a coding prompt."""

    is_coding_related: bool
    overall_score: float | None = None
    overall_assessment: str | None = None
    specificity: Metric | None = None
    clarity: Metric | None = None
    context: Metric | None = None
    constraints: Metric | None = None
    brevity: Metric | None = None
    improved_prompt: str | None = None
    validation_reason: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnalysisResult":
        """Create AnalysisResult from Gemini API response.

        Handles both validation-only responses and full analysis responses.

        Args:
            data: Dictionary with analysis data from Gemini.

        Returns:
            AnalysisResult instance.

        Raises:
            ValueError: If the data structure is invalid.
        """
        is_coding_related = data.get("is_coding_related", True)

        if not is_coding_related:
            # Validation failed - minimal response
            return cls(
                is_coding_related=False,
                validation_reason=data.get("reason", "Not a coding prompt"),
            )

        # Full analysis response
        try:
            metrics = data["metrics"]
            return cls(
                is_coding_related=True,
                overall_score=float(data["overall_score"]),
                overall_assessment=str(data["overall_assessment"]),
                specificity=Metric.from_dict(metrics["specificity"]),
                clarity=Metric.from_dict(metrics["clarity"]),
                context=Metric.from_dict(metrics["context"]),
                constraints=Metric.from_dict(metrics["constraints"]),
                brevity=Metric.from_dict(metrics["brevity"]),
                improved_prompt=data.get("improved_prompt"),
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid analysis data: {e}") from e


def get_score_assessment(score: float) -> str:
    """Get text assessment for a score.

    Args:
        score: The score value (1-10).

    Returns:
        A text assessment label.
    """
    if score >= 9:
        return "Excellent"
    if score >= 7:
        return "Good"
    if score >= 5:
        return "Fair"
    if score >= 3:
        return "Needs improvement"
    return "Poor"
