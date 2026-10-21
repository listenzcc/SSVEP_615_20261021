from loguru import logger

logger.add("log/ssvep-display.log", rotation="1 MB")
