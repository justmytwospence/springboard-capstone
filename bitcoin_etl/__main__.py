import json
import logging
import sys
from pprint import pprint

from bitcoin_etl.models import Block, Transaction

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

with open('data/transactions.txt', 'w') as t, open('data/blocks.txt', 'w') as b:
    for line in sys.stdin:
        try:
            json_line = json.loads(line)
        except json.decoder.JSONDecodeError as e:
            logger.error("This line was not decoded properly: %s", line)
        if json_line['type'] == 'block':
            logger.info(f"Writing block {json_line['number']}")
            b.write(line)
        # elif json_line['type'] == 'transaction':
        #     logger.info(f"Writing transaction {json_line['hash']} from block {json_line['block_number']}")
        #     t.write(line)
        else:
            raise Exception("JSON blob was not of type 'block' or 'transaction'")
