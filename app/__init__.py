from flask import (
    Flask,
    flash,
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
from db import getRandLoc, add_score, top_scores, get_user_stats, get_user_games

#from .db import getRandLoc, add_score, top_scores, get_user_stats, get_user_games
#import os, math, time
#from . import db

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

def getKey():
    try:
        with open('keys/streetview.txt', 'r') as file:
            key = file.read().strip()
    except:
        print('error')
        return
    return key
    #return os.environ["MAPS_KEY"] for droplet

def toRadians(degree):
    return degree *(math.pi / 180.0)

def generate_latex_calculation(distance, max_dist, points):
    """Generate LaTeX formula showing how score was calculated"""
    latex = f"${points} = 5000 \\times e^{{-10 \\times \\frac{{{distance:.2f}}}{{{max_dist}}}}}$"
    return latex

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

    calculations = []
    max_dist = max_distance(region)
    for dist, pts in data["history"]:
        latex = generate_latex_calculation(dist, max_dist, pts)
        calculations.append(latex)
    
    return render_template(
        "results.html",finished=True,history=data["history"],
        total=data["total"],region=region, mode=mode,
        calculations=calculations
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

    if session.get("game_left") and "round" in session:
        for k in ("round", "location", "history", "expires", "mode", "timer_seconds", "move_mode", "game_start_time", "round_start_time", "timeout_occurred", "game_left"):
            session.pop(k, None)
        return redirect(url_for("region_page", region=region))

    # Get timer value from request, default to 60 seconds
    timer_seconds = int(request.args.get('timer', 60))
    # Get move mode from request, default to 'move' (can move around)
    move_mode = request.args.get('move', 'move')
    
    # Reset game state for fresh games or region/mode changes
    if "fresh" in request.args:
        for k in ("round", "location", "history", "expires", "mode", "region", "timer_seconds", "move_mode", "game_start_time", "round_start_time", "game_left"):
            session.pop(k, None)
        
        clean_url = url_for('play', mode=mode, region=region)
        if mode == "timed" and timer_seconds > 0:
            clean_url += f"?timer={timer_seconds}&move={move_mode}"
        else:
            clean_url += f"?move={move_mode}"
        return redirect(clean_url)

    if "round" in session and (session.get("mode") != mode or session.get("region") != region):
        for k in ("round", "location", "history", "expires", "mode", "region", "timer_seconds", "move_mode", "game_start_time", "round_start_time", "game_left"):
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
                "move_mode": move_mode,
                "game_start_time": time.time(),
                "round_start_time": time.time()
            }
        )
        if mode == "timed" and timer_seconds > 0:
            session["expires"] = time.time() + timer_seconds
        session.modified = True

    # Handle POST requests (user guesses and next round)
    if request.method == "POST":
        # Handle timeout submission from js
        if "timeout" in request.form:
            round_time = time.time() - session.get("round_start_time", time.time())
            session["history"].append((max_distance(region), 0))
            session.modified = True

            return render_template(
                "play.html",
                finished=False,
                guessed=True,
                timeout=True,
                dist=max_distance(region),
                pts=0,
                guess_lat=0,
                guess_lon=0,
                lat=session["location"]["lat"],
                lon=session["location"]["long"],
                round=session["round"],
                history=session["history"],
                total=sum(p for _,p in session["history"]),
                map_key=getKey(),
                mode=session["mode"],
                region=region,
                move_mode=session.get("move_mode", 'move'),
                is_final_round=(session["round"] == 5)
            )

        if "input" in request.form and "next" not in request.form:
            round_time = time.time() - session.get("round_start_time", time.time())
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
                total=sum(p for _, p in session["history"]),
                map_key=getKey(),
                mode=session["mode"],
                region=region,
                move_mode=session.get("move_mode", 'move'),
                is_final_round=(session["round"] == 5)
            )

        if "next" in request.form:
            # Handle next round after timeout or normal guess
            session["round"] += 1

            if session["round"] > 5:
                total = sum(p for _, p in session["history"])
                game_time = time.time() - session.get("game_start_time", time.time())
                add_score(
                    session["username"],
                    points=total,
                    distance=sum(d for d, _ in session["history"]),
                    mode=session["mode"],
                    region=region,
                    move_mode=session.get("move_mode", "move"),
                    game_time=game_time
                )
                session.setdefault("games", []).append({"scores": session["history"][:],"total":  total })
                session["results"] = {
                    "history": session["history"],
                    "total": total,
                    "mode":session["mode"]
                }
                for k in ("round","location","history","expires","mode", "timer_seconds", "move_mode", "game_start_time", "round_start_time", "timeout_occurred", "game_left"):
                    session.pop(k, None)
                return redirect(url_for("results", mode=mode, region=region))

            lat,lon = getRandLoc(region)
            session["location"] = {"lat": lat, "long": lon, "heading": 0}
            session["round_start_time"] = time.time()
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
    session["game_left"] = True
    for k in ("round", "location", "history", "expires", "mode", "timer_seconds", "move_mode", "game_start_time", "round_start_time", "timeout_occurred"):
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

@app.route("/profile")
def profile():
    """Display user profile with game history"""
    if "username" not in session:
        return redirect(url_for("landing"))
    
    username = session["username"]
    stats = db.get_user_stats(username)
    games_data = db.get_user_games(username)
    
    return render_template("profile.html", username=username, stats=stats, games=games_data)

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
            try:
                if db.check_user(username, password):
                    session["username"] = username
                    return redirect(url_for("home"))
                flash("Invalid username or password!")
            except:
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
