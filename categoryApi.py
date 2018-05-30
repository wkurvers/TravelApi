from database import Persister


persister = Persister()


def getAllCategories():
    result = persister.getCategories()
    return result
