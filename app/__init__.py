from flask import Flask, render_template, url_for, session, request, redirect, jsonify
import os

app = Flask(__name__)

app.secret_key = os.urandom(32)

@app.route("/")
def home():
    return render_template('home.html')


@app.route('/auth', methods=["GET", "POST"])
def auth():
    return render_template('auth.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.debug = True
    app.run()
