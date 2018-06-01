from werkzeug.security import generate_password_hash
from database import Persister, User

persister = Persister()

def registerSubmit(form):
    user = User(
        username = form.get('username'),
        email = form.get('email'),
        firstName = form.get('firstname'),
        lastName = form.get('lastname'),
        password = generate_password_hash(form.get('password'),method='sha256'),
        country = form.get('country')
    )
    persister.persist_object(user)
