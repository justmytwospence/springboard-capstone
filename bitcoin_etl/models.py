import logging

from sqlalchemy import (BigInteger, Boolean, Column, ForeignKey, Integer,
                        String, UniqueConstraint, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

logger = logging.getLogger(__name__)
Base = declarative_base()


class Block(Base):
    __tablename__ = "Block"

    # fields
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

    # relationships
    transactions = relationship("Transaction", back_populates="block")


class Transaction(Base):
    __tablename__ = "Transaction"

    # fields
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

    # relationships
    block = relationship("Block", back_populates="transactions")


class TransactionInput(Base):
    __tablename__ = "TransactionInput"

    transaction_hash = Column(String,
                              ForeignKey("Transaction.hash"),
                              primary_key=True)
    index = Column(BigInteger, primary_key=True)
    spent_transaction_hash = Column(String)
    spent_output_index = Column(BigInteger)
    script_asm = Column(String)
    script_hex = Column(String)
    sequence = Column(BigInteger)
    required_signatures = Column(BigInteger)
    type = Column(String)
    value = Column(BigInteger)


class TransactionOutput(Base):
    __tablename__ = "TransactionOutput"

    transaction_hash = Column(String,
                              ForeignKey("Transaction.hash"),
                              primary_key=True)
    index = Column(BigInteger, primary_key=True)
    script_asm = Column(String)
    script_hex = Column(String)
    required_signatures = Column(BigInteger)
    type = Column(String)
    value = Column(BigInteger)


class TransactionIO(Base):
    __tablename__ = "TransactionIO"

    id = Column(Integer, primary_key=True)
    transaction_hash = Column(String, ForeignKey("Transaction.hash"))
    input_address = Column(String)
    output_address = Column(String)


engine = create_engine(
    f"postgresql+psycopg2://postgres@localhost:5432/bitcoin_etl")
Session = sessionmaker(engine)
Base.metadata.create_all(engine)
