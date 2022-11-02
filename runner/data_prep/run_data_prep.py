from runner.data_prep.raw_prep import run_raw_prep
from runner.data_prep.domain_prep import run_domain
from runner.data_prep.model_prep import prepare


def run_data_prep():
    run_raw_prep.run_raw_prep()
    run_domain.run_domain()
    prepare.save()
