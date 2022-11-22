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
def _get_natural_and_total_area(df_land_use):
    """
    Melt and treat land use DataFrame.
    """

    natural_area_df = (
        pd.melt(
            df_land_use.query('level_0 == "Natural"'),
            id_vars=["location", "state", "city"],
            value_vars=[str(i) for i in range(1985, 2021)],
            var_name="year",
            value_name="natural_area_ha",
        )
        .groupby(["location", "state", "city", "year"])
        .sum()
        .reset_index()
    )

    total_area_df = (
        pd.melt(
            df_land_use,
            id_vars=["location", "state", "city"],
            value_vars=[str(i) for i in range(1985, 2021)],
            var_name="year",
            value_name="total_area_ha",
        )
        .groupby(["location", "state", "city", "year"])
        .sum()
        .reset_index()
    )

    final_area_df = total_area_df.merge(
        natural_area_df,
        on=["location", "state", "city", "year"],
        how="inner",
        validate="1:1",
    ).drop(columns=["city", "state"])

    return final_area_df


def run():

    land_use_df = io.load_table("preprocessed", "land_use")

    final_df = land_use_df >> _get_pantanal_df() >> _get_natural_and_total_area()

    return final_df


def save():
    data = run()
    io.save_table(data, "domain", "area_pantanal_features")


@click.command()
def run_task():
    save()
