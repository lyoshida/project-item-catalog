# coding: utf-8

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Item(Base):
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    # price = Column(String(8))
    # course = Column(String(250))
    # restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    # restaurant = relationship(Restaurant)


engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
