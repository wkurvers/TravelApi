import os
from flask_login import LoginManager, current_user, login_required, logout_user
from database import User
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file, make_response, session
import userApi, eventApi, categoryApi, registerForm, loginForm
import sys, json
from pymongo import MongoClient


collection = MongoClient('localhost', 27017).travelbuddy.likes
app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(username):
    return userApi.getUser(username)


@app.route('/api/user/getEvents', methods=['GET'])
def getUserEvents():
    if current_user.is_authenticated:
        return userApi.getEvents(current_user.username)
    else:
        return jsonify([])


@app.route('/api/getEvents', methods=['GET'])
def getEvents():
    country = request.args.get('country', None)
    city = request.args.get('city', None)
    return eventApi.getEvents(city, country)


@app.route('/editEvent', methods=['GET'])
def editEvent():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect('/')


@app.route('/eventImage', methods=['GET'])
def getImage():
    img = request.args.get('img', None)
    return send_file('images/events/'+img, mimetype='image/gif')


@app.route('/api/countryName', methods=['GET'])
def getCountry():
    code = request.args.get('code', None)
    return categoryApi.getCountry(code)


@app.route('/api/countries', methods=['GET'])
def countries():
    return categoryApi.getCountries()


@app.route('/api/user/editEvent', methods=['PUT', 'GET'])
def updateEvent():
    if request.method == 'PUT':
        return eventApi.updateEvent(request)
    if request.method == 'GET':
        if request.args.get('id'):
            event = eventApi.getEvent(request.args.get('id'))
            return event
        else:
            return redirect('/profile')


# Submitting & deleting events
@app.route('/api/event', methods=['POST', 'DELETE'])
@login_required
def processEvent():
    if request.method == 'POST':
        return eventApi.postEvent(request)
    if request.method == 'DELETE':
        return eventApi.deleteEvent(request, current_user.username)


@app.route('/addEvent', methods=['GET'])
def addEvent():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect('/')


@app.route('/login', methods=['POST'])
def loginPageHandler():
     if current_user.is_authenticated:
         return render_template('index.html')
     else:
        return jsonify({'value': True}),loginForm.loginUser(request.args)


@app.route('/register', methods=['POST'])
def registerHandler():
    return registerForm.registerSubmit(request.args)


@app.route('/api/loginValue', methods=['GET'])
def loginValue():
    checking = current_user.is_authenticated
    if checking:
        return jsonify({"value": True})
    else:
        return jsonify({"value": False})

@app.route('/api/loginCheck', methods=['GET'])
def loginCheck():
    check = current_user.is_authenticated
    if check:
        print(current_user.username, file=sys.stderr)
        return jsonify({"username": current_user.username})
    else:
        return jsonify(False)


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect('/')
    else:
        return redirect('/login')



@app.route('/api/loginName', methods=['GET'])
def loginName():
    check = current_user.is_authenticated
    if check:
        # print(current_user.username, file=sys.stderr)
        return jsonify({
                "yourName": current_user.username,
                "yourEmail": current_user.email,
                "yourCountry": current_user.country
        })
    else:
        return jsonify({
            "yourName": 'not logged in',
            "yourEmail": 'blah@blah.com',
            "yourCountry": None
        })


@app.route('/friends')
def friends():
    return render_template('index.html')


@app.route('/api/user/friends',methods=['GET','POST'])
@login_required
def friendsMethods():
    username = current_user.username
    if request.method == 'GET':
        friendList = userApi.getFriends(username)
        return jsonify({"friends": friendList})
    if request.method == 'POST':
        friend = request.args.get('friend',None)
        status = userApi.addFriend(username, friend)
        return jsonify({"addfriend": status})

@app.route('/api/user/friends/<name>',methods=['DELETE'])
def deleteFriend(name):
    username = current_user.username
    if request.method == 'DELETE':
        print('jij wilt deleten', file=sys.stderr)
        status = userApi.deleteFriend(username, name)
        return jsonify({"deleteStatus": status})
        # return redirect('/')



