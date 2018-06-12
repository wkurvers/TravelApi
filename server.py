import os
from flask_login import LoginManager, current_user, login_required
from database import User
from flask import Flask, render_template, request, redirect, url_for, jsonify
import userApi, eventApi, categoryApi, registerForm, loginForm
import sys


app = Flask(__name__)
app.secret_key = os.urandom(24)
login = LoginManager(app)
login.init_app(app)


@login.user_loader
def load_user(user_name):
    return userApi.getUser(user_name)

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
                return redirect(url_for('profile'))
             else:
                 print('faal', file=sys.stderr)
                 return render_template('index.html')
    else:
        return "false request"


@app.route('/api/loginCheck', methods=['GET'])
def loginCheck():
    check = current_user.is_authenticated
    if check:
        print(current_user.username, file=sys.stderr)
        return jsonify({"username": current_user.username})
    else:
        return str(None)


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


@app.route('/api/user/favoriteEvent', methods=['POST', 'DELETE'])
def favoriteEvent(name, id):
    if request.method == 'POST':
        return userApi.addFavoriteEvent(name, id)
    if request.method == 'DELETE':
        return userApi.deleteFavoriteEvent(name, id)


@app.route('/api/user/favoritePlace', methods=['POST', 'DELETE'])
def favoritePlace(name, id):
    if request.method == 'POST':
        return userApi.addFavoritePlace(name, id)
    if request.method == 'DELETE':
        return userApi.deleteFavoritePlace(name, id)


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


# Submit event
@app.route('/api/event', methods=['POST'])
def event():
    eventApi.postEvent(request)
    return redirect('/addEvent')

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
