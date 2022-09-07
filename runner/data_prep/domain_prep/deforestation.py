import pandas as pd
import click
import datetime

from ..data_utils import pipe

from runner import io


@pipe
def _get_pantanal_df(df):
    """
    Filter municipalities within Pantanal.
    """
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

    pantanal_df = df[df.location.isin(list_municipios_pantanal)]

    assert len(pantanal_df.location.unique()) == len(list_municipios_pantanal)

    return pantanal_df


@pipe
def _compute_deforestation(pantanal_deforestation_df):
    """
    Compute deforestation (ha).
    """

    pantanal_deforestation_df["year"] = (
        pantanal_deforestation_df["year"]
        .astype("str")
        .apply(lambda x: datetime.datetime.strptime(x, "%Y"))
    )
    pantanal_deforestation_df = pantanal_deforestation_df.set_index(
        ["year", "location"]
    )

    shifted = pantanal_deforestation_df.groupby(level="location").shift(1)
    pantanal_deforestation_df = (
        pantanal_deforestation_df.join(
            shifted.rename(columns=lambda x: x + "_lag")
        ).drop(columns=["state_lag", "city_lag"])
    ).reset_index()

    pantanal_deforestation_df["deforestation_ha"] = (
        pantanal_deforestation_df["area_ha_lag"] - pantanal_deforestation_df["area_ha"]
    ).apply(lambda x: max(0, x))

    pantanal_deforestation_df["location_UF"] = pantanal_deforestation_df[
        "location"
    ].apply(lambda x: x[-3:-1])

    pantanal_deforestation_df = pantanal_deforestation_df.drop(columns=["state"])

    return pantanal_deforestation_df


def run():

    land_use_df = io.load_table("preprocessed", "land_use")

    final_df = land_use_df >> _get_pantanal_df() >> _compute_deforestation()

    return final_df


def save():
    data = run()
    io.save_table(data, "domain", "deforestation")


@click.command()
def run_task():
    save()
