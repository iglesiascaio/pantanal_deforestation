# -*- coding: utf-8 -*-
import pandas as pd
import unicodedata
import pathlib
import zipfile


# from plot_api.enums import ScenarioStatus
from typing import Optional, OrderedDict
from runner import io
from pydantic import BaseModel
import datetime
import numpy as np
import os


from gamma.config import get_config
from gamma.config.dump_dict import to_dict

DICT_PROBLEMATIC_LOCATION = {}
DICT_PROBLEMATIC_PRODUCT = {}
DICT_PROBLEMATIC_TRANSPORTER = {}


def pipe(original):
    class PipeInto(object):
        data = {"function": original}

        def __init__(self, *args, **kwargs):
            self.data["args"] = args
            self.data["kwargs"] = kwargs

        def __rrshift__(self, other):
            return self.data["function"](
                other, *self.data["args"], **self.data["kwargs"]
            )

    return PipeInto


@pipe
def adjust_case(s, to="upper"):
    if isinstance(s, str):
        if to == "upper":
            return s.upper()
        elif to == "lower":
            return s.lower()
        else:
            return "error_adjust_case"
    return s


@pipe
def remove_spaces(s):
    if isinstance(s, str):
        return (
            s.strip().replace(" -  ", " - ").replace("  - ", " - ").replace("  ", " ")
        )
    return s


@pipe
def remove_special_char(s):
    if s is None:
        return None
    if isinstance(s, float) or isinstance(s, int):
        return s
    else:
        decoded = unicodedata.normalize("NFD", s)
        decoded = decoded.encode("ascii", "ignore").decode("utf-8")
        return decoded


# Auxiliary functions
def fix_string(s):
    fixed_s = s >> remove_special_char() >> remove_spaces() >> adjust_case()
    return fixed_s
