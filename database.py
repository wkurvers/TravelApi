
import sys
import sqlalchemy as sqla
from flask import jsonify
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import exists, or_
from passlib.hash import pbkdf2_sha256
import time, os
from hashlib import md5
import checks


conn = sqla.create_engine('mysql+pymysql://root:@127.0.0.1/project?host=127.0.0.1?port=3306')
#conn = sqla.create_engine('mysql+mysqlconnector://root:mysqlSet33@127.0.0.1/project?host=127.0.0.1?port=3306', pool_recycle=3600)
#conn = sqla.create_engine('mysql+mysqlconnector://root:mysqlSet33@127.0.0.1/project?host=127.0.0.1?port=3306')

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
    favorite = relationship('Favorite')
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

class Favorite(Base):
    __tablename__ = 'favorite'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True)
    user_username = sqla.Column('user_username', sqla.VARCHAR(64), sqla.ForeignKey("user.username"))
    place_id = sqla.Column('place_id', sqla.VARCHAR(64))
    event_id = sqla.Column('event_id', sqla.Integer, sqla.ForeignKey('event.id'), sqla.ForeignKey("event.id"))
    type = sqla.Column('type', sqla.VARCHAR(10))

class Event(Base):
    __tablename__ = 'event'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True)
    name = sqla.Column('name', sqla.VARCHAR(128))
    description = sqla.Column('description', sqla.TEXT)
    address = sqla.Column('address', sqla.VARCHAR(64))
    city = sqla.Column('city', sqla.VARCHAR(64))
    country = sqla.Column('country', sqla.VARCHAR(64))
    startDate = sqla.Column('start_date', sqla.DATE)
    startTime = sqla.Column('start_time', sqla.TIME)
    endDate = sqla.Column('end_date', sqla.DATE)
    endTime = sqla.Column('end_time', sqla.TIME)
    image = sqla.Column('image', sqla.VARCHAR(64))
    lat = sqla.Column('lat', sqla.DECIMAL(10, 8))
    lng = sqla.Column('lng', sqla.DECIMAL(10, 8))
    owner = sqla.Column('owner', sqla.VARCHAR(64), sqla.ForeignKey('user.username'))

class Country(Base):
    __tablename__ = 'country'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True)
    code = sqla.Column('code', sqla.VARCHAR(4), unique=True)
    name = sqla.Column('name', sqla.VARCHAR(64), unique=True)

