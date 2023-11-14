import logging
import os

from . import util


def setup_logger(plugin_name):
    logging.basicConfig(
        filename="sysmon.log",
        level=logging.DEBUG if util.DEBUGGING else logging.INFO,
        datefmt="%X",
        format=f"%(asctime)s.%(msecs)03d - %(name)s -> %(message)s",
        filemode="w",
    )

    logger = logging.getLogger(plugin_name)

    return logger
