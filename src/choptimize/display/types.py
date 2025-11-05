from typing import Literal, NotRequired, TypedDict

from rich.style import Style

EchoJustifyMethod = Literal["default", "left", "center", "right", "full"]
EchoOverflowMethod = Literal["fold", "crop", "ellipsis", "ignore"]


class EchoKwargs(TypedDict):
    sep: NotRequired[str]
    end: NotRequired[str]
    style: NotRequired[str | Style | None]
    justify: NotRequired[EchoJustifyMethod | None]
    overflow: NotRequired[EchoOverflowMethod | None]
    no_wrap: NotRequired[bool | None]
    emoji: NotRequired[bool | None]
    markup: NotRequired[bool | None]
    highlight: NotRequired[bool | None]
    width: NotRequired[int | None]
    height: NotRequired[int | None]
    crop: NotRequired[bool]
    soft_wrap: NotRequired[bool | None]
    new_line_start: NotRequired[bool]
