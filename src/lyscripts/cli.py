"""Utilities for configuring and running CLIs app.

In this module, we define and configure a :py:class:`RichDefaultHelpFormatter` that
nicely displays the CLI's ``--help`` text. We also provide a function to
:py:func:`assemble a main function <assemble_main>` for the different CLI apps to save
some boilerplate code. Lastly, we have two functions related to the `loguru`_ setup.

.. _loguru: https://loguru.readthedocs.io/en/stable
"""

from collections.abc import Callable
from typing import Literal

from loguru import logger
from pydantic_settings import BaseSettings, CliApp, CliSettingsSource
from rich.console import Console
from rich.logging import RichHandler
from rich_argparse import ArgumentDefaultsRichHelpFormatter


def assemble_main(
    settings_cls: type[BaseSettings],
    prog_name: str,
) -> Callable[[], None]:
    """Assemble a ``main()`` function for a CLI app.

    It creates a :py:class:`~pydantic_settings.CliSettingsSource` object with the
    provided ``settings_cls`` and ``prog_name``. Then, it fills in some default
    settings for the CLI configuration and runs the CLI app.

    Assembling a ``main()`` function for all subcommands like this saves some
    boilerplate code.
    """

    def main() -> None:
        """Start the main CLI app."""
        cli_settings_source = CliSettingsSource(
            settings_cls=settings_cls,
            cli_prog_name=prog_name,
            cli_kebab_case=True,
            cli_use_class_docs_for_groups=True,
            formatter_class=ArgumentDefaultsRichHelpFormatter,
        )
        CliApp.run(settings_cls, cli_settings_source=cli_settings_source)

    return main


def somewhat_safely_get_loglevel(
    argv: list[str],
) -> Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    """Set the log level of the lyscripts CLI.

    This is a bit of a hack, since the :py:class:`~lyscripts.LyscriptsCLI` class is not
    yet initialized when we need to set the log level. In case the provided log-level is
    not valid, :py:class:`~lyscripts.LyscriptsCLI` will raise an exception at a later
    point.

    Return ``"INFO"`` by default.
    """
    args_str = " ".join(argv)
    if "--log-level" in args_str:
        for log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            if log_level in args_str:
                return log_level

    return "INFO"


def configure_logging(
    argv: list[str],
    console: Console,
) -> None:
    """Configure the `loguru`_ logging system of the lyscripts CLI.

    This function sets the log level and format of the lyscripts CLI. Notably, for
    a log-level of `DEBUG` the output will contain more information.

    .. _loguru: https://loguru.readthedocs.io/en/stable
    """
    logger.enable("lyscripts")
    logger.enable("lydata")
    log_level = somewhat_safely_get_loglevel(argv=argv)
    logger.remove()
    handler = RichHandler(console=console)
    logger.add(
        sink=handler,
        level=log_level,
        format="<lvl>{message}</>",
    )
