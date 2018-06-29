import sys

from flask import jsonify
from database import Persister, Preference_User, Favorite, Friend

persister = Persister()


def getUser(username):
    return persister.getUser(username)


def getUserInfo(name):
    data = persister.getUser(name)
    result = {
        'username': data.username,
        'email': data.email,
        'firstName': data.firstName,
        'lastName': data.lastName,
        'country': data.country,
    }
    return jsonify(result), 200


def getFriends(name):
    friends = persister.getFriends(name)
    result = []
    for user in friends:
        user = persister.getUser(user.Friend.username2)
        result.append([user.firstName, user.lastName, user.country])
    return result


def addFriend(username, friend):
    status = persister.addFriend(username, friend)
    return status


def updateUserInfo(form):
    persister.updateUserInfo(form)


def getUserPreferences(name):
    data = persister.getUser(name)
    res = {}
    for preference in data.preference:
        res.update({preference.name: preference.id})
    return jsonify(res)

def getAllUsers():
    users = persister.getAllUsers()
    return jsonify({"users": users})

def deletePreference(name, id):
    persister.removePreference(id, name)
    return "success"


def addPreference(name, id):
    preference = Preference_User(user_username=name, category_id=id)
    persister.persist_object(preference)
    return "success"


def addFavorite(name, place_id, event_id, type):
    if type == "event":
        favorite = Favorite(user_username=name, event_id=event_id, place_id=None, type="event")
    elif type == "place":
        favorite = Favorite(user_username=name, event_id=None, place_id=place_id, type="place")
    persister.persist_object(favorite)
    return "success"


def deleteFavorite(id, username):
    persister.removeFavorite(id, username)
    return "success"


def getFavorites(user):
    favorites = persister.getFavorites(user)
    result = []
    for favorite in favorites:
        location = ""
        if favorite.address:
            if favorite.city:
                location += favorite.address + ", "
            else:
                location += favorite.address
        if favorite.city:
            if favorite.country:
                location += favorite.city + ", "
            else:
                location += favorite.city
        if favorite.country:
            location += favorite.country

        result.append({
            "id": favorite.id,
            "type": favorite.type,
            "placeId": favorite.place_id,
            "eventId": favorite.event_id,
            "eventName": favorite.name,
            "eventDesc": favorite.description,
            "eventImg": favorite.image,
            "eventStartDate": favorite.startDate,
            "eventStartTime": favorite.startTime,
            "eventEndDate": favorite.endDate,
            "eventEndTime": favorite.endTime,
            "image": favorite.image,
            "address": favorite.address,
            "city": favorite.city,
            "location": location,
            "country": favorite.country,
            "eventLat": favorite.lat,
            "eventLng": favorite.lng
        })
    return result


def checkFavorite(user, id):
    return persister.checkFavorite(user, id)


def deleteFavoritePlace(name, id):
    persister.removeFavoritePlace(id, name)
    return "success"

def deleteFriend(username, friend):
    status = persister.removeFriend(username,friend)
    return status


def getEvents(name):
    result = []
    events = persister.getUserEvents(name)
    for event in events:
        result.append({
            "id": event.id,
            "name": event.name
        })
    return jsonify(result)

