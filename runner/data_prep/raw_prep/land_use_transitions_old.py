import pandas as pd
import numpy as np
import click

from ..data_utils import pipe
from runner import io


def _select_cols_and_treat_df(df_land_use_transitions):
    """
    Select cols and treat land use transtition DataFrame.
    """

    df_land_use_transitions["location"] = (
        df_land_use_transitions["city"] + " (" + df_land_use_transitions["state"] + ")"
    )
    dict_rename_transition = {
        str(i) + "-" + str(i + 1): pd.to_datetime(str(i)) for i in range(1985, 2020)
    }
    relevant_cols = [
        "city",
        "state",
        "location",
        "from_level_0",
        "from_level_1",
        "from_level_2",
        "from_level_3",
        "from_level_4",
        "to_level_0",
        "to_level_1",
        "to_level_2",
        "to_level_3",
        "to_level_4",
    ]
    df_land_use_transitions = df_land_use_transitions[
        relevant_cols + list(dict_rename_transition.keys())
    ]

    return df_land_use_transitions


def run():
    """
    Read data and pre-process the land use Raw Tables.
    """

    # reading the data
    # df_land_use = io.load_table("raw", "land_use")
    df_land_use_transitions = io.load_table("raw", "land_use_transitions")

    # # pre-processing steps
    data_p = _select_cols_and_treat_df(df_land_use_transitions)

    return data_p


def save():
    """
    Save the quantitys pre-processed data.
    """
    data_p = run()

    io.save_table(data_p, "preprocessed", "land_use_transitions")


@click.command()
def run_task():
    save()
