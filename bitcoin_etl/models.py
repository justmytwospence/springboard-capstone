import logging

from sqlalchemy import (BigInteger, Boolean, Column, ForeignKey, Integer,
                        String, UniqueConstraint, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

logger = logging.getLogger(__name__)
Base = declarative_base()


class Block(Base):
    __tablename__ = "Block"

    number = Column(BigInteger, primary_key=True)
    hash = Column(String)
    size = Column(BigInteger)
    stripped_size = Column(BigInteger)
    weight = Column(BigInteger)
    version = Column(BigInteger)
    merkle_root = Column(String)
    timestamp = Column(BigInteger)
    nonce = Column(String)
    bits = Column(String)
    coinbase_param = Column(String)
    transaction_count = Column(BigInteger)

    transactions = relationship("Transaction", back_populates="block")


class Transaction(Base):
    __tablename__ = "Transaction"

    hash = Column(String, primary_key=True)
    block_number = Column(BigInteger, ForeignKey("Block.number"))
    size = Column(BigInteger)
    virtual_size = Column(BigInteger)
    version = Column(BigInteger)
    lock_time = Column(BigInteger)
    block_hash = Column(String)
    block_timestamp = Column(BigInteger)
    is_coinbase = Column(Boolean)
    index = Column(BigInteger)
    input_count = Column(BigInteger)
    output_count = Column(BigInteger)
    input_value = Column(BigInteger)
    output_value = Column(BigInteger)
    fee = Column(BigInteger)

    block = relationship("Block", back_populates="transactions")


class Address(Base):
    __tablename__ = "Address"

    id = Column(Integer, primary_key=True)
    hash = Column(String)


class Input(Base):
    __tablename__ = "Input"

    id = Column(Integer, primary_key=True)
    transaction_hash = Column(String, ForeignKey("Transaction.hash"))
    index = Column(BigInteger)
    spent_transaction_hash = Column(String)
    spent_output_index = Column(BigInteger)
    script_asm = Column(String)
    script_hex = Column(String)
    sequence = Column(BigInteger)
    required_signatures = Column(BigInteger)
    type = Column(String)
    value = Column(BigInteger)

    addresses = relationship("Address", secondary="InputAddress")


class InputAddress(Base):
    __tablename__ = "InputAddress"

    input_id = Column(Integer, ForeignKey("Input.id"), primary_key=True)
    address_id = Column(Integer, ForeignKey("Address.id"), primary_key=True)


class Output(Base):
    __tablename__ = "Output"

    id = Column(Integer, primary_key=True)
    transaction_hash = Column(String, ForeignKey("Transaction.hash"))
    index = Column(BigInteger)
    script_asm = Column(String)
    script_hex = Column(String)
    required_signatures = Column(BigInteger)
    type = Column(String)
    value = Column(BigInteger)

    addresses = relationship("Address", secondary="OutputAddress")


class OutputAddress(Base):
    __tablename__ = "OutputAddress"

    output_id = Column(Integer, ForeignKey("Output.id"), primary_key=True)
    address_id = Column(Integer, ForeignKey("Address.id"), primary_key=True)


class AddressInteraction(Base):
    __tablename__ = "AddressInteraction"

    id = Column(Integer, primary_key=True)
    transaction_hash = Column(String, ForeignKey("Transaction.hash"))
    input_address = Column(String)
    output_address = Column(String)


engine = create_engine(
    f"postgresql+psycopg2://postgres@localhost:5432/bitcoin_etl")
Session = sessionmaker(engine)
Base.metadata.create_all(engine)
