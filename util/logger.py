import logging
import os

os.makedirs("log", exist_ok=True)


def setup_logger(plugin_name):
    logging.basicConfig(
        filename="log/sysmon.log",
        level=logging.DEBUG,
        datefmt="%X",
        format=f"%(asctime)s.%(msecs)03d - %(name)s -> %(message)s",
        filemode="w",
    )

    logger = logging.getLogger(plugin_name)

    return logger
