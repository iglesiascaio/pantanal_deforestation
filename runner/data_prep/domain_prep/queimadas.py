import pandas as pd
import click
import datetime

from ..data_utils import pipe

from runner import io


@pipe
def _melt_and_treat_df(df):

    list_years = [str(i) for i in range(1985, 2022)]

    relevant_cols = [
        "city",
        "state",
        "location",
    ]

    melted_df = (
        pd.melt(
            df.query("level_0 == 'Natural'"),
            id_vars=relevant_cols,
            value_vars=list_years,
            var_name="year",
            value_name="fires_ha",
        )
        .groupby(["city", "state", "location", "year"])
        .sum()
        .reset_index()
        .drop(columns=["state", "city"])
    )

    return melted_df


@pipe
def _estimate_2021_data(df):

    growth_rate = df["2020"].sum() / df["2019"].sum()

    df["2021"] = df["2020"] * growth_rate

    return df


def run():

    queimadas_df = io.load_table("preprocessed", "queimadas")

    final_df = queimadas_df >> _estimate_2021_data() >> _melt_and_treat_df()

    return final_df


def save():
    data = run()

    io.save_table(data, "domain", "queimadas")


@click.command()
def run_task():
    save()
