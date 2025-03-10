"""
.. module:: horta
   :platform: Unix, Windows
   :synopsis: Keep a network path alive by touching a file on a specified frequency

.. moduleauthor:: Miles Smith <miles-smith@omrf.org>
"""

from importlib.metadata import PackageNotFoundError, version
from typing import Annotated
from pathlib import Path
from time import sleep

import typer
from rich import print as rprint
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn, SpinnerColumn


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"



app = typer.Typer(
    name="horta",
    help="Keep a file system awake by repeatedly writing to a file",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)

verbosity_level = 0

def version_callback(value: bool) -> None:  # noqa FBT001
    """Prints the version of the package."""
    if value:
        rprint(f"[yellow]{{MODULE}}[/] version: [bold blue]{__version__}[/]")
        raise typer.Exit()


@app.callback()
def verbosity(
    verbose: Annotated[
        int,
        typer.Option(
            "-v",
            "--verbose",
            help="Control output verbosity. Pass this argument multiple times to increase the amount of output.",
            count=True,
        ),
    ] = 0
) -> None:
    verbosity_level = verbose  # noqa: F841

@app.callback(no_args_is_help=True,invoke_without_command=True)
def no_kill_i(
    touchfile: Annotated[
        Path,
        typer.Argument(
            help="Path to a file or directory that exists in a location that you wish to stay active."
            )
        ],
    frequency: Annotated[
        int,
        typer.Option(
            "--freq",
            "-f",
            help="Frequency in minutes at which to write to the keep-alive file."
            )
        ],
) -> None:
    number_of_times_touched = 0
    while True:
        with Progress(TextColumn("[progress.description]{task.description}"), SpinnerColumn(), BarColumn(), TimeRemainingColumn(), TextColumn(f"times touched {number_of_times_touched}"), transient=True, refresh_per_second=10,) as progress:
            countdown = progress.add_task("[red]Time until touch...", total=(frequency*60))

            while not progress.finished:
                progress.update(countdown, advance=1)
                sleep(1)

            with touchfile.open("w") as tf:
                tf.writelines("echo? echo?")

            number_of_times_touched += 1
