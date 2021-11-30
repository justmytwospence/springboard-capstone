import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# DEBUG and above to file
file_handler = logging.FileHandler("logs/bitcoin-etl.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# ERROR and above to console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)
