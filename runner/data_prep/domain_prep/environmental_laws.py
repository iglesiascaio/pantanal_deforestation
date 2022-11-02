import pandas as pd
import click
import datetime

from ..data_utils import pipe

from runner import io


@pipe
def _get_and_explode_list_years(environmental_laws_df):
    """
    Get list years the law exists DataFrame.
    """

    environmental_laws_df["year"] = environmental_laws_df["implementation_year"].apply(
        lambda x: [str(i) for i in range(x, 2021)]
    )

    environmental_laws_df = environmental_laws_df.explode("year").drop(
        columns=["implementation_year"]
    )

    return environmental_laws_df


@pipe
def _pivot_table(environmental_laws_df):
    """
    Pivot and treat law DataFrame.
    """

    final_df = pd.pivot_table(
        environmental_laws_df, columns=["law"], index=["year"], aggfunc="size"
    ).reset_index()

    return final_df


def run():

    environmental_laws_df = io.load_table("preprocessed", "environmental_laws")

    final_df = environmental_laws_df >> _get_and_explode_list_years() >> _pivot_table()

    return final_df


def save():
    data = run()
    import ipdb

    ipdb.set_trace()
    io.save_table(data, "domain", "environmental_laws")


@click.command()
def run_task():
    save()
