import pandas as pd
import click

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


def _combine_tables(area_df, quantity_df, pecuaria_df):

    df = area_df.merge(
        quantity_df,
        how="inner",
        on=[
            "location",
            "year",
            "crop",
            "type",
        ],
        validate="1:1",
    )

    df = pd.concat([df, pecuaria_df])

    return df


def run():

    area_df = io.load_table("preprocessed", "area")
    quantity_df = io.load_table("preprocessed", "quantity")
    pecuaria_df = io.load_table("preprocessed", "pecuaria")

    final_df = _combine_tables(area_df, quantity_df, pecuaria_df) >> _get_pantanal_df()

    return final_df


def save():
    data = run()
    io.save_table(data, "domain", "pantanal")


@click.command()
def run_task():
    save()
