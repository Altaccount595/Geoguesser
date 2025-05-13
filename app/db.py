'''
TopherTime Studios - Tawab Berri, Alex Luo, Jacob Lukose, Jonathan Metzler
SoftDev
Spring 2025
p05 - DevoGuessr
'''
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, csv, random

DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "users.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS loc;
        DROP TABLE IF EXISTS address;

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
	    long REAL NOT NULL
        );
    """)
    """CREATE TABLE IF NOT EXISTS address (
            add_id INTEGER PRIMARY KEY AUTOINCREMENT,
            num INTEGER NOT NULL,
            street TEXT NOT NULL,
            city TEXT NOT NULL,
            region TEXT NOT NULL,
            post INTEGER NOT NULL
        );"""
    conn.commit()
    conn.close()


def add_user(username, password):
    create_db()
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

def check_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row and check_password_hash(row["password_hash"], password)

def add_score(username, region, points, distance, mode="untimed"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    id = cur.fetchone()
    if not id:
        conn.close()
        return False
    user_id = id["user_id"]
    cur.execute("INSERT INTO scores (user_id, region, mode, points, distance) VALUES (?, ?, ?, ?, ?)", (user_id, region, mode, points, distance,))
    conn.commit()
    conn.close()
    return True

def loc_db():
    count = 0
    conn = get_db_connection()
    cur = conn.cursor()
    with open('../statewide.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            #print(row[0], row[1])
            if(count > 5000):
                break
            cur.execute("INSERT INTO loc (lat, long) VALUES (?, ?)", (row[1], row[0]))
            cur.execute("SELECT MAX(loc_id) FROM loc")
            #len = cur.fetchone()[0]
            #print(row[1], row[0])
            count += 1
    conn.commit()
    conn.close()
'''
def address_db():
    count = 0
    conn = get_db_connection()
    cur = conn.cursor()
    with open('../statewide.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            #print(row[0], row[1])
            if(count > 1000):
                break
            cur.execute("INSERT INTO address (num, street, city, region, post) VALUES (?, ?, ?, ?, ?)", (row[2], row[3], row[5], row[7], row[8]))
            cur.execute("SELECT MAX(add_id) FROM address")
            #len = cur.fetchone()[0]
            #print(row[1], row[0])
            count += 1
    conn.commit()
    conn.close()
'''
def getRandLoc():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(loc_id) FROM loc;")
    len = cur.fetchone()[0]
    print(len)
    rand = random.randint(1, len)
    cur.execute("SELECT * FROM loc WHERE loc_id = ?", (rand,))
    rand_loc = cur.fetchone()
    lat_long = [rand_loc[1], rand_loc[2]]
    #print(lat_long)
    conn.close()
    return lat_long
'''
def getRandAddress():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(add_id) FROM address;")
    len = cur.fetchone()[0]
    #print(len)
    rand = random.randint(0, len)
    cur.execute("SELECT * FROM address WHERE add_id = ?", (rand,))
    loc = cur.fetchone()
    address = f"{loc[1]} {loc[2]}, {loc[3]}, {loc[4]} {loc[5]}"
    #print(address)
    conn.close()
    return address
'''
def top_scores():
    conn = get_db_connection()
    cur  = conn.cursor()

    cur.execute("""
        SELECT u.username, s.region, s.points, s.distance
        FROM scores AS s
        JOIN users AS u ON u.user_id = s.user_id
        ORDER BY s.points DESC, s.distance ASC;
    """)

    rows = cur.fetchall()
    conn.close()
    return rows

#create_db()
#loc_db()

