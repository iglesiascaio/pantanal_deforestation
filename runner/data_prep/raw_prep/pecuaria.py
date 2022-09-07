import pandas as pd
import numpy as np
import click

from ..data_utils import pipe
from runner import io


def _melt_and_treat_df(df_pecuaria_cabecas):
    """
    Melt, treat and concat every quantity DataFrame.
    """

    melted_df = pd.melt(df_pecuaria_cabecas, id_vars=["level_0"]).rename(
        columns={
            "level_0": "location",
            "1985": "year",
            "Bovino": "crop",
            "value": "numero_cabecas",
        }
    )

    melted_df["numero_cabecas"] = melted_df["numero_cabecas"].replace("-", 0)
    melted_df["numero_cabecas"] = melted_df["numero_cabecas"].replace(
        ["...", ".."], np.nan
    )
    melted_df["type"] = "pecuaria"

    melted_df = melted_df.drop_duplicates().query('crop != "Total"')

    return melted_df


def run():
    """
    Read data and pre-process the quantity Raw Tables.
    """

    # reading the data
    pecuaria = io.load_table("raw", "pecuaria")

    # # pre-processing steps
    data_p = _melt_and_treat_df(pecuaria)

    return data_p


def save():
    """
    Save the quantitys pre-processed data.
    """
    data_p = run()

    io.save_table(data_p, "preprocessed", "pecuaria")


@click.command()
def run_task():
    save()
