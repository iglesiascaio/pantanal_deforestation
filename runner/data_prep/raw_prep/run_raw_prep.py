from runner.data_prep.raw_prep import area
from runner.data_prep.raw_prep import pecuaria
from runner.data_prep.raw_prep import quantidade
from runner.data_prep.raw_prep import land_use


def run_raw_prep():
    area.save()
    pecuaria.save()
    quantidade.save()
    land_use.save()
