import sys

from loguru import logger


def init_logger():
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    logger.add("logs/app.log", rotation="1 day", retention="7 days")

    return logger
