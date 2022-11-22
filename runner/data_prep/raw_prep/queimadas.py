import pandas as pd
import numpy as np
import click

from ..data_utils import pipe
from runner import io


@pipe
def _get_pantanal_df(df):

    pantanal_states_dict = {"MATO GROSSO": "MT", "MATO GROSSO DO SUL": "MS"}

    df = df.query("state.isin(@pantanal_states_dict)").assign(
        state=lambda x: x["state"].replace(pantanal_states_dict)
    )

    df["city"] = (
        df["city"]
        .str.title()
        .str.replace("De", "de")
        .str.replace("Da", "da")
        .str.replace("Do", "do")
    )

    df["location"] = df["city"] + " (" + df["state"] + ")"

    list_municipios_pantanal = [
        "Barão de Melgaço (MT)",
        "Cáceres (MT)",
        "Itiquira (MT)",
        "Lambari D'Oeste (MT)",
        "Nossa Senhora do Livramento (MT)",
        "Poconé (MT)",
        "Santo Antônio do Leverger (MT)",
        "Aquidauana (MS)",
        "Bodoquena (MS)",
        "Corumbá (MS)",
        "Coxim (MS)",
        "Ladário (MS)",
        "Miranda (MS)",
        "Sonora (MS)",
        "Porto Murtinho (MS)",
        "Rio Verde de Mato Grosso (MS)",
    ]

    df = df[df.location.isin(list_municipios_pantanal)]

    assert len(df.location.unique()) == len(list_municipios_pantanal)

    return df


@pipe
def _fix_column_names(df):

    df.columns = [str(i) for i in df.columns]

    return df


def run():
    """
    Read data and pre-process the Area Raw Tables.
    """

    # reading the data
    queimadas = io.load_table("raw", "queimadas")

    data_p = queimadas >> _get_pantanal_df() >> _fix_column_names()

    return data_p


def save():
    """
    Save the areas pre-processed data.
    """
    data_p = run()

    io.save_table(data_p, "preprocessed", "queimadas")


@click.command()
def run_task():
    save()
