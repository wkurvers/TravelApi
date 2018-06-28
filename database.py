
import sys
import sqlalchemy as sqla
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, scoped_session
from passlib.hash import pbkdf2_sha256
import time, os
from hashlib import md5



conn = sqla.create_engine('mysql+pymysql://root:@127.0.0.1/project?host=127.0.0.1?port=3306')


Session = scoped_session(sessionmaker(bind=conn))

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

    preference = relationship('Category', secondary="preference_user", backref='preference', lazy='subquery')
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
        db = Session()
        user = db.query(User).filter(User.password == password).first()
        db.close()
        return user

    def getEmail(self,email):
        db = Session()
        user = db.query(User).filter(User.email == email).first()
        db.close()
        return user

    def persist_object(self, obj):
        db = Session()
        db.add(obj)
        db.commit()
        db.close()

    def addFriend(self, username, friend):
        db = Session()
        db.execute("INSERT INTO friend VALUES ('" + username + "', '" + friend + "'), ('" + friend + "', '" + username + "');")
        db.commit()
        db.close()

    def remove_object(self, obj):
        db = Session()
        db.delete(obj)
        db.commit()
        db.close()

    def getFriends(self, name):
        db = Session()
        friends = db.query(User, Friend)\
            .join(Friend, User.username == Friend.username1)\
            .filter(User.username == name) \
            .all()
        db.close()
        return friends

    def getUser(self, name):
        db = Session()
        try:
            user = db.query(User).filter(User.username == name).first()
            db.close()
            return user
        except:
            db.rollback()
            db.close()

    def getAllUsers(self):
        db = Session()
        users = db.query(User.username).all()
        db.close()
        return users

    def getUserByEmail(self, email):
        db = Session()
        user = db.query(User).filter(User.email == email).first()
        db.close()
        return user

    def getPassword(self,email):
        db = Session()
        user = db.query(User.password).filter(User.email == email).first()
        db.close()
        return user

    def getUsername(self,email):
        db = Session()
        user = db.query(User.username).filter(User.email == email).first()
        db.close()
        return user

    def getEmail(self,email):
        db = Session()
        user = db.query(User).filter(User.email == email).first()
        db.close()
        return user

    def getId(self,email):
        db = Session()
        user = db.query(User.id).filter(User.email == email).first()
        db.close()
        return user

    def getCategories(self):
        db = Session()
        categories = db.query(Category).all()
        db.close()
        return categories

    def removePreference(self, id, name):
        db = Session()
        preference = db.query(Preference_User)\
            .filter(Preference_User.user_username==name)\
            .filter(Preference_User.category_id==int(id))\
            .first()
        db.delete(preference)
        db.commit()
        db.close()

    def removeFriend(self,username,friend):
        db = Session()
        try:
            myFriend = db.query(Friend) \
                .filter(Friend.username1==username) \
                .filter(Friend.username2==friend) \
                .first()
            db.delete(myFriend)

            hisFriend = db.query(Friend) \
                .filter(Friend.username1==friend) \
                .filter(Friend.username2==username) \
                .first()
            db.delete(hisFriend)
            db.commit()
            return True
        except:
            return False
        db.close()

    def updateUserInfo(self, form):
        db = Session()
        user = db.query(User)\
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

        db.commit()
        db.close()

    def getEvent(self, id):
        db = Session()
        event = db.query(Event) \
            .filter(Event.id == id) \
            .first()
        db.close()
        return event

    def updateEvent(self, request):
        db = Session()
        form = request.form

        event = db.query(Event)\
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

        db.commit()
        db.close()


    def removeFavoritePlace(self, id, name):
        db = Session()
        favorite = db.query(Preference_User) \
        .filter(Favorite_Place.user_username == name) \
        .filter(Favorite_Place.place_id == id) \
        .first()
        db.delete(favorite)
        db.commit()
        db.close()


    def removeFavoriteEvent(self, id, name):
        db = Session()
        favorite = db.query(Preference_User) \
            .filter(Favorite_Event.user_username == name) \
            .filter(Favorite_Event.event_id == id) \
            .first()
        db.delete(favorite)
        db.commit()
        db.close()

    def __init__(self):
        print("test")
        #Session = scoped_session(sessionmaker(bind=conn))
        #Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=conn))
        #self.session = Session()


Base.metadata.create_all(conn)

