import os
from flask_login import LoginManager, current_user, login_required, logout_user
from database import User
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
import userApi, eventApi, categoryApi, registerForm, loginForm
import sys, json
from pymongo import MongoClient


collection = MongoClient('localhost', 27017).travelbuddy.likes
app = Flask(__name__)
app.secret_key = os.urandom(24)
login = LoginManager(app)
login.init_app(app)


@login.user_loader
def load_user(user_name):
    return userApi.getUser(user_name)


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


@app.route('/api/user/editEvent', methods=['POST', 'GET'])
def updateEvent():
    if request.method == 'POST':
        eventApi.updateEvent(request)
        return redirect('/profile')
    if request.method == 'GET':
        if request.args.get('id'):
            event = eventApi.getEvent(request.args.get('id'))
            return event
        else:
            return redirect('/profile')

# Submit event
@app.route('/api/event', methods=['POST'])
def postEvent():
    eventApi.postEvent(request)
    return redirect('/addEvent')


@app.route('/addEvent', methods=['GET'])
def addEvent():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect('/')


@app.route('/login', methods=['POST'])
def loginPageHandler():

    if request.method == 'POST':
        if request.form['submit'] == 'register':
            registerForm.registerSubmit(request.form)
            return render_template('index.html')
        elif request.form['submit'] == 'login':
             if current_user.is_authenticated:
                 return render_template('index.html')
             if loginForm.loginCheck(request.form):
                flash("Ingelogd!")
                return redirect(url_for('profile'))
             else:
                 print('faal', file=sys.stderr)
                 return render_template('index.html')
    else:
        return "false request"


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
        return str(None)


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


@app.route('/api/loginEmail', methods=['GET'])
def loginEmail():
    check = current_user.is_authenticated
    if check:
        return jsonify({"yourEmail": current_user.email})
    else:
        return jsonify({"yourEmail": 'blah@blah.com'})


@app.route('/api/user/friends', methods=['GET', 'POST'])
def friends():
    username = request.args.get('name')
    if request.method == 'GET':
        friendList = userApi.getFriends(username)
        return jsonify({"friends": friendList})
    if request.method == 'POST':
        friend = request.args.get('friend')
        userApi.addFriend(username, friend)
        return redirect('/profile')


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
        userId = request.args.get('userId', None)
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

    if request.method == 'DELETE':
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


@app.route('/api/user/checkLiked')
def check():
    placeId = request.args.get('placeId', None)
    userId = request.args.get('userId', None)

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


@app.route('/api/user/checkFavorite', methods=['GET'])
def checkFavorite():
    user = request.args.get('username', None)
    id = request.args.get('id', None)
    result = userApi.checkFavorite(user, id)
    if result:
        return str(result), 409
    return str(result), 200


@app.route('/api/user/favorite', methods=['POST', 'DELETE', 'GET'])
def favoriteEvent():
    if request.method == 'POST':
        user = request.args.get('username', None)
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

    if request.method == 'DELETE':
        username = request.args.get('username', None)
        id = request.args.get('id', None)
        return userApi.deleteFavorite(id, username)

    if request.method == 'GET':
        user = request.args.get('username', None)
        return json.dumps(userApi.getFavorites(user), indent=4, default=str)


# Get all user details
@app.route('/api/user/<name>', methods=['GET', 'POST'])
def user(name):
    if request.method == 'GET':
        user = userApi.getUserInfo(name)
        return user

    if request.method == 'POST':
        userApi.updateUserInfo(request.form)
        return redirect('/profile')


# Get all preferences of user
@app.route('/api/user/preferences/<name>', methods=['GET'])
def getPreferences(name):
    return userApi.getUserPreferences(name)


# Submit and remove preference of user
@app.route('/api/user/preferences/<name>/<id>', methods=['POST', 'DELETE'])
def preferences(name, id):
    if request.method == 'POST':
        return userApi.addPreference(name, id)
    if request.method == 'DELETE':
        return userApi.deletePreference(name, id)


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
    app.run(host='localhost', debug=True)
