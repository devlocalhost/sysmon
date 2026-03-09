import logging

# this part feels ugly to me. i do it so nicely in pyspodl...
from .config import Config, ConfigError

config = Config().read_config()

try:
    DEBUGGING = config["misc"]["debugging"]

except ConfigError:
    DEBUGGING = False
# this part feels ugly to me. i do it so nicely in pyspodl...

def create_logger(plugin_name):
    logging.basicConfig(
        filename="sysmon.log" if DEBUGGING else "/dev/null",
        level=logging.DEBUG if DEBUGGING else logging.INFO,
        datefmt="%X",
        format="%(asctime)s.%(msecs)03d - %(name)-16s %(funcName)-30s -> %(message)s",
        filemode="w",
    )

    logger = logging.getLogger(plugin_name)

    return logger
