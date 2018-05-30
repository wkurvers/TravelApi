from flask import jsonify
from database import Persister

persister = Persister()


def getUserInfo(name):
    data = persister.getUser(name)
    result = {
        'username': data.username,
        'email': data.email,
        'firstName': data.firstName,
        'lastName': data.lastName,
        'country': data.country,
        'passwordLen': len(data.password)
    }
    return jsonify(result), 200


def getUserPreferences(name):
    data = persister.getUser(name)
    return jsonify(data)
