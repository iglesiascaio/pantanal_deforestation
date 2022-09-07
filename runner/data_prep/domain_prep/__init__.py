from runner.engine import cli


@cli.root.group("domain")
def domain_group():
    """Functions to build domain data"""
    pass


@domain_group.command("build-all")
def run_build_domain():
    """Build all domain tables"""
    from .run_domain import run_domain

    run_domain()
