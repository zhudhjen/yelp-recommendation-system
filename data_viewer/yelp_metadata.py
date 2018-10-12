from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import ForeignKey

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    def __init__(self, user):
        self.user_id = user['user_id']
        self.name = user['name']
        self.review_count = user['review_count']
        self.yelping_since = user['yelping_since']
        self.useful = user['useful']
        self.funny = user['funny']
        self.cool = user['cool']
        self.fans = user['fans']
        self.average_stars = user['average_stars']

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

    def __init__(self, business):
        self.business_id = business['business_id']
        self.name = business['name']
        self.neighborhood = business['neighborhood']
        self.address = business['address']
        self.city = business['city']
        self.state = business['state']
        self.postal_code = business['postal_code']
        self.latitude = business['latitude']
        self.longitude = business['longitude']
        self.stars = business['stars']
        self.review_count = business['review_count']
        self.is_open = business['is_open']

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

    def __init__(self, review):
        self.review_id = review['review_id']
        self.user_id = review['user_id']
        self.business_id = review['business_id']
        self.stars = review['stars']
        self.date = review['date']
        self.text = review['text']
        self.useful = review['useful']
        self.funny = review['funny']
        self.cool = review['cool']

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


def load_session():
    engine = create_engine('sqlite:///yelp.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
