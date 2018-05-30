import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

conn = sqla.create_engine('mysql+pymysql://tester:tester@localhost/project?host=localhost?port=3306')
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    username = sqla.Column('username', sqla.VARCHAR(64), primary_key=True)
    email = sqla.Column('email', sqla.VARCHAR(64))
    firstName = sqla.Column('firstName', sqla.VARCHAR(64))
    lastName = sqla.Column('lastName', sqla.VARCHAR(64))
    password = sqla.Column('password', sqla.VARCHAR(64))
    country = sqla.Column('country', sqla.VARCHAR(64))

    preference = relationship('Preference', secondary="preference_user")
    favorite_place = relationship('Place', secondary="favorite_place")
    favorite_event = relationship('Event', secondary="favorite_event")

class Friend(Base):
    __tablename__ = 'friend'
    username1 = sqla.Column('username1', sqla.VARCHAR(64), sqla.ForeignKey("user.username"), primary_key=True)
    username2 = sqla.Column('username2', sqla.VARCHAR(64), sqla.ForeignKey("user.username"), primary_key=True)

class Preference(Base):
    __tablename__ = 'preference'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True)
    name = sqla.Column('name', sqla.VARCHAR(64))

class Preference_User(Base):
    __tablename__ = 'preference_user'
    preference_id = sqla.Column('preference_id', sqla.Integer, sqla.ForeignKey("preference.id"), primary_key=True)
    user_username = sqla.Column('user_username', sqla.VARCHAR(64), sqla.ForeignKey("user.username"), primary_key=True)

class Place(Base):
    __tablename__ = 'place'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True)
    place_id = sqla.Column('place_id', sqla.VARCHAR(64))

class Favorite_Place(Base):
    __tablename__ = 'favorite_place'
    user_username = sqla.Column('user_username', sqla.VARCHAR(64), sqla.ForeignKey("user.username"), primary_key=True)
    place_id = sqla.Column('place_id', sqla.Integer, sqla.ForeignKey("place.id"), primary_key=True)

class Event(Base):
    __tablename__ = 'event'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True)
    name = sqla.Column('name', sqla.VARCHAR(64))
    category = sqla.Column('category', sqla.VARCHAR(64))
    description = sqla.Column('description', sqla.VARCHAR(64))
    location = sqla.Column('location', sqla.VARCHAR(64))
    startDate = sqla.Column('startDate', sqla.DATETIME)
    endDate = sqla.Column('endDate', sqla.DATETIME)
    image = sqla.Column('image', sqla.VARCHAR(64))

class Favorite_Event(Base):
    __tablename__ = 'favorite_event'
    user_username = sqla.Column('user_username', sqla.VARCHAR(64), sqla.ForeignKey("user.username"), primary_key=True)
    event_id = sqla.Column('event_id', sqla.Integer, sqla.ForeignKey("event.id"), primary_key=True)

class Persister():
    def persist_object(self, obj):
        self.session.add(obj)
        self.session.commit()

    def getUser(self, name):
        return self.session.query(User).filter(User.username == name).first()

    def getCategories(self):
        return self.session.query(Preference).all()

    def __init__(self):
        Session = sessionmaker(bind=conn)
        self.session = Session()

Base.metadata.create_all(conn)