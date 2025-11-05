import sys
from argparse import ArgumentParser
from typing import NoReturn, override

from choptimize.display.handles import cerr


class ArgParser(ArgumentParser):
    def rich_print_err(self, message: str) -> None:
        cerr.print(message)

    def _warning(self, message: str) -> None:
        self.rich_print_err(f"[bold yellow]{self.prog}: warning:[/bold red] {message}")

    @override
    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        if message:
            self.rich_print_err(message)
        sys.exit(status)

    @override
    def error(self, message: str) -> NoReturn:
        self.rich_print_err(f"[bold red]{self.prog}: error:[/bold red] {message}")
        self.print_usage()
        sys.exit(0)
