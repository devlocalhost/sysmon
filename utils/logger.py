import logging

# from . import util


def define_logger(plugin_name):
    logging.basicConfig(
        filename="sysmon.log",
        # filename="sysmon.log" if util.DEBUGGING else "/dev/null",
        # level=logging.DEBUG if util.DEBUGGING else logging.INFO,
        level=logging.DEBUG,
        datefmt="%X",
        format="%(asctime)s.%(msecs)03d - %(name)-16s %(funcName)-30s -> %(message)s",
        filemode="w",
    )

    logger = logging.getLogger(plugin_name)

    return logger
