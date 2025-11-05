import sys

from rich_argparse import RichHelpFormatter

from choptimize.analysis import PromptAnalysisError, analyze_prompt
from choptimize.display import ArgParser, cout, display_analysis, echo_err

RichHelpFormatter.styles = {
    "argparse.args": "cyan",
    "argparse.groups": "bold green",
    "argparse.prog": "cyan",
    "argparse.metavar": "cyan",
    "argparse.help": "default",
    "argparse.text": "default",
}


def make_arg_parser() -> ArgParser:
    parser = ArgParser(
        description="Analyze & optimize coding prompts",
        formatter_class=RichHelpFormatter,
        add_help=False,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="Show this help message & exit",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="[cyan]%(prog)s[/cyan] [green]v0.1.0[/green]",
        help="Show current program version & exit",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to analyze",
    )

    return parser


def get_prompt_input(prompt: str | None) -> str:
    """Get prompt input from argument (or stdin)

    Args:
        prompt: Command-line prompt argument

    Returns:
        Prompt text to analyze
    """
    if prompt is None:
        # Read from stdin if no argument provided
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        else:
            echo_err(
                "no prompt provided",
                "provide as argument or via pipe [cyan]|[/cyan] or here string [cyan]<<<[/cyan]",
            )
            sys.exit(1)

    if not prompt:
        echo_err("empty prompt provided")
        sys.exit(1)

    return prompt


def run() -> None:
    """Analyze & optimize coding prompts.

    Evaluates the prompt across 5 key metrics:

    - Specificity:  How precisely the requirements are defined
    - Clarity:      How easily the prompt can be understood
    - Context:      How well background information is provided
    - Constraints:  How explicitly limitations are specified
    - Brevity:      How concisely information is communicated

    Examples:
      choptimize "Write a function to reverse a string"
      echo "Create a REST API" | choptimize
      choptimize < my_prompt.txt

    Args:
        prompt: The prompt to analyze (None to read from stdin).
        allow_any: If True, skip coding-related validation check.
    """

    try:
        parser = make_arg_parser()
        args = parser.parse_args()

        prompt: str = args.prompt
        prompt_text = get_prompt_input(prompt)

        with cout.status("[green]Analyzing prompt [/green]", spinner="bouncingBar"):
            analysis = analyze_prompt(prompt_text)

        display_analysis(analysis, prompt_text)

    except PromptAnalysisError as e:
        echo_err("error analyzing prompt", str(e), then_exit_with=1)
    except Exception as e:
        echo_err("unexpected error", str(e), then_exit_with=1)
    except KeyboardInterrupt:
        echo_err("keyboard interrupt raised", prefix="!", then_exit_with=0)
