from runner.engine import cli


@cli.root.group("raw_prep")
def raw_prep_group():
    """Functions to build raw prepared data"""
    pass


@raw_prep_group.command("build-all")
def run_build_raw_prep():
    """Build all raw_prep tables"""
    from .run_raw_prep import run_raw_prep

    run_raw_prep()
