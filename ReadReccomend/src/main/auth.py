import DataBase as db
import jwt
from datetime import datetime, timedelta
from flask import abort
import sqlite3
import hashlib
from random import random

secretKey = str(random())

Token_map = {}

reset_time = timedelta(minutes=15)
max_live_time = timedelta(days=1)


def registerAccount(username, password):

    if len(username) < 1 or len(password) < 1:
        abort(400, 'Username and password must be at least one character')

    # hash password
    password = passwordHash(password)
    # check if already in databse
    user = db.getUser(username)
    if (isinstance(user, sqlite3.Error)):
        abort(400, "user cannot be added: " + str(user))
    if (user != None):
        abort(400, "user already exists")
    # add user to database
    dbResponse = db.addUser(username, password)
    if(isinstance(dbResponse, sqlite3.Error)):
        abort(400, "user cannot be added: " + str(dbResponse))
    # create Token
    token = createUserToken(username)
    # add token to active table
    addOrUpdateToken(token)
    # return token
    return token.decode("UTF-8")


def login(username, password):
    user = db.getUser(username)
    if (user == None):
        abort(400, "user doesnt exist")

    if (user["password"] != passwordHash(password)):
        abort(400, "incorrect password")
    token = createUserToken(username)
    addOrUpdateToken(token)
    return token.decode("UTF-8")


def authenticate(request):
    def decorator(endpoint):
        def wrapper(*args, **kwargs):
            if("Token" not in request.headers.keys()):
                abort(401, "No Token Present")
            token = request.headers['token'].encode("UTF-8")
            if(token not in Token_map.keys()):
                abort(401, "Token is Invalid")
            expired = addOrUpdateToken(token)
            if(not expired):
                abort(401, "Token has expired")
            payload = jwt.decode(token, secretKey, algorithms=['HS256'])
            username = payload['username']
            user = db.getUser(username)
            return endpoint(*args, user=user, **kwargs)
        return wrapper
    return decorator

#probably want this to be more secure
def passwordHash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# we may need to include something like the date in this hash as currently tokens are the same every time
# for now im just going to make the key a random number generated at startup
def createUserToken(username):
    return jwt.encode({"username": username}, secretKey, algorithm='HS256')


def logout(username):
    token = createUserToken(username)
    if token not in Token_map.keys():
        abort(400, "user not logged in")
    del Token_map[token]


def addOrUpdateToken(token):

    if token not in Token_map.keys():
        Token_map[token] = {
            "current_life": datetime.now() + reset_time,
            "max_life": datetime.now() + max_live_time,
        }
        return True

    if Token_map[token]["max_life"] < datetime.now() or Token_map[token]["current_life"] < datetime.now():
        return False

    Token_map[token]["current_life"] = datetime.now() + reset_time
    return True
