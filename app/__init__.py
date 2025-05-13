from flask import Flask, render_template, url_for, session, request, redirect, jsonify, flash
from db import getRandLoc
import db
import os
from api_handle import image

app = Flask(__name__)

app.secret_key = os.urandom(32)

db.create_db()

@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("auth"))
    location = getRandLoc()
    image(location[0], location[1])
    return render_template("home.html", username=session["username"], img = 'streetview_image.jpg')

@app.route('/auth', methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if "login" in request.form:
            if db.check_user(username, password):
                session["username"] = username
                return redirect(url_for("home"))
            flash("Invalid username or password!")
        elif "register" in request.form:
            if db.add_user(username, password):
                session["username"] = username
                return redirect(url_for("home"))
            flash("Username already taken!")

    return render_template("auth.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth'))

@app.route("/leaderboard")
def leaderboard():
    scores = db.top_scores()       
    return render_template("leaderboard.html", scores=scores)

if __name__ == "__main__":
    app.debug = True
    app.run()
