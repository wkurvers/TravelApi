from database import Persister, User
from passlib.hash import pbkdf2_sha256

persister = Persister()

def registerSubmit(form):

    user = User(
        username = form.get('username'),
        email = form.get('email'),
        firstName = form.get('firstname'),
        lastName = form.get('lastname'),
        password = pbkdf2_sha256.hash(form.get('password')),
        country = form.get('country')
    )

    persister.persist_object(user)
