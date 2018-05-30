from flask import Flask, jsonify, render_template, request
import sys
import login as login
import userApi, eventApi, categoryApi

app = Flask(__name__)


@app.route('/api/user/<name>', methods=['GET'])
def getUser(name):
    return userApi.getUserInfo(name)


@app.route('/api/user/preferences/<name>', methods=['GET'])
def getPreferences(name):
    return userApi.getUserPreferences("wouter")


@app.route('/api/categories', methods=['GET'])
def getCategories():
    res = []
    result = categoryApi.getAllCategories()
    for x in result:
        res.append(x.name)
    return jsonify(res)


@app.route('/event', methods=['POST', 'GET'])
def event():
    if request.method == 'POST':
        return eventApi.postEvent(request.form)
    else:
        return "false request"


@app.route('/profile')
def profile():
    if not login.check_login():
        print("Not logged in!", file=sys.stderr)
        return "Not logged in!"


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def route(path):
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='localhost', debug=True)
