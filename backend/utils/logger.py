import sys
from loguru import logger
from config.settings import settings

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
    "<level>{message}</level>"
)


def setup_logger():
    logger.remove()

    # Console
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level=settings.log_level,
        colorize=True,
    )

    # Dosya
    logger.add(
        settings.log_file,
        format=LOG_FORMAT,
        level=settings.log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    return logger


log = setup_logger()
