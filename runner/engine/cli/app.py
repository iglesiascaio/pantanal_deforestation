import click
from runner.logging import initialize_logging


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.pass_context
def root(ctx):
    initialize_logging()


def main():
    root()
