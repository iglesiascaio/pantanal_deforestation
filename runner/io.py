import pickle
import logging
import tempfile
from pathlib import Path

import fsspec
import pandas as pd
from typing import Any
from gamma.config import get_config
from jinja2 import StrictUndefined, Template, Undefined

from runner.fs import get_fs_path, make_parents

logger = logging.getLogger(__name__)


def get_current_date():
    dt_today = pd.to_datetime("today")
    return dt_today.strftime("%Y-%m-%d")


def get_info(domain: str, element: str, element_type="table"):
    config = get_config()

    default_base_uri = config["data_context"]["data_uri"]
    #    default_account = config["data_context"]["account_name"]

    domain_elements = config["data"].get(domain, None)
    container_name = domain_elements.get("container_name", Undefined())
    #   account_name = domain_elements.get("account_name", default_account)

    if domain_elements is None:
        raise ValueError(
            f"The domain {domain} has not been declared in the config.yaml"
        )

    if "base_uri" in domain_elements:
        base_uri: str = domain_elements.get("base_uri", default_base_uri).rstrip("/")
    else:
        base_uri = default_base_uri

    element_info = domain_elements[element_type + "s"].get(element, None)

    if element_info is None:
        raise ValueError(
            f"The element {element} has not been declared in the domain {domain}"
        )

    return element_info, container_name, base_uri


def get_format(domain: str, element: str, element_type: str = "table") -> str:
    element_info, _, _ = get_info(domain, element, element_type)
    return element_info.get("format", "parquet")


def get_kwargs(domain: str, element: str, element_type: str = "table") -> str:
    element_info, _, _ = get_info(domain, element, element_type)
    return element_info.get("kwargs", {})


def get_uri(
    domain: str, element: str, element_type: str = "table", version: str = ""
) -> str:

    element_info, container_name, base_uri = get_info(domain, element, element_type)
    base_uri: str = base_uri
    container_name: str = container_name
    path: str = element_info["path"].lstrip("/")
    version = version + "/" if version else version

    base_uri = (
        Template(base_uri, undefined=StrictUndefined)
        .render(container_name=container_name)
        .rstrip("/")
    )

    uri = f"{base_uri}/{path}"
    return uri


def load_pickle(domain: str, pickled_object: str) -> Any:
    config = get_config()
    domain_pickles = config["data"][domain]
    pickles_info = domain_pickles["pickles"][pickled_object]
    info_format = pickles_info["format"]
    uri = get_uri(domain, pickled_object, "pickle")
    fs, path = get_fs_path(uri)

    if info_format != "pickle":
        raise ValueError(
            f"The dataset format for '{domain}.{pickled_object}' must be "
            f"'pickle' instead of '{info_format}'"
        )

    with fs.open(path) as f:
        logger.info(f"Loading '{domain}.{pickled_object}' from {path} as pickle")
        return pickle.load(f)


def load_table(domain: str, table: str, backend="pandas", **kwargs_override):
    if backend == "pandas":
        return load_table_pandas(domain=domain, table=table, **kwargs_override)
    else:
        raise ValueError(
            f"The backend {backend} is not currently supported."
            " The supported backend is 'pandas'."
        )


def load_table_pandas(domain: str, table: str, **kwargs_override) -> pd.DataFrame:
    config = get_config()
    domain_tables = config["data"][domain]
    table_info = domain_tables["tables"][table]

    if table_info["format"] == "csv":
        read_func = pd.read_csv
    elif table_info["format"] == "xlsx":
        read_func = pd.read_excel
    elif table_info["format"] == "parquet":
        read_func = pd.read_parquet
    elif table_info["format"] == "xls":
        read_func = pd.read_excel
    else:
        raise NotImplementedError(
            f"The format {table_info['format']} is currently not supported in Pandas"
        )

    uri = get_uri(domain, table)
    fs, path = get_fs_path(uri)

    kwargs = table_info.get("kwargs", None) or {}
    kwargs = dict(kwargs)
    kwargs.update(kwargs_override)

    if "extract_date" in kwargs:
        path = f'/{kwargs["extract_date"]}/{table_info.filename}'
        del kwargs["extract_date"]

    logger.info(f"Loading {domain}::{table} from {uri}")

    with fs.open(path) as file_handler:
        df = read_func(file_handler, **kwargs)
    logger.info("Data loaded sucessfully")

    if domain == "raw" and table_info["source"] == "IBGE":
        df = df.reset_index().drop(columns=["level_1"])

    return df


def save_pickle(obj: Any, domain: str, pickled_object: str) -> None:
    config = get_config()
    domain_pickles = config["data"][domain]
    pickles_info = domain_pickles["pickles"][pickled_object]
    info_format = pickles_info["format"]
    uri = get_uri(domain, pickled_object, "pickle")
    fs, path = get_fs_path(uri)

    if info_format != "pickle":
        raise ValueError(
            f"The dataset format for '{domain}.{pickled_object}' must be "
            f"'pickle' instead of '{info_format}'"
        )

    make_parents(fs, path)
    with fs.open(path, "wb") as f:
        logger.info(f"Saving '{domain}.{pickled_object}' into {path} as pickle")
        return pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def save_table(df, domain, table, backend="pandas", **kwargs) -> None:

    config_kwargs = get_kwargs(domain, table)
    kwargs = {**kwargs, **config_kwargs}

    if backend == "pandas":
        save_table_pandas(df, domain, table, **kwargs)
    else:
        raise ValueError(
            f"The backend {backend} is not currently supported."
            " The supported backend is 'pandas'."
        )


def save_table_pandas(df: pd.DataFrame, domain, table, **kwargs):
    fmt = get_format(domain, table)
    uri = get_uri(domain, table)
    fs, path = get_fs_path(uri)
    if fs.isdir(str(path)):
        fs.rm(str(path), recursive=True)
    elif fs.exists(str(path)) and not fs.isdir(str(path)):
        fs.rm(str(path))
    logger.info(f"Saving {domain}::{table} into {uri}")
    parent, _ = path.rstrip("/").rsplit("/", 1)
    fs.mkdirs(parent, exist_ok=True)
    if fmt == "parquet":
        df.to_parquet(
            path,
            partition_cols=kwargs.get("partitionBy", None),
            filesystem=fs,
        )
    elif fmt == "csv":
        _save_upload(
            lambda stream: df.to_csv(stream, index=kwargs.get("index", None)), fs, path
        )

    else:
        raise NotImplementedError(f"Format {fmt} not supported")
    logger.info("Data saved sucessfully")


def _save_upload(save_func, fs: fsspec.AbstractFileSystem, path):
    if fs.protocol == "file":
        with fs.open(str(path), mode="w") as stream:
            save_func(stream)
    else:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "data"
            with tmp.open("w") as stream:
                save_func(stream)
            fs.upload(str(tmp), path)
