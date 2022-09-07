import importlib
import logging
from runner.engine import cli
import click

logger = logging.getLogger(__name__)


@cli.root.command("task", context_settings=dict(ignore_unknown_options=True))
@click.argument("name", required=False)
@click.argument("task_args", nargs=-1)
@click.option("--help", is_flag=True, help="Show this message and exit.")
def task(name, help, task_args):
    """Run a function as a batch task.

    The NAME must be a `<module>:<func>` specification.

    Any option passed after NAME are passed as is to the function as a list. If your
    function `@click.command` wrapped, it should work if called directly.
    """

    if not name:
        with click.Context(task) as ctx:
            click.echo(task.get_help(ctx))
        raise SystemExit(0)

    func = get_task_func(name)
    if func is None:
        raise click.BadArgumentUsage("Task not found with NAME: " + name)

    task_args = list(task_args)

    if help:
        task_args += ["--help"]

    if help and isinstance(func, click.core.BaseCommand):
        func(task_args)
        raise SystemExit(0)

    logger.info("*" * 50)
    logger.info("Starting task: " + name)
    try:
        func(task_args)
    except SystemExit as ex:
        if ex.code != 0:
            raise
    logger.info("Finished task: " + name)
    logger.info("*" * 50)


def get_task_func(name):
    try:
        module_name, func_name = name.split(":", 1)
    except ValueError:
        raise ValueError("Task name should be of the form <module>:<func>")

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as ex:
        if ex.name == module_name:
            raise ValueError("Task module name not found: " + module_name)
        raise

    try:
        func = getattr(module, func_name)
    except AttributeError:
        raise ValueError("Task function not found in module:" + func_name)

    return func
