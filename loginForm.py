import sys

from flask import flash
from passlib.hash import pbkdf2_sha256
from database import Persister, User

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
        return True
    else: return False



