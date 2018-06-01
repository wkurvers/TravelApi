from database import Persister
from flask import jsonify


persister = Persister()


def getAllCategories():
    result = persister.getCategories()
    res = {}
    for category in result:
        res.update({category.name: category.id})
    return jsonify(res)
