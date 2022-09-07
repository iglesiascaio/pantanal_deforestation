from runner.data_prep.domain_prep import pantanal
from runner.data_prep.domain_prep import deforestation


def run_domain():
    pantanal.save()
    deforestation.save()
