from datetime import datetime, time
from typing import List, Dict, Any
import sys
import os
from sqlalchemy import Time
from flask_sqlalchemy import SQLAlchemy

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

from sqlalchemy import Column, Integer, String, Float, \
    create_engine, Sequence, Identity, ForeignKey, delete, Boolean, JSON, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, DeclarativeBase, Mapped, mapped_column
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

db = SQLAlchemy()

class Base(DeclarativeBase):
    pass

class Client(Base):
    """
    Asiakkaiden tietokantamalli
    """
    __tablename__ = 'client'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    credit_card: Mapped[str] = mapped_column(String(50))
    car_number: Mapped[str] = mapped_column(String(10))

    def __repr__(self):
        return f"Asiakas {self.name} {self.surname}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}


class Parking(Base):
    """
    Pysäköintiä tietokantamalli
    """
    __tablename__ = 'parking'
    id: Mapped[int] = mapped_column(Integer, Sequence('parking_id_seq'), primary_key=True)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    opened: Mapped[bool] = mapped_column(Boolean)
    count_places: Mapped[int] = mapped_column(Integer, nullable=False)
    count_available_places: Mapped[int] = mapped_column(Integer, nullable=False)
    opening_time: Mapped[Time] = mapped_column(Time, nullable=False)
    closing_time: Mapped[Time] = mapped_column(Time, nullable=False)

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}

def is_parking_open(opening_time: time, closing_time: time) -> bool:
    current_time = datetime.now().time()
    if opening_time <= closing_time:
        return opening_time <= current_time <= closing_time
    else:  # Handles cases where parking is open overnight
        return current_time >= opening_time or current_time <= closing_time

class ClientParking(Base):
    """
    Asiakkaiden - parkkipaikkojen tietokantamalli
    """
    __tablename__ = 'client_parking'
    id: Mapped[int] = mapped_column(Integer, Sequence('parking_id_seq'), primary_key=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey('client.id'))
    parking_id: Mapped[int] = mapped_column(Integer, ForeignKey('parking.id'))
    time_in: Mapped[datetime] = mapped_column(DateTime, nullable=True, server_default=func.now())
    time_out: Mapped[datetime] = mapped_column(DateTime, nullable=True, server_default=func.now())