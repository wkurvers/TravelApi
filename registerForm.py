from database import Persister, User
from passlib.hash import pbkdf2_sha256
from flask import jsonify
import checks

persister = Persister()

def registerSubmit(form):
    # check if username en email there

    firstName = form.get('firstName', None)
    lastName = form.get('lastName', None)
    country = form.get('country', None)
    email = form.get('email', None)
    username = form.get('username', None)
    password = form.get('password', None)

    username = username.replace(" ", "")
    email = email.replace(" ", "")
    firstName = firstName.strip()
    lastName = lastName.strip()

    if checks.checkSpecialChars([username]):
        return jsonify({
            "message": "Please use no special characters in your username!"
        }), 400, {'ContentType': 'application/json'}

    if checks.checkSpecialCharsEmail(email):
        return jsonify({
            "message": "Please use no special characters in your email!"
        }), 400, {'ContentType': 'application/json'}

    if checks.emptyCheck([firstName, lastName, email, country, username, password]):
        return jsonify({
            "message": "Please fill in all fields."
        }), 400, {'ContentType': 'application/json'}

    if checks.lengthSixtyFourCheck([firstName, lastName, country, email, username]):
        return jsonify({
            "message": "Please don't fill in more than 64 characters."
        }), 400, {'ContentType': 'application/json'}

    password = form.get('password', None)
    check = checks.passwordLengthCheck(password)
    if check == [False, "short"]:
        return jsonify({
            "message": "Please make your password 5 characters or longer."
        }), 400, {'ContentType': 'application/json'}
    if check == [False, "long"]:
        return jsonify({
            "message": "Please keep your password shorter than 64 characters."
        }), 400, {'ContentType': 'application/json'}

    if persister.checkUserExistance(username, email):
        return jsonify({
            "message": "Username or email already exists."
        }), 400, {'ContentType': 'application/json'}

    user = User(
        username=username,
        email=email,
        firstName=firstName,
        lastName=lastName,
        password=pbkdf2_sha256.hash(password),
        country=country
    )

    persister.persist_object(user)
    persister.addFriend(username, "Never Travel Alone")

    return jsonify({
        "message": "Welcome to TravelBuddy! You are now a member."
    }), 200, {'ContentType': 'application/json'}
