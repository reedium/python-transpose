import logging


def create_logger(logger_name: str) -> logging:
    logger = logging.getLogger(logger_name)
    return logger
