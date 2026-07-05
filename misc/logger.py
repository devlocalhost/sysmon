import logging

from .config import Config, ConfigError

config = Config().load_config()
DEBUGGING = config["misc"]["debugging"]

def create_logger(plugin_name):
    logging.basicConfig(
        filename="sysmon.log" if DEBUGGING else "/dev/null",
        level=logging.DEBUG if DEBUGGING else logging.INFO,
        datefmt="%X",
        format="%(asctime)s.%(msecs)03d - %(filename)-16s %(funcName)-30s -> %(message)s",
        filemode="w",
    )

    logger = logging.getLogger(plugin_name)

    return logger
