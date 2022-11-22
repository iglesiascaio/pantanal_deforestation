import pandas as pd
import click
import datetime

from runner.data_prep.data_utils.utils import remove_special_char

from ..data_utils import pipe, remove_special_char

from runner import io


@pipe
def _prepare_deforestation_pantanal_df(deforestation_df):

    # deforestation_df = deforestation_df.drop(columns=["area_ha", "area_ha_lag"])
    deforestation_df["year"] = deforestation_df["year"].dt.year.astype("str")

    return deforestation_df


@pipe
def _prepare_production_pantanal_df(pantanal_df):

    pecuaria_df = pantanal_df.query('type=="pecuaria"')
    crops_df = pantanal_df.query('type!="pecuaria"')

    pecuaria_df = pecuaria_df.drop(
        columns=["crop", "type", "area_ha", "quantity_ton"]
    ).rename(columns={"numero_cabecas": "nb_heads_cattle"})

    crops_df = crops_df.drop(columns=["type", "numero_cabecas"])

    crops_df["crop"] = crops_df["crop"].apply(lambda x: x.lower().replace(" ", "_"))

    crops_df = pd.pivot_table(
        crops_df,
        values=["quantity_ton", "delta_quantity_ton"],
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


@pipe
def _prepare_environmental_law_df(environmental_law_df):

    environmental_law_df.columns = [
        "law_" + i.lower().replace(" ", "_") >> remove_special_char()
        if i != "year"
        else i
        for i in environmental_law_df.columns
    ]

    return environmental_law_df


def _merge_dfs(
    processed_pantanal_df,
    processed_deforestation_df,
    area_pantanal_features_df,
    environmental_law_df,
    queimadas_df,
):
    """
    Merge processed domain DataFrames.
    """

    merged_df = (
        processed_pantanal_df.merge(processed_deforestation_df, on=["location", "year"])
        .merge(area_pantanal_features_df, on=["location", "year"])
        .merge(queimadas_df, on=["location", "year"], how="left")
        .drop(columns=["location"])
        .merge(environmental_law_df, on=["year"], how="left")
    )

    cols_laws = environmental_law_df.drop(columns=["year"]).columns

    merged_df[cols_laws] = merged_df[cols_laws].fillna(0)

    return merged_df


@pipe
def _create_lag_vars(merged_df, n_lag):

    vars_to_lag = ["deforestation_ha", "nb_heads_cattle", "fires_ha"]

    grouped_df = merged_df.groupby(["city"])

    def __lag_by_group(key, value_df, i):
        df = value_df.assign(group=key)
        return (
            df.sort_values(by=["year"], ascending=True)
            .set_index(["year"])
            .shift(i)
            .rename(columns={var: var + "_" + str(i) for var in vars_to_lag})[
                ["city"] + [var + "_" + str(i) for var in vars_to_lag]
            ]
        )

    for i in range(1, n_lag + 1):
        dflist = [
            __lag_by_group(g, grouped_df.get_group(g), i)
            for g in grouped_df.groups.keys()
        ]
        lagged_df_it = pd.concat(dflist, axis=0).reset_index()
        merged_df = merged_df.merge(lagged_df_it, on=["city", "year"], how="left")

    return merged_df


def run():

    production_pantanal_df = io.load_table("domain", "pantanal")
    deforestation_pantanal_df = io.load_table("domain", "deforestation")
    area_pantanal_features_df = io.load_table("domain", "area_pantanal_features")
    environmental_law_df = io.load_table("domain", "environmental_laws")
    queimadas_df = io.load_table("domain", "queimadas")
    n_lags = 5

    processed_production_pantanal_df = (
        production_pantanal_df >> _prepare_production_pantanal_df()
    )
    processed_deforestation_df = (
        deforestation_pantanal_df >> _prepare_deforestation_pantanal_df()
    )

    preproceed_environmental_law_df = (
        environmental_law_df >> _prepare_environmental_law_df()
    )

    model_df = _merge_dfs(
        processed_production_pantanal_df,
        processed_deforestation_df,
        area_pantanal_features_df,
        environmental_law_df,
        queimadas_df,
    ) >> _create_lag_vars(n_lags)

    return model_df


def save():
    data = run()
    io.save_table(data, "model", "model_df")


@click.command()
def run_task():
    save()
