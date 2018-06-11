import sys
from flask_login import login_user
from passlib.hash import pbkdf2_sha256
from database import Persister

persister = Persister()


def loginCheck(form):
    emailLogin = form.get('email')
    password_candidate = form.get('password')
    dbEmail = persister.getEmail(emailLogin)
    hashed = persister.getPassword(emailLogin)
    if hashed == None or dbEmail == None:
        print('login failed', file=sys.stderr)
        return False
    if pbkdf2_sha256.verify(password_candidate,hashed[0]):
        print('logged in', file=sys.stderr)
        user = persister.getUserByEmail(emailLogin)
        login_user(user)
        return True
    else: return False



