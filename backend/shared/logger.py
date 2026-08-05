import sys
from loguru import logger

# Remove default handler
logger.remove()

# Add structured console handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

def get_logger(name: str):
    return logger.bind(name=name)
