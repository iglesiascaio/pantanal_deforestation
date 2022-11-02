from runner.data_prep.domain_prep import production_pantanal
from runner.data_prep.domain_prep import deforestation_pantanal
from runner.data_prep.domain_prep import area_pantanal_features


def run_domain():
    production_pantanal.save()
    deforestation_pantanal.save()
    area_pantanal_features.save()
