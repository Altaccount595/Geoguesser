from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import math
import os
import time

import db
from db import getRandLoc, add_score, top_scores, get_user_stats
from api_handle import image, getKey

#from .db import getRandLoc, add_score, top_scores
#import os, math, time
#from . import db
#from .api_handle import image, getKey

RADIUS = 6371.0
REGION_MAX_DISTANCE = {
    "nyc": 120, # km from bronx to staten island
    "us": 4500, # km from maine to hawaii
    "europe": 3800, # km from portugal to ural mountains of russia
    "global": 20000, # half earth's circumference
}
POINT_CAP = 5000

app = Flask(__name__)
app.secret_key = os.urandom(32)

#db.create_db()

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

def max_distance(region):
    return REGION_MAX_DISTANCE.get(region, REGION_MAX_DISTANCE["global"])

def check_guess():
    """
    Process a user's guess and calculate distance from actual location
    Returns distance in kilometers
    """
    loc = (request.form.get('input'))
    split = loc.split(", ")
    lat = float(split[0])
    long = float(split[1])
    guess =  [lat, long]
    answer= [session['location']['lat'], session['location']['long']]
    dist = haversine(guess[0], guess[1], answer[0], answer[1])
    return dist

# Route Handlers

@app.route("/")
def landing():
    if "username" in session:
        return render_template("home.html", username=session["username"])
    return render_template("landing.html")

@app.route("/home")
def home():
    return render_template("home.html", username=session.get("username"))

@app.route("/results/<mode>/<region>")
def results(mode, region):
    if "results" not in session:
        return render_template("home.html", username=session.get("username"))
    data = session["results"]
    return render_template(
        "results.html",finished=True,history=data["history"],
        total=data["total"],region=region, mode=mode
    )

#play route

