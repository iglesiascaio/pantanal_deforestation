import pandas as pd
import click
import datetime

from ..data_utils import pipe

from runner import io


@pipe
def _compute_deforestation(df):

    df = df.rename(columns={"municipality": "city", "UF": "state"})

    dict_rename_transition = {
        str(i) + "-" + str(i + 1): pd.to_datetime(str(i)) for i in range(1985, 2021)
    }
    relevant_cols = [
        "city",
        "state",
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

    natural_ids = [3, 4, 5, 49, 11, 12, 32, 29, 50, 13]

    melted_df = (
        pd.melt(
            # df.query(
            #     " from_class.isin(@natural_ids) and level_0 == 'Anthropic' and biome == 'PANTANAL'"
            # ),
            df.query(" from_class.isin(@natural_ids) and level_0 == 'Anthropic'"),
            id_vars=relevant_cols,
            value_vars=list(dict_rename_transition.keys()),
            var_name="year",
            value_name="deforestation_ha",
        )
        .drop(columns=["from_class", "to_class"])
        .rename(columns={"location_UF": "state"})
        .groupby(["city", "state", "location", "year"])
        .sum()
        .reset_index()
        .assign(year=lambda x: x["year"].replace(dict_rename_transition))
        .rename(columns={"state": "location_UF"})
    )

    return melted_df


def run():

    land_use_df = io.load_table("preprocessed", "land_use_transitions")

    final_df = land_use_df >> _compute_deforestation()

    return final_df


def save():
    data = run()
    io.save_table(data, "domain", "deforestation")


@click.command()
def run_task():
    save()
