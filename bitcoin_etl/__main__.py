import itertools
import json
import logging
import sys

from sqlalchemy.exc import IntegrityError

from bitcoin_etl.models import (Block, Session, Transaction, TransactionInput,
                                TransactionIO, TransactionOutput)

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

# INFO and above to console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

for line in sys.stdin:

    try:
        line_dict = json.loads(line)
    except json.decoder.JSONDecodeError as e:
        logger.error("This line was not decoded properly: %s", line)

    line_dict.pop('item_id')
    line_type = line_dict.pop('type')

    with Session() as session:

        # write blocks to the Block table
        if line_type == 'block':
            logger.info(f"Writing block {line_dict['number']}")
            session.add(Block(**line_dict))
            session.commit()

        elif line_type == 'transaction':
            logger.info(
                f"Writing transaction {line_dict['hash']} from block {line_dict['block_number']}")
            transaction_inputs = line_dict.pop('inputs')
            transaction_outputs = line_dict.pop('outputs')

            # write transactions to the Transaction table
            session.add(Transaction(**line_dict))
            session.commit()

            # write inputs to TransactionInput table
            input_addresses = []
            for transaction_input in transaction_inputs:
                addresses = transaction_input.pop('addresses')
                input_addresses.extend(addresses)
                session.add(TransactionInput(transaction_hash=line_dict['hash'],
                                             **transaction_input))
                session.commit()

            # write outputs to TransactionOutput table
            output_addresses = []
            for transaction_output in transaction_outputs:
                addresses = transaction_output.pop('addresses')
                output_addresses.extend(addresses)
                session.add(TransactionOutput(transaction_hash=line_dict['hash'],
                                              **transaction_output))
                session.commit()

            for input_address, output_address in itertools.product(input_addresses, output_addresses):
                session.add(TransactionIO(transaction_hash=line_dict['hash'],
                                          input_address=input_address,
                                          output_address=output_address))
                session.commit()

        # log an error and raise exception if not "block" or "transaction"
        else:
            error_message = f"JSON blob was  of type {line_dict['type']}, it needs to be of type 'block' or 'transaction'"
            logger.error(error_message)
            raise Exception(error_message)
