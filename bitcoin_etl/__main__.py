import itertools
import json
import logging
import sys

from sqlalchemy.exc import IntegrityError

from bitcoin_etl.models import (Address, AddressInteraction, Block, Input,
                                Output, Session, Transaction)

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


def process_inputs(transaction_inputs, transaction_hash):
    input_addresses = []  # collect input addresses for AddressInteractions
    for transaction_input in transaction_inputs:
        addresses = transaction_input.pop('addresses')
        input_addresses.extend(addresses)

        logger.info(f"Writing input {transaction_input['index']}")
        transaction_input = Input(transaction_hash=transaction_hash, **transaction_input)
        session.add(transaction_input)
        session.commit()

        # write addresses to Address table if they don't exist
        for address in addresses:
            logger.info("Writing address %s", address)
            address = Address(hash=address)
            session.add(address)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()

            # add input <> address combo to bridge table
            transaction_input.addresses.append(address)

    return input_addresses


def process_outputs(transaction_outputs, transaction_hash):
    output_addresses = []  # collect input addresses for AddressInteractions
    for transaction_output in transaction_outputs:
        addresses = transaction_output.pop('addresses')
        output_addresses.extend(addresses)

        logger.info(f"Writing output {transaction_output['index']}")
        transaction_output = Output(transaction_hash=transaction_hash, **transaction_output)
        session.add(transaction_output)
        session.commit()

        # write addresses to Address table if they don't exist
        for address in addresses:
            logger.info("Writing address %s", address)
            address = Address(hash=address)
            session.add(address)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()

            # add output <> address combo to bridge table
            transaction_output.addresses.append(address)

    return output_addresses


for line in sys.stdin:

    try:
        line_dict = json.loads(line)
    except json.decoder.JSONDecodeError as e:
        logger.error("This line was not decoded properly: %s", line)

    line_dict.pop('item_id')
    line_type = line_dict.pop('type')

    with Session() as session:

        if line_type == 'block':
            logger.info(f"Writing block {line_dict['number']}")
            session.add(Block(**line_dict))
            session.commit()

        elif line_type == 'transaction':
            transaction_inputs = line_dict.pop('inputs')
            transaction_outputs = line_dict.pop('outputs')

            logger.info(f"Writing transaction {line_dict['hash']} from block {line_dict['block_number']}")
            session.add(Transaction(**line_dict))
            session.commit()

            input_addresses = process_inputs(transaction_inputs, line_dict['hash'])
            output_addresses = process_outputs(transaction_outputs, line_dict['hash'])

            # write address interactions to AddressInteractions table
            for input_address, output_address in itertools.product(input_addresses, output_addresses):
                logger.info("Writing address interaction between %s and %s", input_address, output_address)
                session.add(AddressInteraction(transaction_hash=line_dict['hash'],
                                               input_address=input_address,
                                               output_address=output_address))
                session.commit()

        # log an error and raise exception if not "block" or "transaction"
        else:
            error_message = f"JSON blob was  of type {line_dict['type']}, it needs to be of type 'block' or 'transaction'."
            logger.error(error_message)
            raise Exception(error_message)