@app.route("/play/<region>", methods=["GET", "POST"], defaults={"mode": "untimed"})
@app.route("/play/<mode>/<region>", methods=["GET","POST"])
def play(mode, region):
    """
    Main game route handling:
    - Game initialization
    - Timer management for timed mode
    - Processing user guesses
    - Score calculation
    - Round progression
    - Game completion
    
    Parameters:
    - mode: Game mode ('timed' or 'untimed')
    - region: Game region ('nyc', 'us', 'europe', 'global')
    """
    if "username" not in session:
        return redirect(url_for("landing"))

    # Get timer value from request, default to 60 seconds
    timer_seconds = int(request.args.get('timer', 60))
    # Get move mode from request, default to 'move' (can move around)
    move_mode = request.args.get('move', 'move')
    
    # Reset game state for fresh games or region/mode changes
    if "fresh" in request.args:
        for k in ("round", "location", "history", "expires", "mode", "region", "timer_seconds", "move_mode"):
            session.pop(k, None)

    if "round" in session and (session.get("mode") != mode or session.get("region") != region):
        for k in ("round", "location", "history", "expires", "mode", "region", "timer_seconds", "move_mode"):
            session.pop(k, None)

    # Initialize new game
    if "round" not in session:
        lat,lon = getRandLoc(region)
        session.update(
            {
                "region": region,"mode": mode,
                "round": 1,"history": [],
                "location": {"lat": lat, "long": lon, "heading": 0},
                "timer_seconds": timer_seconds,
                "move_mode": move_mode
            }
        )
        if mode == "timed" and timer_seconds > 0:
            session["expires"] = time.time() + timer_seconds
        session.modified = True

    # Handle timer expiration
    if session["mode"] == "timed" and session.get("timer_seconds", 60) > 0 and time.time() > session.get("expires", float('inf')):
        session["history"].append((max_distance(region), 0))
        session["round"] += 1

        if session["round"] > 5:
            total = sum(p for _, p in session["history"])
            add_score(
                session["username"], points=total,
                distance=sum(d for d, _ in session["history"]),
                mode=session["mode"], region=region,
                move_mode=session.get("move_mode", "move")
            )
            session.setdefault("games", []).append(
                {"scores": session["history"][:], "total": total}
            )
            session["results"] = {
                "history": session["history"],
                "total": total,
                "mode": session["mode"]
            }
            for k in ("round", "location", "history", "expires", "mode", "timer_seconds", "move_mode"):
                session.pop(k, None)
            return redirect(url_for("results", mode=mode, region=region))
        lat, lon = getRandLoc(region)
        session["location"] = {"lat": lat, "long": lon, "heading": 0}
        if session.get("timer_seconds", 60) > 0:
            session["expires"] = time.time() + session["timer_seconds"]
        session.modified = True
        if mode == "timed":
            return redirect(url_for("play", mode=mode, region=region, timer=session.get("timer_seconds", 60), move=session.get("move_mode", 'move')))
        else:
            return redirect(url_for("play", mode=mode, region=region, move=session.get("move_mode", 'move')))

    # Handle POST requests (user guesses and next round)
    if request.method == "POST":
        if "input" in request.form and "next" not in request.form:
            dist = check_guess()
            pts = round(POINT_CAP * math.exp(-10 * (dist / max_distance(region))))
            guess = list(map(float, request.form["input"].split(", ")))
            actual = [session["location"]["lat"], session["location"]["long"]]

            session["history"].append((round(dist, 2), pts))
            session.modified = True

            return render_template(
                "play.html",
                finished=False,
                guessed=True,
                dist=round(dist,2),
                pts=pts,
                guess_lat=guess[0],
                guess_lon=guess[1],
                lat=actual[0],lon=actual[1],
                round=session["round"],
                history=session["history"],
                total=sum(p for _,p in session["history"]),
                map_key=getKey(),
                mode=session["mode"],
                region=region,
                move_mode=session.get("move_mode", 'move'),
            )

        if "next" in request.form:
            session["round"] += 1

            if session["round"] > 5:
                total = sum(p for _, p in session["history"])
                add_score(
                    session["username"],
                    points=total,
                    distance=sum(d for d, _ in session["history"]),
                    mode=session["mode"],
                    region=region,
                    move_mode=session.get("move_mode", "move")
                )
                session.setdefault("games", []).append({"scores": session["history"][:],"total":  total })
                session["results"] = {
                    "history": session["history"],
                    "total": total,
                    "mode":session["mode"]
                }
                for k in ("round","location","history","expires","mode", "timer_seconds", "move_mode"):
                    session.pop(k, None)
                return redirect(url_for("results", mode=mode, region=region))

            lat,lon = getRandLoc(region)
            session["location"] = {"lat": lat, "long": lon, "heading": 0}
            if session["mode"] == "timed" and session.get("timer_seconds", 60) > 0:
                session["expires"] = time.time() + session["timer_seconds"]
            session.modified = True

            if mode == "timed":
                return redirect(url_for("play", mode=mode, region=region, timer=session.get("timer_seconds", 60), move=session.get("move_mode", 'move')))
            else:
                return redirect(url_for("play", mode=mode, region=region, move=session.get("move_mode", 'move')))

    remaining = None
    if session["mode"] == "timed" and session.get("timer_seconds", 60) > 0:
        remaining = max(0, math.ceil(session["expires"] - time.time()))

    return render_template(
        "play.html",
        guessed=False,
        finished=False,
        history=session.get("history", []),
        total=sum(p for _, p in session.get("history", [])),
        lat=session["location"]["lat"],lon=session["location"]["long"],
        map_key=getKey(),
        round=session.get("round", 1),
        mode=session["mode"],
        remaining_time=remaining,
        region=region,
        move_mode=session.get("move_mode", 'move'),
    )

@app.route("/leave", methods=["POST", "GET"])
def leave_game():
    """clears game state and returns to region page"""
    region = request.form.get("region", "nyc")
    for k in ("round", "location", "history", "expires", "mode", "timer_seconds", "move_mode"):
        session.pop(k, None)
    return redirect(url_for("region_page", region=region))

@app.route("/region/<region>", methods=["GET", "POST"])
def region_page(region):
    move_scores = db.top_scores(region, move_mode="move")[:25]
    nomove_scores = db.top_scores(region, move_mode="nomove")[:25]
    
    username = session.get("username")
    if request.method == "POST" and not username:
        flash("You must be logged in to play")
    return render_template("region.html", region=region, move_scores=move_scores, nomove_scores=nomove_scores, username=username)

@app.route("/leaderboard")
@app.route("/leaderboard/<region>")
def leaderboard(region="nyc"):
    """Display leaderboard for specified region (defaults to NYC)"""
    scores = db.top_scores(region)
    return render_template("leaderboard.html", scores=scores, region=region)

@app.route("/profile")
def profile():
    """Display user profile with game history"""
    if "username" not in session:
        return redirect(url_for("landing"))
    
    username = session["username"]
    stats = db.get_user_stats(username)
    
    return render_template("profile.html", username=username, stats=stats, games=session.get("games", []))

@app.route("/information")
def information():
    """Display information page"""
    return render_template("information.html", username=session.get("username"))

@app.route("/auth", methods=["GET", "POST"])
def auth():
    """Handles user authentication"""
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
    return redirect(url_for("landing"))

@app.route('/createAccount')
def createAccount():
    if "username" in session:
        return redirect(url_for("home"))
    return render_template("createAccount.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for("landing"))

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