@app.route('/api/likes', methods=['GET', 'DELETE', 'POST'])
def index():
    placeId = request.args.get('placeId', None)
    doc = collection.find_one(
        {'place_event_id': placeId}
    )
    if request.method == 'GET':
        if doc:
            return jsonify({'likes': doc['likes']})
        else:
            # collection.insert_one(
            #     {'likes': 0, 'users': []}
            # )
            return jsonify({'likes': 0})

    if request.method == 'POST':
        if current_user.is_authenticated:
            # userId = request.args.get('userId', None)
            userId = current_user.username
            if doc:
                if userId in doc['users']:
                    return jsonify({'likes': "Error"})
                doc['likes'] = doc['likes']+1
                doc['users'].append(userId)
                collection.update_one({'place_event_id': placeId}, {'$set': doc})
                return jsonify({'likes': doc['likes']})
            else:
                likes = {
                    'place_event_id': placeId,
                    'likes': 1,
                    'users': [userId]
                }
                collection.insert_one(likes)
                return jsonify({'likes': 1})
        else:
            return jsonify(False)

    if request.method == 'DELETE':
        if current_user.is_authenticated:
            # userId = current_user.username
            userId = request.args.get('userId', None)

            if doc:
                if userId in doc['users']:
                    doc['users'].remove(userId)
                    doc['likes'] = doc['likes']-1
                    collection.update_one({'place_event_id': placeId}, {'$set': doc})
                    return jsonify({'likes': doc['likes']})
                else:
                    return jsonify({'likes': "Error"})
            else:
                return "Not found!"
        else:
            return jsonify(False)


@app.route('/api/user/checkLiked')
def check():
    if current_user.is_authenticated:
        userId = current_user.username
        placeId = request.args.get('placeId', None)
        # userId = request.args.get('userId', None)

        if placeId and userId:
            doc = collection.find_one(
                {'place_event_id': placeId}
            )
            if not doc:
                doc = {
                    'place_event_id': placeId,
                    'likes': 0,
                    'users': []
                }
                collection.insert_one(doc)
                return jsonify({"check": False})
            if userId in doc['users']:
                return jsonify({"check": True})
            return jsonify({"check": False})
        else:
            return "Error"
    else:
        return jsonify(False)


@app.route('/api/user/checkFavorite', methods=['GET'])
def checkFavorite():
    if current_user.is_authenticated:
        user = current_user.username
        # user = request.args.get('username', None)
        id = request.args.get('id', None)
        result = userApi.checkFavorite(user, id)
        if result:
            return str(result), 409
        return str(result), 200
    else:
        return jsonify(False)


@app.route('/api/user/favorite', methods=['POST', 'DELETE', 'GET'])
def favoriteEvent():
    if request.method == 'POST':
        if current_user.is_authenticated:
            user = current_user.username
            #user = request.args.get('username', None)
            type = request.args.get('type', None)
            if type == "event":
                place_id = None
                event_id = request.args.get('eventId', None)
            elif type == "place":
                place_id = request.args.get('placeId', None)
                event_id = None
            else:
                place_id = None
                event_id = None
            return userApi.addFavorite(user, place_id, event_id, type)
        else:
            return jsonify(False)

    if request.method == 'DELETE':
        if current_user.is_authenticated:
            username = current_user.username
            id = request.args.get('id', None)
            return userApi.deleteFavorite(id, username)
        else:
            return jsonify(False)

    if request.method == 'GET':
        # user = request.args.get('username', None)
        if current_user.is_authenticated:
            user = current_user.username
            return json.dumps(userApi.getFavorites(user), indent=4, default=str)
        else:
            return jsonify(False)


# Get all user details
@app.route('/api/user', methods=['GET', 'PUT'])
@login_required
def user():
    name = current_user.username
    if request.method == 'GET':
        user = userApi.getUserInfo(name)
        return user

    if request.method == 'PUT':
        return userApi.updateUserInfo(request.args)


# Get all preferences of user
@app.route('/api/user/preferences', methods=['GET'])
def getPreferences():
    if current_user.is_authenticated:
        name = current_user.username
        return userApi.getUserPreferences(name)
    else:
        return jsonify(False)

# Get all users
@app.route('/api/userList/', methods=['GET'])
def getAllUsers():
    return userApi.getAllUsers()

# Submit and remove preference of user
@app.route('/api/user/preferences', methods=['POST', 'DELETE'])
def preferences():
    if current_user.is_authenticated:
        name = current_user.username
        id = request.args.get('id', None)
        if request.method == 'POST':
            return userApi.addPreference(name, id)
        if request.method == 'DELETE':
            return userApi.deletePreference(name, id)
    else:
        return jsonify(False)


# Get all categories available
@app.route('/api/categories', methods=['GET'])
def getCategories():
    return categoryApi.getAllCategories()


@app.route('/profile')
@login_required
def profile():
    return render_template('index.html')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def route(path):
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
