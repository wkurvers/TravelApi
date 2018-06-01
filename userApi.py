from flask import jsonify
from database import Persister, Preference_User, Favorite_Event, Favorite_Place

persister = Persister()


def getUserInfo(name):
    data = persister.getUser(name)
    #   if(data.username == None) or (data.email == None) or (data.email == None) or (data.firstName == None) or (data.lastName == None) or (data.country == None):
    #     return False
    result = {
        'username': data.username,
        'email': data.email,
        'firstName': data.firstName,
        'lastName': data.lastName,
        'country': data.country,
    }
    return jsonify(result), 200


def updateUserInfo(form):
    persister.updateUserInfo(form)


def getUserPreferences(name):
    data = persister.getUser(name)
    res = {}
    for preference in data.preference:
        res.update({preference.name: preference.id})
    return jsonify(res)


def deletePreference(name, id):
    persister.removePreference(id, name)
    return "success"


def addPreference(name, id):
    preference = Preference_User(user_username=name, category_id=id)
    persister.persist_object(preference)
    return "success"


def addFavoriteEvent(name, id):
    favorite = Favorite_Event(user_username=name, event_id=id)
    persister.persist_object(favorite)
    return "sucess"


def deleteFavoriteEvent(name, id):
    persister.removeFavoriteEvent(id, name)
    return "success"


def addFavoritePlace(name, id):
    favorite = Favorite_Place(user_username=name, place_id=id)
    persister.persist_object(favorite)
    return "sucess"


def deleteFavoritePlace(name, id):
    persister.removeFavoritePlace(id, name)
    return "success"