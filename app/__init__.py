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
    guessed = False
    session.modified=True
    if ('location' in session):
        print(session['location']['new'])
    if ('location' not in session) or (session['location']['new']):
        print(2025)
        location = getRandLoc()
        info = image(location[0], location[1])
        session['location'] = {
            'lat' : info[0],
            'long' : info[1],
            'heading' : info[2],
            'fov' : info[3],
            'new' : True
        }
        session.modified = True
    if request.method  == 'POST':
        if 'input' in request.form:
            dist = check_guess()
            points = round(POINT_CAP * math.exp(-10 * (dist / MAX_DISTANCE)))

            if 'history' not in session:          
                session['history'] = []
            session['history'].append((round(dist, 2), points))
            session.modified = True
            
            guessed = True
            session['location']['new'] = True
            return render_template("home.html", username=session["username"], img = 'streetview_image.jpg', guessed = guessed, dist=round(dist, 2), points=points, history=session['history'])
        elif 'left' in request.form:
            location = session['location']
            location['heading'] = (location['heading'] + 270) % 360
            location['new'] = False
            session['location'] =  location
            image(session['location']['lat'], session['location']['long'], session['location']['heading'])
        elif 'right' in request.form:
            session['location']['heading'] = (session['location']['heading'] + 90) % 360
            session['location']['new'] = False
            session.modified = True
            image(session['location']['lat'], session['location']['long'], session['location']['heading'])
    return render_template("home.html", username=session["username"], img = 'streetview_image.jpg', guessed = guessed)
def check_guess():
    loc = (request.form.get('input'))
    split = loc.split(", ")
    lat = float(split[0])
    long = float(split[1])
    guess =  [lat, long]
    #print(lat)
    answer= [session['location']['lat'], session['location']['long']]
    dist = haversine(guess[0], guess[1], answer[0], answer[1])
    return dist

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

MAX_DISTANCE = 120 # km from bronx to staten island
POINT_CAP = 5000

@app.route("/result", methods=["POST"])
def result():
    if "username" not in session:
        return redirect(url_for("auth"))

    # form field for lat and lon
    lat_str, lon_str = request.form["input"].split(",")
    guess_lat, guess_lon = float(lat_str), float(lon_str)

    tgt = session["location"] #distance from target location
    km  = haversine(guess_lat, guess_lon, tgt["lat"], tgt["long"])

    # 5000 · e^(‑10·d/MaxD)
    score = round(POINT_CAP * math.exp(-10 * (km / MAX_DISTANCE)))

    #db.add_score(session["username"], region="nyc", points=score, distance=km)

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.debug = True
    app.run()