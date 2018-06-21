
import sys
import sqlalchemy as sqla
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from passlib.hash import pbkdf2_sha256
import time, os
from hashlib import md5


conn = sqla.create_engine('mysql+pymysql://root:@localhost/project?host=127.0.0.1?port=3306')


Base = declarative_base()


class Friend(Base):
    __tablename__ = 'friend'
    username1 = sqla.Column('username1', sqla.VARCHAR(64), sqla.ForeignKey("user.username"), primary_key=True)
    username2 = sqla.Column('username2', sqla.VARCHAR(64), sqla.ForeignKey("user.username"), primary_key=True)

class User(Base,UserMixin):
    __tablename__ = 'user'
    username = sqla.Column('username', sqla.VARCHAR(64), primary_key=True)
    email = sqla.Column('email', sqla.VARCHAR(64))
    firstName = sqla.Column('first_name', sqla.VARCHAR(64))
    lastName = sqla.Column('last_name', sqla.VARCHAR(64))
    password = sqla.Column('password', sqla.VARCHAR(64))
    country = sqla.Column('country', sqla.VARCHAR(64))


    def get_id(self):
        return self.username


    def avatar(self):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s=24'.format(digest)

    preference = relationship('Category', secondary="preference_user", backref='preference')
    favorite_place = relationship('Place', secondary="favorite_place")
    favorite_event = relationship('Event', secondary="favorite_event")
    events = relationship('Event')

class Category(Base):
    __tablename__ = 'category'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True)
    name = sqla.Column('name', sqla.VARCHAR(64))
    user = relationship('User', secondary="preference_user")

class Preference_User(Base):
    __tablename__ = 'preference_user'
    category_id = sqla.Column('category.id', sqla.Integer, sqla.ForeignKey("category.id"), primary_key=True)
    user_username = sqla.Column('user.username', sqla.VARCHAR(64), sqla.ForeignKey("user.username"), primary_key=True)

class Place(Base):
    __tablename__ = 'place'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True)
    place_id = sqla.Column('place.id', sqla.VARCHAR(64))

class Favorite_Place(Base):
    __tablename__ = 'favorite_place'
    user_username = sqla.Column('user.username', sqla.VARCHAR(64), sqla.ForeignKey("user.username"), primary_key=True)
    place_id = sqla.Column('place.id', sqla.Integer, sqla.ForeignKey("place.id"), primary_key=True)

class Event(Base):
    __tablename__ = 'event'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True)
    name = sqla.Column('name', sqla.VARCHAR(64))
    description = sqla.Column('description', sqla.VARCHAR(64))
    location = sqla.Column('location', sqla.VARCHAR(64))
    startDate = sqla.Column('start_date', sqla.DATE)
    startTime = sqla.Column('start_time', sqla.TIME)
    endDate = sqla.Column('end_date', sqla.DATE)
    endTime = sqla.Column('end_time', sqla.TIME)
    image = sqla.Column('image', sqla.VARCHAR(64))
    category = sqla.Column('category', sqla.Integer, sqla.ForeignKey('category.id'))
    owner = sqla.Column('owner', sqla.VARCHAR(64), sqla.ForeignKey('user.username'))

class Favorite_Event(Base):
    __tablename__ = 'favorite_event'
    user_username = sqla.Column('user_username', sqla.VARCHAR(64), sqla.ForeignKey("user.username"), primary_key=True)
    event_id = sqla.Column('event_id', sqla.Integer, sqla.ForeignKey("event.id"), primary_key=True)

class Persister():

    def getPassword(self, password):
        return self.session.query(User).filter(User.password == password).first()

    def getEmail(self,email):
        return self.session.query(User).filter(User.email == email).first()

    def persist_object(self, obj):
        self.session.add(obj)
        self.session.commit()

    def addFriend(self, username, friend):
        self.session.execute("INSERT INTO friend VALUES ('" + username + "', '" + friend + "'), ('" + friend + "', '" + username + "');")
        self.session.commit()

    def remove_object(self, obj):
        self.session.delete(obj)
        self.session.commit()

    def getFriends(self, name):
        return self.session.query(User, Friend)\
            .join(Friend, User.username == Friend.username1)\
            .filter(User.username == name) \
            .all()

    def getUser(self, name):
        return self.session.query(User).filter(User.username == name).first()

    def getUserByEmail(self, email):
        return self.session.query(User).filter(User.email == email).first()

    def getPassword(self,email):
        return self.session.query(User.password).filter(User.email == email).first()

    def getUsername(self,email):
        return self.session.query(User.username).filter(User.email == email).first()

    def getEmail(self,email):
        return self.session.query(User).filter(User.email == email).first()

    def getId(self,email):
        return self.session.query(User.id).filter(User.email == email).first()

    def getCategories(self):
        return self.session.query(Category).all()

    def removePreference(self, id, name):
        preference = self.session.query(Preference_User)\
            .filter(Preference_User.user_username==name)\
            .filter(Preference_User.category_id==int(id))\
            .first()
        self.session.delete(preference)
        self.session.commit()

    def updateUserInfo(self, form):
        user = self.session.query(User)\
            .filter(User.username == form.get('username'))\
            .first()

        user.firstName = form.get('firstName')
        user.lastName = form.get('lastName')
        user.country = form.get('country')
        user.email = form.get('email')
        password = form.get('password')
        if len(password) > 3:
            user.password = pbkdf2_sha256.hash(password)
        user.country = form.get('country')

        self.session.commit()

    def getEvent(self, id):
        event = self.session.query(Event) \
            .filter(Event.id == id) \
            .first()

        return event

    def updateEvent(self, request):
        form = request.form

        event = self.session.query(Event)\
            .filter(Event.id == form.get('eventId'))\
            .first()

        if event.owner == form.get('owner'):
            img = ""
            if request.files.get('image', None):
                file = request.files.get('image', None)
                img = str(time.time()).replace(".", "")
                img = img + "." + file.filename.partition(".")[-1]
                file.save(os.path.join('images\events', img))
            if form.get('name'):
                event.name = form.get('name')
            if form.get('category'):
                event.category = form.get('category')
            if form.get('description'):
                event.description = form.get('description')
            if form.get('location'):
                event.location = form.get('location')
            if form.get('start_date'):
                event.startDate = form.get('start_date')
            if form.get('start_time'):
                event.startTime = form.get('start_time')
            if form.get('end_date'):
                event.endDate = form.get('end_date')
            if form.get('end_time'):
                event.endTime = form.get('end_time')
            if img != "":
                event.image = img

        self.session.commit()


    def removeFavoritePlace(self, id, name):
        favorite = self.session.query(Preference_User) \
        .filter(Favorite_Place.user_username == name) \
        .filter(Favorite_Place.place_id == id) \
        .first()
        self.session.delete(favorite)
        self.session.commit()


    def removeFavoriteEvent(self, id, name):
        favorite = self.session.query(Preference_User) \
            .filter(Favorite_Event.user_username == name) \
            .filter(Favorite_Event.event_id == id) \
            .first()
        self.session.delete(favorite)
        self.session.commit()

    def __init__(self):
        Session = sessionmaker(bind=conn)
        self.session = Session()


Base.metadata.create_all(conn)

