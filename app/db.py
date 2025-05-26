'''
TopherTime Studios - Tawab Berri, Alex Luo, Jacob Lukose, Jonathan Metzler
SoftDev
Spring 2025
p05 - DevoGuessr
'''
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import random
import sqlite3

DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "users.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# creates db for users and locations
def create_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS scores;
        DROP TABLE IF EXISTS address;
        DROP TABLE IF EXISTS loc;  
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS scores (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            region TEXT NOT NULL,
            mode TEXT NOT NULL DEFAULT 'untimed',
            points INTEGER NOT NULL,
            distance REAL NOT NULL
	);

	CREATE TABLE IF NOT EXISTS loc (
        loc_id INTEGER PRIMARY KEY AUTOINCREMENT,
	    lat REAL NOT NULL,
	    long REAL NOT NULL,
        region TEXT NOT NULL DEFAULT 'nyc'
        );
    """)
    conn.commit()
    conn.close()

# add users to users database
def add_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    pw_hash = generate_password_hash(password)
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, pw_hash)
        )
        conn.commit()
        ok = True
    except sqlite3.IntegrityError:
        ok = False
    finally:
        conn.close()
    return ok

# check users password and username
def check_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row and check_password_hash(row["password_hash"], password)

# adds users scores
def add_score(username, points, distance, mode="untimed",  region="nyc"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    id = cur.fetchone()
    if not id:
        conn.close()
        return False
    user_id = id["user_id"]
    cur.execute(
        "INSERT INTO scores (user_id, region, mode, points, distance) VALUES (?, ?, ?, ?, ?)",
        (user_id, region, mode, points, distance,)
    )
    conn.commit()
    conn.close()
    return True

def import_csv_to_loc(region, csv_path):
    conn = get_db_connection()
    cur  = conn.cursor()

    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        next(reader, None)                
        for row in reader:
            lon = float(row[0])            
            lat = float(row[1])            
            cur.execute(
                "INSERT INTO loc (lat, long, region) VALUES (?, ?, ?)",
                (lat, lon, region)
            )
    conn.commit()
    conn.close()

def import_folder_to_loc(region, folder_path):
    for file in os.listdir(folder_path):       
        if file.lower().endswith(".csv"):     
            csv_path = os.path.join(folder_path, file)
            import_csv_to_loc(region, csv_path)

#gets random location, this is also subject to change with the use of Google Geocoding API in order to avoid unintellgible coords
def getRandLoc(region="nyc"):
    conn = get_db_connection()
    cur = conn.cursor()
    if region == "global":
        cur.execute("SELECT lat, long FROM loc ORDER BY RANDOM() LIMIT 1")
    else:
        cur.execute(
            "SELECT lat, long FROM loc WHERE region = ? ORDER BY RANDOM() LIMIT 1",
            (region,)
        )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise ValueError("No coordinates found for region " + region + ".")
    return [row["lat"], row["long"]]

#gets top scores to serve to leaderboard
def top_scores(region="nyc"):
    conn = get_db_connection()
    cur  = conn.cursor()

    cur.execute("""
        SELECT u.username, s.points, s.distance
        FROM scores AS s
        JOIN users AS u ON u.user_id = s.user_id
        WHERE s.region = ?
        ORDER BY s.points DESC, s.distance ASC
        LIMIT 30;
    """, (region,))

    rows = cur.fetchall()
    conn.close()
    return rows