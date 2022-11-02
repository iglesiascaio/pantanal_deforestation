import pandas as pd
import numpy as np
import click

from ..data_utils import pipe
from runner import io


@pipe
def _create_cols(df):

    df["location"] = df["city"] + " (" + df["state"] + ")"

    return df


@pipe
def _rename_cols(df):

    dict_rename_cols = {i: str(i) for i in range(1985, 2021)}

    df = df.rename(columns=dict_rename_cols)

    return df


def run():
    """
    Read data and pre-process the land use Raw Tables.
    """

    # reading the data
    df_land_use = io.load_table("raw", "land_use")

    # # pre-processing steps
    data_p = df_land_use >> _rename_cols() >> _create_cols()

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
