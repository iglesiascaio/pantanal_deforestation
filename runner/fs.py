from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlsplit

import tempfile
import fsspec
import logging
from gamma.config import get_config
from concurrent.futures import ThreadPoolExecutor

CONFIG_SECTION = "filesystems"


logger = logging.getLogger(__name__)


def get_fs_path(uri: str) -> Tuple[fsspec.AbstractFileSystem, str]:
    uri = uri.strip()

    if uri.startswith("/"):
        return fsspec.filesystem("file"), uri

    if ":" not in uri:
        raise ValueError(f"Invalid URI; or local paths should be absolute: {uri}")

    scheme: str = uri.strip().split(":", 1)[0]

    if scheme == "" or scheme == "file":
        return fsspec.filesystem("file"), urlsplit(uri).path

    if scheme in ("abfs", "abfss"):
        return _get_fs_path_abfs(uri)

    raise ValueError(f"No handler implemented for scheme '{scheme}' in URI: {uri}")


def _get_fs_path_abfs(uri: str) -> fsspec.AbstractFileSystem:
    """
    Define a filesystem using the Storage Account connection string
    """
    # TODO: adjust credentials handling from secure location

    u = urlsplit(uri)
    account_name = u.hostname.split(".", 1)[0]
    path = u.path.lstrip("/")
    if u.username:
        path = f"{u.username}/{path}"
    credential = _get_credentials()
    fs = fsspec.filesystem("abfs", account_name=account_name, credential=credential)
    return fs, path


# TODO: implement secure credential handling when its available
def _get_credentials():
    ...


def get_storage_options(uri: str) -> Dict[str, Any]:
    """Lookup in the configuration for matching fsspec paramters for the given URI

    We expect a ``filesystems`` section in the config. For each entry,
    we'll try to match, in order
        ``(scheme, host, user)``,
        ``(scheme, host, *)``,
        ``(scheme, *, *)``,

    If we find any match, we use the parameters to configure a fsspec ``FileSystem``
    instance.
    """

    # decompose uri
    u = urlsplit(uri)

    scheme = u.scheme or "file"
    host = f"{u.hostname}:{u.port}" if u.port else u.hostname
    host = host if host else None
    user = u.username if u.username else None

    # get possible matching keys
    keys = [(scheme, host, user), (scheme, host, None), (scheme, None, None)]

    entries = get_config().get(CONFIG_SECTION, [])

    opts: Optional[Config] = None
    for key in keys:
        for entry in entries:
            entry_key = entry.get("scheme"), entry.get("host"), entry.get("user")
            if key == entry_key:
                opts = entry
                break

    # try to match a wildcard
    if opts is None:
        raise Exception(
            f"Key not found in config.storage_options: ({scheme}, {host}, {user})"
        )

    # Augment options with known URI components
    opts = opts.to_dict()
    if opts["scheme"] == "s3":
        del opts["host"]

    del opts["scheme"]
    return opts


def get_project_uri(return_default=True) -> str:
    """Get a local URI pointing to the project root"""
    return str(Path(__file__).absolute().parents[1])


def make_parents(fs, path) -> Any:
    """Make parent dirs of path"""
    parent = path.rsplit("/", 1)[0]
    fs.makedirs(parent, exist_ok=True)


def copy_tree(
    src_fs: fsspec.AbstractFileSystem,
    src_path,
    dst_fs: fsspec.AbstractFileSystem,
    dst_path,
):
    with ThreadPoolExecutor(max_workers=32) as executor:
        with tempfile.TemporaryDirectory() as td:
            prefix = len(src_path) + 1
            # get files recursively
            futures = []
            logger.info(f"Copying files from {src_path} to {dst_path}")
            for folder, _, files in src_fs.walk(src_path):
                rel_folder = folder[prefix:].rstrip("/")

                if not rel_folder:
                    dst_folder = f"{td}"
                else:
                    dst_folder = f"{td}/{rel_folder}"
                    Path(dst_folder).mkdir(parents=True, exist_ok=True)

                for file in files:
                    src = f"{folder}/{file}"
                    dst = f"{dst_folder}/{file}"
                    fut = executor.submit(src_fs.download, src, dst)
                    futures.append(fut)

            # wait futures
            for fut in futures:
                fut.result()

            # upload files recursively
            td = Path(td)
            parents = set()
            futures.clear()
            for file in td.rglob("*"):
                rel_file = str(file.relative_to(td))
                dst_file = f"{dst_path.rstrip('/')}/{rel_file}"
                parent = dst_file.rsplit("/", 1)[0]
                if parent not in parents:
                    parents.add(parent)
                dst_fs.makedirs(parent, exist_ok=True)
                lpath = str(file.absolute())
                fut = executor.submit(dst_fs.upload, lpath, dst_file)
                futures.append(fut)

            # wait futures
            for fut in futures:
                fut.result()
