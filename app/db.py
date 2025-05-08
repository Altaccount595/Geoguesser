'''
TopherTime Studios - Tawab Berri, Alex Luo, Jacob Lukose, Jonathan Metzler
SoftDev
Spring 2025
p05 - DevoGuessr
'''

import sqlite3

DB_FILE = "app/database.db"

db = sqlite3.connect(DB_FILE, check_same_thread = False)
c = db.cursor()

def create():
    c.execute("DROP TABLE IF EXISTS users;")
    c.execute(
        '''
    )
