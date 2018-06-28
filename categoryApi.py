from database import Persister
from flask import jsonify


persister = Persister()


def getAllCategories():
    result = persister.getCategories()
    res = {}
    for category in result:
        res.update({category.name: category.id})
    return jsonify(res)


def getCountry(code):
    country = persister.getCountry(code)
    return jsonify({"name": country})


def getCountries():
    countries = persister.getCountries()
    result = []
    for country in countries:
        result.append({"id": country.id, "code": country.code, "name": country.name})
    return jsonify(result)
