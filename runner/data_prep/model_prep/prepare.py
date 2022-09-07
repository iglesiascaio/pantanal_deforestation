import pandas as pd
import click
import datetime

from ..data_utils import pipe

from runner import io


@pipe
def _prepare_deforestation_df(deforestation_df):

    deforestation_df = deforestation_df.drop(columns=["area_ha", "area_ha_lag"])
    deforestation_df["year"] = deforestation_df["year"].dt.year.astype("str")

    return deforestation_df


@pipe
def _prepare_pantanal_df(pantanal_df):

    pecuaria_df = pantanal_df.query('type=="pecuaria"')
    crops_df = pantanal_df.query('type!="pecuaria"')

    pecuaria_df = pecuaria_df.drop(
        columns=["crop", "type", "area_ha", "quantidade_ton"]
    ).rename(columns={"numero_cabecas": "nb_heads_cattle"})

    crops_df = crops_df.drop(columns=["type", "numero_cabecas"])

    crops_df["crop"] = crops_df["crop"].apply(lambda x: x.lower().replace(" ", "_"))

    crops_df = pd.pivot_table(
        crops_df,
        values=["area_ha", "quantidade_ton"],
        index=["location", "year"],
        columns=["crop"],
    )

    crops_df.columns = (
        crops_df.columns.get_level_values(0)
        + "_"
        + crops_df.columns.get_level_values(1)
    )

    merged_processed_pantanal_df = pecuaria_df.merge(
        crops_df, on=["location", "year"], how="inner"
    )

    return merged_processed_pantanal_df


def _merge_dfs(processed_pantanal_df, processed_deforestation_df):
    """
    Merge processed domain DataFrames.
    """

    import ipdb

    ipdb.set_trace()

    merged_df = processed_pantanal_df.merge(
        processed_deforestation_df, on=["location", "year"]
    ).drop(columns=["location"])

    return merged_df


def run():

    pantanal_df = io.load_table("domain", "pantanal")
    deforestation_df = io.load_table("domain", "deforestation")

    processed_pantanal_df = pantanal_df >> _prepare_pantanal_df()
    processed_deforestation_df = deforestation_df >> _prepare_deforestation_df()

    model_df = _merge_dfs(processed_pantanal_df, processed_deforestation_df)

    return model_df


def save():
    data = run()
    import ipdb

    ipdb.set_trace()
    io.save_table(data, "model", "model_df")


@click.command()
def run_task():
    save()
