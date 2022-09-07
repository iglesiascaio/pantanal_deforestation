import pandas as pd
import numpy as np
import click

from ..data_utils import pipe
from runner import io


def __melt_and_treat_single_table(df, type_df):
    """
    Melt, assign type and treat area variable for a single DataFrame.
    """

    df_melted = pd.melt(df, id_vars=["level_0"]).rename(
        columns={
            "level_0": "location",
            "1985": "year",
            "Total": "crop",
            "value": "area_ha",
        }
    )

    df_melted["area_ha"] = df_melted["area_ha"].replace("-", 0)
    df_melted["area_ha"] = df_melted["area_ha"].replace(["...", ".."], np.nan)
    df_melted["type"] = type_df

    return df_melted


def _melt_and_concat_tables(list_tables):
    """
    Melt, treat and concat every area DataFrame.
    """
    melted_list = []
    for i, df in enumerate(list_tables):
        # the last DataFrame is respective to permanent culture
        if i == len(list_tables) - 1:
            type_df = "permanente"
        else:
            type_df = "temporario"
        melted_list.append(__melt_and_treat_single_table(df, type_df))

    concat_df = pd.concat(melted_list).drop_duplicates().query('crop != "Total"')

    return concat_df


def run():
    """
    Read data and pre-process the Area Raw Tables.
    """

    # reading the data
    temp_1_area = io.load_table("raw", "temp_1_area")
    temp_2_area = io.load_table("raw", "temp_2_area")
    temp_3_area = io.load_table("raw", "temp_3_area")
    perm_area = io.load_table("raw", "perm_area")

    list_tables = [temp_1_area, temp_2_area, temp_3_area, perm_area]

    # # pre-processing steps
    data_p = _melt_and_concat_tables(list_tables)

    return data_p


def save():
    """
    Save the areas pre-processed data.
    """
    data_p = run()

    io.save_table(data_p, "preprocessed", "area")


@click.command()
def run_task():
    save()
