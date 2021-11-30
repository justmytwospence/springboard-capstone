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
    hash = Column(String)
    size = Column(BigInteger)
    stripped_size = Column(BigInteger)
    weight = Column(BigInteger)
    number = Column(BigInteger, primary_key=True)
    version = Column(BigInteger)
    merkle_root = Column(String)
    timestamp = Column(BigInteger)
    nonce = Column(String)
    bits = Column(String)
    coinbase_param = Column(String)
    transaction_count = Column(BigInteger)

    # relationships
    transactions = relationship('Transaction')


class Address(Base):
    __tablename__ = "Address"

    # fields
    hash = Column(String)

    # relationships
    transactions = relationship("Transaction",
                                secondary="TransactionIO",
                                back_populates="transactions")

class Transaction(Base):
    __tablename__ = "Transaction"

    # fields
    hash = Column(String, primary_key=True)
    block_number = Column(BigInteger, ForeignKey('Block.number'))
    size = Column(BigInteger)
    virtual_size = Column(BigInteger)
    version = Column(BigInteger)
    lock_time = Column(BigInteger)
    block_hash = Column(String)
    block_timestamp = Column(BigInteger)
    is_coinbase = Column(Boolean)
    index = Column(BigInteger)
    # inputs = Column([]transaction_input)
    # outputs = Column([]transaction_output)
    input_count = Column(BigInteger)
    output_count = Column(BigInteger)
    input_value = Column(BigInteger)
    output_value = Column(BigInteger)
    fee = Column(BigInteger)

    # relationships
    block = relationship("Block", back_populates="Transaction")
    # relationships
    addresses = relationship("Transaction",
                             secondary="TransactionIO",
                             back_populates="transactions")


class TransactionIO(Base):
    __tablename__ = "TransactionIO"

    # fields
    transaction_id = Column(String,
                            ForeignKey("Transaction.hash"),
                            primary_key=True)
    input = Column(String,
                   ForeignKey("Address.hash"),
                   primary_key=True)
    output = Column(String,
                    ForeignKey("Address.hash"),
                    primary_key=True)


engine = create_engine(
    f"postgresql+psycopg2://postgres@localhost:5432/bitcoin_etl")
Session = sessionmaker(engine)
Base.metadata.create_all(engine)
