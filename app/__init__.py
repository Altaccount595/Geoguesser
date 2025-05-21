from flask import Flask, render_template, url_for, session, request, redirect, jsonify, flash
from db import getRandLoc, add_score, top_scores
import db, os, math
from api_handle import image, getKey

RADIUS = 6371.0
MAX_DISTANCE = 120 # km from bronx to staten island
POINT_CAP = 5000

app = Flask(__name__)

app.secret_key = os.urandom(32)

db.create_db()

# helper functions

def toRadians(degree):
    return degree *(math.pi / 180.0)

def haversine(lat1, lon1, lat2, lon2):
    lat1 = toRadians(lat1)
    lon1 = toRadians(lon1)
    lat2 = toRadians(lat2)
    lon2 = toRadians(lon2)
    dLat = lat2 - lat1
    dLon = lon2 - lon1
    a = (math.sin(dLat / 2)
         * math.sin(dLat / 2)
         + math.cos(lat1)
         * math.cos(lat2)
         * math.sin(dLon / 2)
         * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return RADIUS * c

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

# home route

@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("auth"))
    return render_template("home.html", username=session["username"])

@app.route("/results/<region>")
def results(region):
    if "results" not in session:
        return redirect(url_for("home"))
    data = session["results"]
    return render_template(
        "results.html",finished=True,history=data["history"],
        total=data["total"],region=region
    )

#play route

@app.route("/play/<region>", methods=["GET", "POST"])
def play(region):
    if "username" not in session:
        return redirect(url_for("auth"))

    if "round" not in session:
        session.update({"region": region,"round": 1,"history": []})
        lat,lon = getRandLoc()
        session["location"] = {"lat": lat, "long": lon, "heading": 0}
        session.modified = True

    if request.method == "POST":
        if "input" in request.form and "next" not in request.form:
            dist = check_guess()
            pts = round(POINT_CAP * math.exp(-10 * (dist / MAX_DISTANCE)))
            guess = list(map(float, request.form["input"].split(", ")))
            actual = [session["location"]["lat"], session["location"]["long"]]

            session["history"].append((round(dist, 2), pts))
            session.modified = True

            return render_template(
                "play.html",finished=False,guessed=True,
                dist=round(dist,2),guess_lat=guess[0],guess_lon=guess[1],
                lat=actual[0],lon=actual[1],round=session["round"],
                history=session["history"],
                total=sum(p for _,p in session["history"]),map_key=getKey()
            )

        if "next" in request.form:
            session["round"] += 1

            if session["round"] > 5:
                total = sum(p for _, p in session["history"])
                add_score(
                    session["username"], points=total,
                    distance=sum(d for d, _ in session["history"]),region=region
                )
                session.setdefault("games", []).append({"scores": session["history"][:],"total":  total })
                session["results"] = {"history": session["history"], "total": total}
                session.pop("round")
                session.pop("location")
                return redirect(url_for("results", region=region))

            lat,lon = getRandLoc()
            session["location"] = {"lat": lat, "long": lon, "heading": 0}
            session.modified = True

            return redirect(url_for("play", region=region))

    return render_template(
        "play.html",finished=False,history=session.get("history", []),
        total=sum(p for _, p in session.get("history", [])),
        lat=session["location"]["lat"],lon=session["location"]["long"],
        map_key=getKey(),round=session.get("round", 1)
    )

#leaderboard route
@app.route("/leaderboard")
@app.route("/leaderboard/<region>")
def leaderboard(region="nyc"):
    scores = db.top_scores(region)
    return render_template("leaderboard.html", scores=scores, region=region)

#profile route

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("auth"))
    return render_template("profile.html", games=session.get("games", []))

# auth  and logout routes
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

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
