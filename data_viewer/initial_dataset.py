from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import ForeignKey


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True)
    name = Column(String)
    review_count = Column(Integer)
    yelping_since = Column(String)
    # TODO friends
    useful = Column(Integer)
    funny = Column(Integer)
    cool = Column(Integer)
    fans = Column(Integer)
    # TODO elite
    average_stars = Column(Float)
    # TODO some compliments


class Business(Base):
    __tablename__ = 'businesses'
    id = Column(Integer, primary_key=True)
    business_id = Column(String, unique=True)
    name = Column(String)
    neighborhood = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    stars = Column(Float)
    review_count = Column(Integer)
    is_open = Column(Integer)
    # TODO attributes, categories, hours


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    review_id = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    business_id = Column(Integer, ForeignKey('businesses.business_id'))
    stars = Column(Integer)
    date = Column(String)
    text = Column(String)
    useful = Column(Integer)
    funny = Column(Integer)
    cool = Column(Integer)
