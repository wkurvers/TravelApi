from flask import Flask, jsonify, render_template, request, redirect, url_for
import sys
import userApi, eventApi, categoryApi, registerForm, login

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/login', methods=['POST'])
def loginPageHandler():
    if request.method == 'POST':
        if request.form['submit'] == 'register':
             registerForm.registerSubmit(request.form)
             return render_template('index.html')
        elif request.form['submit'] == 'login':
             check = login.loginUser(request.form)
             if check:
                return redirect(url_for('profile'))
             else:
                 return render_template('index.html')
    else:
        return "false request"

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
    return render_template('index.html')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def route(path):
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='localhost', debug=True)