class Persister():

    def getCityEvents(self, city, country):
        db = Session()
        events = db.query(Event).filter(Event.city == city).limit(10).all()
        if len(events) < 2:
            events = db.query(Event).filter(Event.country == country).limit(10).all()
            if len(events) < 2:
                db.close()
                return None
            db.close()
            return [country, events]
        else:
            db.close()
            return [city, events]

    def getCountries(self):
        db = Session()
        countries = db.query(Country).all()
        db.close()
        return countries

    def getCountry(self, code):
        db = Session()
        country = db.query(Country.name).filter(Country.code == code).first()
        db.close()
        return country

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
        try:
         db.execute("INSERT INTO friend VALUES ('" + username + "', '" + friend + "'), ('" + friend + "', '" + username + "');")
         db.commit()
         return True
        except:
         db.close()
         return False

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
            db.close()
            return False

    def updateUserInfo(self, firstName, lastName, country, username, password):
        db = Session()
        user = db.query(User)\
            .filter(User.username == username)\
            .first()

        user.firstName = firstName
        user.lastName = lastName
        user.country = country

        if password:
            user.password = pbkdf2_sha256.hash(password)

        db.commit()
        db.close()
        return jsonify({
            "message": "Updated!"
        }), 200, {'ContentType': 'application/json'}

    def getEvent(self, id):
        db = Session()
        event = db.query(Event) \
            .filter(Event.id == id) \
            .first()
        db.close()
        return event

    def updateEvent(self, request):
        db = Session()
        form = request.args

        event = db.query(Event)\
            .filter(Event.id == form.get('eventId'))\
            .first()

        if event.owner == form.get('owner'):

            location = form.get('location').strip()
            name = form.get('name').strip()
            description = form.get('description').strip()
            startDate = form.get('startDate')
            startTime = form.get('startTime')
            endDate = form.get('endDate')
            endTime = form.get('endTime')
            owner = form.get('owner')
            lng = form.get('lng')
            lat = form.get('lat')

            if checks.emptyCheck([location, name, description, startDate, startTime, endDate, endTime, owner, lng, lat]):
                return jsonify({
                    "message": "Please, fill in all fields."
                }), 400, {'ContentType': 'application/json'}

            if checks.lengthSixtyFourCheck([name]):
                return jsonify({
                    "message": "Please don't fill in more than 64 characters."
                }), 400, {'ContentType': 'application/json'}

            if checks.dateTimeCheck(startDate, startTime, endDate, endTime):
                return jsonify({
                    "message": "A problem occurred with regards to the dates and times of this event.<br>"
                               "Rules:<br>"
                               "- Events that start later than 1 year from now are not allowed.<br>"
                               "- The event's start date/time can't be later than the end date/time.<br>"
                               "- You can't enter dates earlier than today.<br>"
                               "- An event's length can't be longer than a year."
                }), 400, {'ContentType': 'application/json'}

            if request.files.get('image'):
                file = request.files.get('image', None)
                img = str(time.time()).replace(".", "")
                ext = file.filename.partition(".")[-1]
                if not checks.imgExtensionCheck(ext):
                    return jsonify({
                        "message": "Only .png, .jpg or .jpeg  images are valid!"
                    }), 400, {'ContentType': 'application/json'}
                img = img + "." + ext
                file.save(os.path.join('images\events', img))
            else:
                img = None

            temp = location.split(', ')
            country = None
            city = None
            address = None
            if len(temp) > 0:
                country = temp.pop()
            if len(temp) > 0:
                city = temp.pop()
            if len(temp) > 0:
                address = ', '.join(temp)

            event.name = name
            event.description = description
            event.address = address
            event.city = city
            event.country = country
            event.startDate = form.get('startDate')
            event.startTime = form.get('startTime')
            event.endDate = form.get('endDate')
            event.endTime = form.get('endTime')
            event.lat = form.get('lat')
            event.lng = form.get('lng')
            if img:
                event.image = img

        db.commit()
        db.close()

        return jsonify({
            "message": "Event updated!"
        }), 200, {'ContentType': 'application/json'}

    def deleteEvent(self, eventId, username):
        db = Session()

        event = db.query(Event).filter(Event.id == eventId)\
            .filter(Event.owner == username)

        if not event:
            return jsonify({
                "message": "Either the event does not exist, or you are not the owner!"
            }), 400, {'ContentType': 'application/json'}

        event.delete()
        db.commit()
        db.close()

        return jsonify({
            "message": "Successfully deleted!"
        }), 200, {'ContentType': 'application/json'}

    def removeFavorite(self, id, username):
        db = Session()

        db.query(Favorite) \
            .filter(Favorite.user_username == username) \
            .filter(or_(Favorite.event_id == id, Favorite.place_id == id)) \
            .delete()
        db.commit()
        db.close()

    def getFavorites(self, user):
        db = Session()
        favorites = db\
            .query(
                Favorite.id, Favorite.type, Favorite.event_id, Favorite.place_id,
                Event.name, Event.image, Event.description, Event.startDate,
                Event.startTime, Event.endDate, Event.endTime, Event.address,
                Event.city, Event.country, Event.lat, Event.lng
            )\
            .outerjoin(Event, Event.id == Favorite.event_id) \
            .filter(Favorite.user_username == user) \
            .all()
        db.close()
        return favorites

    def checkFavorite(self, username, id):
        db = Session()
        favorite = db.query(Favorite)\
            .filter(Favorite.user_username == username)\
            .filter(or_(Favorite.place_id == id, Favorite.event_id == id))\
            .first()
        db.close()
        if favorite:
            return True
        return False

    def getUserEvents(self, username):
        db = Session()
        events = db.query(Event)\
            .filter(Event.owner == username)\
            .all()
        db.close()
        return events

    def checkUserExistance(self, username, email):
        db = Session()
        if db.query(User).filter(User.email == email).count():
            db.close()
            return True
        if db.query(User).filter(User.username == username).count():
            db.close()
            return True
        db.close()
        return False


    # def __init__(self):
    #     print("test")
        #Session = scoped_session(sessionmaker(bind=conn))
        #Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=conn))
        #self.session = Session()

Base.metadata.create_all(conn)

