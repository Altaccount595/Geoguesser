from flask import Flask, render_template, url_for, session, request, redirect, jsonify, flash
from db import getRandLoc
import db
import os, math
from api_handle import image
RADIUS = 6371.0

app = Flask(__name__)

app.secret_key = os.urandom(32)

db.create_db()

@app.route("/", methods = ['GET', 'POST'])
def home():
    if "username" not in session:
        return redirect(url_for("auth"))
    location = getRandLoc()
    image(location[0], location[1])
    session['location'] = {
        'lat' : location[0],
        'long' : location[1]
    }
    if request.method  == 'POST':
        score = check_guess()
        return render_template("home.html", username=session["username"], img = 'streetview_image.jpg')
    return render_template("home.html", username=session["username"], img = 'streetview_image.jpg')

def check_guess():
    lat = float(request.form.get('lat'))
    long = float(request.form.get('long'))
    guess =  [lat, long]
    print(lat)
    answer= [session['location']['lat'], session['location']['long']]
    check = (answer == guess)
    if check:
        score = 1
    else:
        score = 0
    return score

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

def toRadians(degree):
    return degree *(math.pi / 180.0)

def haversine(lat1, lon1, lat2, lon2):
    lat1 = toRadians(lat1)
    lon1 = toRadians(lon1)
    lat2 = toRadians(lat2)
    lon2 = toRadians(lon2)
    dLat = lat2 - lat1
    dLon = lon2 - lon1
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(lat1) * math.cos(lat2) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return RADIUS * c

if __name__ == "__main__":
    app.debug = True
    app.run()
