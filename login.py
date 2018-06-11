import sys
from flask import session
from werkzeug.security import check_password_hash

from database import Persister

persister = Persister()

def loginUser(form):
    emailLogin = form.get('email')
    password_candidate = form.get('password')
    dbEmail = persister.getEmail(emailLogin)
    p = persister.getPassword(password_candidate)
    if p == None or dbEmail == None:
        print('login failed', file=sys.stderr)
        return False
    elif p.password == password_candidate and dbEmail.email == emailLogin:
        print('logged in', file=sys.stderr)
        session['email'] = emailLogin
        return True
