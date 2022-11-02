import pandas as pd
import numpy as np
import click

from runner import io


def run():
    """
    Read data and pre-process the land use Raw Tables.
    Source: https://www.ibflorestas.org.br/conteudo/leis-ambientais
    """

    # reading the data
    df_law_enviromental = pd.DataFrame(
        {
            "law": [
                "Novo Código Florestal Brasileiro",
                "Lei de Crimes Ambientais",
                "Política Nacional de Recursos Hídricos",
                "Sistema Nacional de Unidades de Conservação da Natureza",
                "Política Agrícola",
            ],
            "implementation_year": [2012, 1998, 1997, 2000, 1991],
        }
    )

    return df_law_enviromental


def save():
    """
    Save the quantitys pre-processed data.
    """
    data_p = run()
    import ipdb

    ipdb.set_trace()
    io.save_table(data_p, "preprocessed", "environmental_laws")


@click.command()
def run_task():
    save()
