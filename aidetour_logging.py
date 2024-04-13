# aidetour_logging

from loguru import logger

def setup_logger(log_name):
    logger.remove()  # remove default handlers to ensure no duplicate logging
    res = logger.add(log_name, mode="w", encoding="utf-8") # "w" = don't append
    # logger.info(f"aidetour_logging: setup_logger: log_name={log_name} res={res}")
