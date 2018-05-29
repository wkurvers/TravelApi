from flask import Flask
from flask import render_template
import sys
import login as login

app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def route(path):
    # Hier kun je een login check doen. Het url pad wordt meegegeven in path #
    if path == 'profile':
        if not login.check_login():
            print("Not logged in!", file=sys.stderr)
            return "Not logged in!"

    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='localhost', debug=True)
