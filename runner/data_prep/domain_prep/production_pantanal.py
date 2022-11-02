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


@pipe
def _agg_cultures(production_df):

    most_relevant_cultures = list(
        (
            (
                production_df.groupby("crop").quantidade_ton.sum()
                / production_df.quantidade_ton.sum()
            )
            .sort_values(ascending=False)
            .reset_index()
        )
        .query("quantidade_ton > 0.1")
        .crop.unique()
    ) + ["Bovino"]

    specific_df = production_df.query("crop.isin(@most_relevant_cultures)")
    non_specific_df = production_df.query("~crop.isin(@most_relevant_cultures)").assign(
        crop=lambda x: "Others_" + x["type"]
    )

    non_specific_df = non_specific_df.groupby(
        ["location", "year", "crop"], as_index=False
    )[["area_ha", "quantidade_ton"]].sum()

    final_df = pd.concat([specific_df, non_specific_df])

    return final_df


@pipe
def _create_delta_variables(pantanal_df):

    import ipdb

    ipdb.set_trace()

    grouped_df = pantanal_df.groupby(["location", "crop"])

    def __lag_by_group_1(key, value_df):
        df = value_df.assign(group=key[0] + ", " + key[1])
        return (
            df.sort_values(by=["year"], ascending=True)
            .set_index(["year"])
            .shift(1)
            .rename(
                columns={
                    "area_ha": "area_ha_lag",
                    "quantidade_ton": "quantidade_ton_lag",
                    "numero_cabecas": "numero_cabecas_lag",
                }
            )[
                [
                    "location",
                    "crop",
                    "area_ha_lag",
                    "quantidade_ton_lag",
                    "numero_cabecas_lag",
                ]
            ]
        )

    dflist = [
        __lag_by_group_1(g, grouped_df.get_group(g)) for g in grouped_df.groups.keys()
    ]
    lagged_df = pd.concat(dflist, axis=0).reset_index()
    pantanal_df = pantanal_df.merge(
        lagged_df, on=["location", "crop", "year"], how="left"
    )

    pantanal_df["delta_ha"] = (
        pantanal_df["area_ha"] - pantanal_df["area_ha_lag"]
    ).apply(lambda x: max(0, x))

    pantanal_df["delta_quantidade_ton"] = (
        pantanal_df["quantidade_ton"] - pantanal_df["quantidade_ton_lag"]
    ).apply(lambda x: max(0, x))

    pantanal_df["delta_nb_heads"] = (
        pantanal_df["numero_cabecas"] - pantanal_df["numero_cabecas_lag"]
    ).apply(lambda x: max(0, x))

    pantanal_df = pantanal_df.drop(
        columns=["area_ha_lag", "quantidade_ton_lag", "numero_cabecas_lag"]
    )

    return pantanal_df


def run():

    area_df = io.load_table("preprocessed", "area")
    quantity_df = io.load_table("preprocessed", "quantity")
    pecuaria_df = io.load_table("preprocessed", "pecuaria")

    final_df = (
        _combine_tables(area_df, quantity_df, pecuaria_df)
        >> _get_pantanal_df()
        >> _agg_cultures()
        >> _create_delta_variables()
    )

    return final_df


def save():
    data = run()
    import ipdb

    ipdb.set_trace()
    io.save_table(data, "domain", "pantanal")


@click.command()
def run_task():
    save()
