from flask import Flask, render_template, request, redirect
import userApi, eventApi, categoryApi
import time

app = Flask(__name__)


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
        #userApi.updateUserInfo(request.form)
        return redirect('/addEvent')


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
@app.route('/event', methods=['POST'])
def event():
    return eventApi.postEvent(request.form)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def route(path):
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='localhost', debug=True)
