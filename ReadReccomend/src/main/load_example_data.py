import sqlite3
import os

DATABASE_PATH = "./db"
DATABASE_DATA = "./example.sql"
DATABASE_SCHEMA = "./schema.sql"

# So i don't have to delete the data base each time
try:
    os.remove(DATABASE_PATH)
except OSError:
    pass

db = sqlite3.connect(DATABASE_PATH)
with open(DATABASE_SCHEMA) as f:
    db.executescript(f.read())

db = sqlite3.connect(DATABASE_PATH)
with open(DATABASE_DATA) as f:
    db.executescript(f.read())
