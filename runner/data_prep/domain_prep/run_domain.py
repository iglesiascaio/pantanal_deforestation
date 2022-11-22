from runner.data_prep.domain_prep import production_pantanal
from runner.data_prep.domain_prep import deforestation_pantanal
from runner.data_prep.domain_prep import area_pantanal_features
from runner.data_prep.domain_prep import queimadas
from runner.data_prep.domain_prep import environmental_laws


def run_domain():
    production_pantanal.save()
    deforestation_pantanal.save()
    area_pantanal_features.save()
    queimadas.save()
    environmental_laws.save()
