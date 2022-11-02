from runner.engine import cli


@cli.root.group("all_data_prep")
def all_data_prep_group():
    """Functions to build model data from raw data"""
    pass


@all_data_prep_group.command("build-all")
def run_build_raw_prep():
    """Build model data from raw"""
    from .run_data_prep import run_data_prep

    run_data_prep()
