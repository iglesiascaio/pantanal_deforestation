import pandas as pd
import numpy as np
import click

from ..data_utils import pipe
from runner import io


@pipe
def _select_cols_and_treat_df(df_land_use_transitions):
    """
    Select cols and treat land use transtition DataFrame.
    """

    df_land_use_transitions["location"] = (
        df_land_use_transitions["municipality"]
        + " ("
        + df_land_use_transitions["UF"]
        + ")"
    )
    dict_rename_transition = {
        str(i) + "-" + str(i + 1): pd.to_datetime(str(i)) for i in range(1985, 2021)
    }
    relevant_cols = [
        "municipality",
        "UF",
        "location",
        "biome",
        "level_0",
        "level_1",
        "level_2",
        "level_3",
        "level_4",
        "from_class",
        "to_class",
    ]
    df_land_use_transitions = df_land_use_transitions[
        relevant_cols + list(dict_rename_transition.keys())
    ]

    return df_land_use_transitions


@pipe
def _get_pantanal_df(df):
    """
    Filter municipalities within Pantanal.
    """

    pantanal_df = df.copy()
    dict_municipios_pantanal = {
        "Baro de Melgao (MT)": "Barão de Melgaço (MT)",
        "Cceres (MT)": "Cáceres (MT)",
        "Itiquira (MT)": "Itiquira (MT)",
        "Lambari D'Oeste (MT)": "Lambari D'Oeste (MT)",
        "Nossa Senhora do Livramento (MT)": "Nossa Senhora do Livramento (MT)",
        "Pocon (MT)": "Poconé (MT)",
        "Santo Antnio do Leverger (MT)": "Santo Antônio do Leverger (MT)",
        "Aquidauana (MS)": "Aquidauana (MS)",
        "Bodoquena (MS)": "Bodoquena (MS)",
        "Corumb (MS)": "Corumbá (MS)",
        "Coxim (MS)": "Coxim (MS)",
        "Ladrio (MS)": "Ladário (MS)",
        "Miranda (MS)": "Miranda (MS)",
        "Sonora (MS)": "Sonora (MS)",
        "Porto Murtinho (MS)": "Porto Murtinho (MS)",
        "Rio Verde de Mato Grosso (MS)": "Rio Verde de Mato Grosso (MS)",
    }

    pantanal_df["location"] = pantanal_df["location"].replace(dict_municipios_pantanal)

    pantanal_df["municipality"] = (
        pantanal_df["location"].str.split("(").str[0].str.strip()
    )

    pantanal_df = pantanal_df[
        pantanal_df.location.isin(dict_municipios_pantanal.values())
    ]

    assert len(pantanal_df.location.unique()) == len(dict_municipios_pantanal)

    return pantanal_df


def run():
    """
    Read data and pre-process the land use Raw Tables.
    """

    # reading the data
    # df_land_use = io.load_table("raw", "land_use")
    df_land_use_transitions = io.load_table("raw", "land_use_transitions_new")

    # # pre-processing steps
    data_p = (
        df_land_use_transitions >> _select_cols_and_treat_df() >> _get_pantanal_df()
    )

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
