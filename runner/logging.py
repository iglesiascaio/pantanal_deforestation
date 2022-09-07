# flake8: noqa

import logging
import logging.config
from gamma.config import get_config, to_dict

# __all__: all public functions

# exported
def initialize_logging():
    """Initialize logging from configuration"""
    log_cfg = to_dict(get_config()["logging"])
    logging.config.dictConfig(log_cfg)
