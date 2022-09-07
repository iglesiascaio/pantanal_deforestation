import pandas as pd
import numpy as np
import click

from ..data_utils import pipe
from runner import io


def _melt_and_treat_df(df_land_use):
    """
    Melt and treat land use DataFrame.
    """

    melted_df = (
        pd.melt(
            df_land_use.query('level_1 == "1. Forest"'),
            id_vars=["state", "city"],
            value_vars=list(range(1985, 2021)),
            var_name="year",
            value_name="area_ha",
        )
        .groupby(["state", "city", "year"])
        .sum()
        .reset_index()
    )

    melted_df["location"] = melted_df["city"] + " (" + melted_df["state"] + ")"

    return melted_df


def run():
    """
    Read data and pre-process the land use Raw Tables.
    """

    # reading the data
    df_land_use = io.load_table("raw", "land_use")

    # # pre-processing steps
    data_p = _melt_and_treat_df(df_land_use)

    return data_p


def save():
    """
    Save the quantitys pre-processed data.
    """
    data_p = run()

    io.save_table(data_p, "preprocessed", "land_use")


@click.command()
def run_task():
    save()
