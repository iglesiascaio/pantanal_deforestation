from runner.data_prep.raw_prep import area
from runner.data_prep.raw_prep import pecuaria
from runner.data_prep.raw_prep import quantidade
from runner.data_prep.raw_prep import land_use_transitions
from runner.data_prep.raw_prep import land_use
from runner.data_prep.raw_prep import environmental_laws
from runner.data_prep.raw_prep import queimadas


def run_raw_prep():
    area.save()
    pecuaria.save()
    quantidade.save()
    land_use_transitions.save()
    land_use.save()
    environmental_laws.save()
    queimadas.save()
