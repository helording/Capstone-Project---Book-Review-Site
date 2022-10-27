import sqlite3
import hashlib
import pprint
from flask import abort
from datetime import datetime
import pandas as pd
import json


DATABASE_PATH = "./db"
DATABASE_SCHEMA = "./schema.sql"


def createOrGetDB():
    db = sqlite3.connect(DATABASE_PATH)
    with open(DATABASE_SCHEMA) as f:
        db.executescript(f.read())
        db.commit()
    return db


# Wrapper around a general SQL query
def cmd(query, values=[]):
    try:
        db = createOrGetDB()
        ret = db.execute(query, values).fetchall()
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return str(error)
    return ret


def getBook(id):
    try:
        db = createOrGetDB()
        book = db.execute("SELECT * FROM Books WHERE id == ?", [id]).fetchall()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    if len(book) != 1:
        return None
    return parseBook(book[0])


# Given a dictionary "ratings" (where key=bookId, value="list of ratings"),
# return a list of book ids where the mean rating is greater or equal to the
# minRating
def getRatingsAbove(ratings, minRating):

    bookIds = []

    for k, v in ratings.items():
        mean = sum(v) / len(v)
        if mean >= minRating:
            bookIds.append(k)

    return bookIds


# Returns a list of book ids where the average rating is greater or equal to
# the "rating"
def getBookIdsByMinRating(rating):
    try:
        rating = int(rating)
    except ValueError:
        return {'error' : f'Rating is not a valid integer: {rating}'}

    if rating < 0 or rating > 5:
       return {'error': f'Rating is outside of valid range: {rating}'}
    reviews = cmd('SELECT * FROM Reviews')
    allRatings = {}
    for rev in reviews:
        r = parseReview(rev)
        if r['bookId'] not in allRatings:
            allRatings[r['bookId']] = [r['rating']]
        else:
            allRatings[r['bookId']].append(r['rating'])

    return getRatingsAbove(allRatings, rating)

def getBookByTitle(title):
    try:
        db = createOrGetDB()
        book = db.execute("SELECT * FROM Books WHERE Title == ?", [title]).fetchall()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    if len(book) != 1:
        return None
    return parseBook(book[0])


# Return a list of book IDs based on the book title
def getBookIdsByTitle(title):
    bookIds = cmd("SELECT id FROM Books WHERE Title LIKE ?", [f'%{title}%'])

    if type(bookIds) == str:
        return {'error' : bookIds}
    elif bookIds == []:
        return {'error' : f'No books with title: {title}'}

    return [i[0] for i in bookIds]


def getBookIdsByCountry(country):

    bookIds = cmd("SELECT id FROM Books WHERE country LIKE ?", [f'%{country}%'])

    if type(bookIds) == str:
        return {'error' : bookIds}
    elif bookIds == []:
        return {'error' : f'No books with country: {country}'}

    return [i[0] for i in bookIds]


def getBookIdsByCatagoryId(catId):
    bookIds = cmd("SELECT id FROM Books WHERE catagoryId == ?", [catId])

    if type(bookIds) == str:
        return {'error' : bookIds}
    elif bookIds == []:
        name = getCatagory(catId)
        if name is not None:
            name = name['catagory']
        return {'error' : f'No books with catagoryId: {name}'}

    return [i[0] for i in bookIds]


# Return a list of books based on a search criteria. Each criteria is AND'd
# together (i.e. if we are searching for the title and the author, a given
# book must satisify the title AND the author). The criteria is passed as a
# regular python3 dictionary. The return value is a regular dictionary of
# books, similar to the getAllBooks function. If there is an error, a
# dictionary is returned with a single key (set to "error") and value
# (containing an error string).
#
# The values in the criteria are:
# Title -> Title of book, string, fuzzy searched
# Country -> Country of book, string, fuzzy searched
# catagoryId -> ID of catagory, int
# author -> Name of author, string, fuzzy searched
# authorId -> Id of author, int
# publisher -> Name of publisher, string, fuzzy searched
# author -> Name of author, string, fuzzy searched
# authorId -> Id of author, int
# minRating -> Minimium rating of possible books, int/float
def getBookAdvSearch(criteria):
    ids = []

    searchHandles = {
        'Title' : getBookIdsByTitle,
        'Country' : getBookIdsByCountry,
        'catagoryId' : getBookIdsByCatagoryId,
        'author' : getBookIdsByAuthor,
        'authorId' : getBookIdsFromAuthorId,
        'publisher' : getBookIdsByPublisher,
        'minRating' : getBookIdsByMinRating
    }

    for k, v in criteria.items():
        if k not in searchHandles:
            return {'error' : f'Unkown search parameter: {k}'}
        ret = searchHandles[k](v)
        if 'error' in ret:
            return ret
        ids.append(ret)


    if ids == []:
        return {'error' : 'Invalid search parameters'}
    bookIds = set.intersection(*map(set, ids))

    books = []
    for bookId in bookIds:
        book = getBook(bookId)
        books.append(book)

    # Thank you stack overflow gods:
    # https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary
    return sorted(books, key=lambda b: b['id'])


def deleteBook(id):
    try:
        db = createOrGetDB()
        db.execute("DELETE FROM BOOKS WHERE id == ?", [id])
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return True

# Returns a list of users that the user "userName" is following
def getLeaders(userName):
    leaders = cmd('''
        SELECT leaderId FROM Followers WHERE followerId == ?
    ''', [userName])

    if type(leaders) == str:
        return leaders

    ret = []
    for l in leaders:
        user = getUser(l[0])
        if type(user) == str:
            return user
        ret.append(user)
    return ret

# Returns a list of users that are following the "leaderName"
def getFollowers(leaderName):
    followers = cmd('''
        SELECT followerId FROM Followers WHERE leaderId == ?
    ''', [leaderName])
    if type(followers) == str:
        return followers

    ret = []
    for f in followers:
        user = getUser(f[0])
        if type(user) == str:
            return user
        ret.append(user)
    return ret

# Return True if "userName" is following "leaderName", else return False
def isFollowing(leaderName, userName):
    ret = cmd('''
        SELECT * FROM Followers WHERE leaderId == ? AND followerId == ?
    ''', [leaderName, userName])

    if type(ret) == str:
        return ret

    if len(ret) == 1:
        return True

    return False

def followLeader(leaderName, userName):
    if leaderName == userName:
        return {'error':'You can\'t follow yourself'}

    ret = isFollowing(leaderName, userName)
    if type(ret) == str:
        return ret
    elif ret == True:
        return {'error':'You are already following this user'}

    return cmd('''
        INSERT INTO Followers (leaderId,followerId) VALUES(?,?)
    ''', [leaderName, userName])

def unfollowLeader(leaderName, userName):
    if leaderName == userName:
        return {'error':'You can\'t unfollow yourself'}

    ret = isFollowing(leaderName, userName)
    if type(ret) == str:
        return ret
    elif ret == False:
        return {'error':'You are not following this user'}

    return cmd('''
        DELETE FROM Followers WHERE leaderId == ? AND followerId == ?
    ''', [leaderName, userName])

# Given a user's username return a list of their events
def getEventsFromUser(userName):
    events = cmd('''
        SELECT * FROM Events WHERE leaderId == ? ORDER BY dateAdded ASC
    ''', [userName])
    if type(events) == str:
        return events

    eventList = []

    for event in events:
        e = parseEvent(event)
        eventList.append(e)

    return eventList



def getEventsForUser(userName):
    leaders = getLeaders(userName)
    if type(leaders) == str:
        return leaders

    if len(leaders) == 0:
        return leaders

    query = 'SELECT * FROM Events WHERE leaderId == ?'
    for _ in range(len(leaders)-1):
        query += ' OR leaderId == ? '
    query += 'ORDER BY dateAdded ASC'

    leadersList = [l['username'] for l in leaders]
    events = cmd(query, leadersList)

    eventList = []

    for e in events:
        e = parseEvent(e)
        eventList.append(e)

    return eventList

def getEventByEventId(eventId):
    ret = cmd('''
        SELECT *
        FROM Events
        WHERE eventId == ?
    ''', [eventId])
    if type(ret) == str:
        return {'error':ret}
    if ret == []:
        return {'error':'Event does not exist in database'}
    return parseEvent(ret[0])

def deleteEventByEventId(eventId):
    return cmd('''
        DELETE FROM Events
        WHERE eventId == ?
    ''', [eventId])

def addEventToTable(leader, eventType, bookId, dateTime):
    eventId = leader + eventType + str(bookId) + dateTime
    eventId = hashlib.sha256(eventId.encode()).hexdigest()
    return cmd('''
        INSERT INTO Events (leaderId,eventType,bookId,dateAdded,eventId)
        VALUES(?,?,?,?,?)
    ''', [leader, eventType, bookId, dateTime, eventId])

def addEventReadingBook(leaderName, bookId):
    return addEventToTable(
        leaderName,
        'read',
        bookId,
        datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    )

def addEventDoneBook(leaderName, bookId):
    return addEventToTable(
        leaderName,
        'done',
        bookId,
        datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    )

def parseEvent(row):
    return {
        'leader'  : row[0],
        'type'    : row[1],
        'book'    : getBook(row[2]),
        'date'    : row[3],
        'eventId' : row[4]
    }

# TODO Add author(s) to Authors_Books table
def addBook(book):
    try:
        # Why can't why find an id that isn't taken yet?
        titleAuthorString = book['title'] + book['author']
        id = hashlib.md5(titleAuthorString.encode()).hexdigest()
        db = createOrGetDB()
        db.execute("INSERT INTO Books (id,Title,Country,catagoryId,Keywords,image_url,description) VALUES (?,?,?,?,?,?,?);",
            [
                id,
                book['title'],
                #book['author'],
                book['country'],
                book['genre'], # NOTE: It would make more sense to be "catagoryId"
                book['keywords'],
                book['imageURL'],
                book['description'],
            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return {"id": id}


def addUser(username, password_sha256):
    try:
        db = createOrGetDB()
        db.execute("INSERT INTO Users (username, pass) VALUES (?,?);",
            [
                username,
                password_sha256
            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return True


def getUser(username):
    try:
        db = createOrGetDB()
        user = db.execute("SELECT * FROM Users WHERE username = ?;",
            [
                username
            ]
        ).fetchall()
        if len(user) != 1:
            return None
        user = user[0]
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return parseUser(user)


def getAllBooks():
    try:
        db = createOrGetDB()
        books = db.execute('''
            SELECT * FROM Books
        ''').fetchall()
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    if len(books) == 0:
        return None
    return [parseBook(b) for b in books]

def getAllUsers():
    try:
        db = createOrGetDB()
        users = db.execute('''
            SELECT username FROM Users
        ''').fetchall()
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return users

def getUserAll(username):
    try:
        db = createOrGetDB()
        info = db.execute("SELECT * FROM Users WHERE username = ?",
            [username]
        ).fetchall()
        db.commit()
    except sqlite3.Error as error:
        abor(400, str(error))
        return error

    if len(info) != 1:
        return None

    info = parseUser(info[0])
    info["collections"] = getCollectionsByUser(username)
    return info

def parseUser(row):
    return {
        "username" : row[0],
        "password" : row[1],
        "selfInfo" : row[2],
    }


# Because col_id is created by encoding the name... two collections from different cannot havve the same name
# as then they'll have the same id
# XXX This can create a hash collision, if one user has their collection and a
#     malicous user splits his/her name in half and appends the name to the
#     collection name...
def addCollection(name, user):
    col_id = hashlib.md5(name.encode() + user.encode()).hexdigest()
    try:
        db = createOrGetDB()
        db.execute("INSERT INTO Collections (id, name, user_created) VALUES (?,?,?);",
            [
                col_id,
                name,
                user,
            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return col_id

# Return True if the bookid is in the collid
# Return False if the bookid is in the collid
def bookInCollection(collId, bookId):
    ret = cmd(
        'SELECT book_id FROM Collections__Book WHERE collections_id == ? AND book_id == ?',
        [collId, bookId]
    )
    if type(ret) == str:
        return {'error':ret}
    if len(ret) == 0:
        return False # Book does not exist in collection
    return True

def addBookToCollection(collection_id, book_id):
    ret = bookInCollection(collection_id, book_id)
    if type(ret) == dict:
        return ret
    elif ret == True:
        return {'error':'Book is already in collection'}

    try:
        db = createOrGetDB()
        date = datetime.today().strftime('%Y-%m-%d')
        db.execute("INSERT INTO Collections__Book (collections_id, book_id, dateAdded) VALUES (?,?,?);",
            [
                collection_id,
                book_id,
                date,
            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return True


def rmBookFromCollection(collId, bookId):
    try:
        db = createOrGetDB()
        db.execute('''DELETE FROM Collections__Book
                        WHERE collections_id == ?
                        AND book_id == ?''', [collId, bookId])
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return True


def getCollection(collection_id):
    try:
        db = createOrGetDB()
        collection = db.execute("SELECT * FROM Collections WHERE id == ?;",
            [
                collection_id,
            ]
        ).fetchall()
        if len(collection) != 1:
            return None
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return parseCollection(collection[0])

def getCollectionsByUser(user):
    try:
        db = createOrGetDB()
        collection = db.execute("SELECT * FROM Collections WHERE user_created == ?;",
            [
                user,
            ]
        ).fetchall()
        if len(collection) == 0:
            return None
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return [parseCollection(c) for c in collection]


def find_books(query):
    # this should be expanded to search for all aspects. however for now i will just search by title.
    try:
        db = createOrGetDB()
        books = db.execute("SELECT * FROM Books WHERE title LIKE ?;",
            [
                "%" + query + "%",
            ]
        ).fetchall()
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return [parseBook(book) for book in books]


def books_in_collection(collection_id):
    try:
        db = createOrGetDB()
        books = db.execute('''SELECT * FROM Books
                                INNER JOIN Collections__book
                                    ON Collections__book.book_id = Books.id
                                WHERE collections_id == ?;''',
            [
                collection_id,
            ]
        ).fetchall()
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return [parseBook(book) for book in books]

def deleteCollection(collId):
    ret = cmd('''
        DELETE FROM Collections__Book WHERE collections_id == ? ;
    ''', [collId])
    if type(ret) == str:
        return ret

    ret = cmd('''
        DELETE FROM Collections WHERE id == ? ;
    ''', [collId])
    if type(ret) == str:
        return ret

    return True

def findCollections(query):
    # this should be expanded to search for all aspects. however for now i will just search by title.
    try:
        db = createOrGetDB()
        collections = db.execute("SELECT * FROM Collections WHERE name LIKE ?;",
            [
                "%" + query + "%",
            ]
        ).fetchall()
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return [parseCollection(collection) for collection in collections]

# Returns a list of ids for the given author. This is a fuzzy search,
# therefore only part of the author's name is needed
def getAuthorIds(author):
    authorIds = cmd('SELECT id FROM Authors WHERE name LIKE ?', [f'%{author}%'])
    if type(authorIds) == str:
        return {'error' : authorIds}
    elif authorIds == []:
        return {'error' : f'Author does not exist: {author}'}
    return [a[0] for a in authorIds]

# Returns a list of book ids written by the given author. The author is fuzzy
# searched
def getBookIdsByAuthor(author):
    authorIds = getAuthorIds(author)
    if 'error' in authorIds:
        return authorIds
    ret = []
    for a in authorIds:
        li = getBookIdsFromAuthorId(a)
        if 'error' in li:
            continue # ignore errors
        for n in li:
            ret.append(n)
    return ret

# Return a list of book ids associated with the given publisher. the publisher
# is fuzzy searched
def getBookIdsByPublisher(publisher):
    publisherIds = getPublisherIds(publisher)
    ret = []
    for p in publisherIds:
        r = getBookIdsByPublisherId(p)
        for n in r:
            ret.append(n)
    if ret == []:
        return {'error' : f'No books with publisher: {publisher}'}

    return ret

# Return a list of books given the publisher id
def getBookIdsByPublisherId(publisherId):
    bookIds = cmd(
        'SELECT id FROM Books WHERE publisherId == ?',
        [publisherId]
    )
    return [b[0] for b in bookIds]


# Do a fuzzy search on the list of publishers and return their ids
def getPublisherIds(publisher):
    pubIds = cmd(
        'SELECT id FROM Publishers WHERE publisher LIKE ?',
        [f'%{publisher}%']
    )
    return [p[0] for p in pubIds]

# Returns a list of book ids that the author has written
def getBookIdsFromAuthorId(authorId):
    bookIds = cmd(
        'SELECT bookId FROM Authors_Books WHERE authorId == ?',
        [authorId]
    )
    if type(bookIds) == str:
        return bookIds
    elif bookIds == []:
        name = getAuthorById(authorId)
        if name is not None:
            name = name['name']
        return {'error' : f'No books with author: {name}'}

    return [i[0] for i in bookIds]

def getAuthorsFromBookId(bookId):
    try:
        db = createOrGetDB()
        authors = db.execute(
            "SELECT authorId FROM Authors_Books WHERE bookId == ?",
            [bookId]
        ).fetchall()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    if len(authors) == 0:
        return None
    return parseAuthors(authors)

def getAuthorById(authorId):
    try:
        db = createOrGetDB()
        author = db.execute(
            "SELECT * FROM Authors WHERE id == ?",
            [authorId]
        ).fetchall()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    if len(author) != 1:
        return None
    return parseAuthor(author[0])


def addReview(textReview, rating, reviewer, bookID):
    idString = str(textReview) + str(rating) + str(reviewer) + str(bookID)
    reviewID = hashlib.md5(idString.encode()).hexdigest()
    try:
        db = createOrGetDB()
        db.execute("INSERT INTO Reviews (id,review,rating,reviewer,book) VALUES (?,?,?,?,?);",
            [
                reviewID,
                textReview,
                rating,
                reviewer,
                bookID

            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return True

def getReviewsFromBookId(bookId):
    try:
        db = createOrGetDB()
        reviews = db.execute(
            "SELECT * FROM Reviews WHERE book == ?",
            [bookId]
        ).fetchall()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    if len(reviews) == 0:
        return None
    return parseReviews(reviews)

def getCatagory(catId):
    try:
        db = createOrGetDB()
        cat = db.execute(
            "SELECT * FROM Catagorys WHERE id == ?",
            [catId]
        ).fetchall()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    if len(cat) != 1:
        return None
    return parseCatagory(cat[0])

def getAllCatagories():
    try:
        db = createOrGetDB()
        cat = db.execute(
            "SELECT * FROM Catagorys;"
        ).fetchall()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return [parseCatagory(c) for c in cat]


def parseReviews(row):
    ret = []
    for r in row:
        ret.append(parseReview(r))
    return ret

def parseReview(row):
    return {
        "id" : row[0],
        "text" : row[1],
        "rating" : row[2],
        "reviewerId" : row[3],
        "bookId" : row[4],
    }

def parseCatagory(row):
    return {
        "id" : row[0],
        "catagory" : row[1],
    }

def parseAuthors(authors):
    ret = []
    for a in authors:
        ret.append(getAuthorById(a[0]))
    return ret

def parseAuthor(row):
    return {
        "id" : row[0],
        "name" : row[1],
    }

def parseCollection(row):
    return {
        "id": row[0],
        "name": row[1],
        "user": row[2],
    }

def parseBook(row):
    return {
        "id":         extractBookId(row),
        "title":      row[1],
        "country":    row[2],
        "catagory":   getCatagory(row[3]),
        "keywords":   row[4],  # TODO change to list format
        "imageURL":   row[6],
        'description': row[7],
        "Authors" :   getAuthorsFromBookId(row[0]),
        "reviews" :   getReviewsFromBookId(row[0]),
        "publisherId" : extractPublisherId(row)
    }

# Extract book id from a row in the "Books" table
def extractBookId(row):
    return row[0]

# Extract publisher id from a row in the "Books" table
def extractPublisherId(row):
    return row[5]

def updateInfo(username, info, typeInfo):
    try:
        db = createOrGetDB()
        sql = "UPDATE Users set " + typeInfo + "= ? where username = ?"
        db.execute(sql,
            [
                info, username
            ]
        )
        db.commit()
    except sqlite3.cError as error:
        return error
    return True

def getInfo(username, typeInfo):
    try:
        db = createOrGetDB()
        sql = "SELECT " + typeInfo + " from Users WHERE username == ?"
        info = db.execute(sql,
            [
                username
            ]
        ).fetchall
        db.commit()
    except sqlite3.cError as error:
        return error
    return {
        str(typeInfo): info
    }

#a function to check out if a user "username" have marked the book "bookID" as readen
def ifUserReaden(username, bookID):
    userList =  getPersonRead(bookID)
    for user in userList:
        if username == user["username"]:
            return True
    return False

def getAccInfo(usernmae):
    try:
        db = createOrGetDB()
        sql = "SELECT * FROM Users WHERE username == ?"
        user = db.execute(sql,
            usernmae
        ).fetchall
        if len(user) != 1:
            return None
        user = user[0]
        sql = "SELECT Collections.name FROM Users JOIN Collections ON Users.username=Collections.user_created WHERE Users.username == ?"
        collections = db.execute(sql,
            usernmae
        ).fetchall
        db.commit()
    except sqlite3.cError as error:
        return error
    return {
        "username": user[0],
        "email": user[1],
        "self_Intro": user[6],
        "collections": collections,
    }

def getNRecentlyAddedFromCollection(collId, n=10):
    try:
        db = createOrGetDB()
        ret = db.execute('''
            SELECT *
            FROM Collections__Book
            INNER JOIN Books
            ON Books.id = Collections__Book.book_id
            WHERE Collections__Book.collections_id == ?
            ORDER BY Collections__Book.dateAdded DESC
            LIMIT ?
        ''', [collId, n]).fetchall()
        db.commit()
    except sqlite3.Error as error:
        return error
    if len(ret) == 0:
        return None
    return [parseBookColl(r) for r in ret]


def addBookRead(user_id, book_id):
    try:
        db = createOrGetDB()
        date = datetime.today().strftime('%Y-%m-%d')
        db.execute("INSERT INTO Books__Read (userId, bookId, dateAdded) VALUES (?,?,?);",
            [
                user_id,
                book_id,
                date,
            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return True

def removeBookRead(user_id, book_id):
    try:
        db = createOrGetDB()
        db.execute("DELETE FROM Books__Read WHERE  userId == ? AND bookId == ?",
            [
                user_id,
                book_id,
            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return True

def getBooksRead(user_id):
    try:
        db = createOrGetDB()
        data = db.execute("SELECT bookId, MAX(dateAdded) FROM Books__Read WHERE userId == ? GROUP BY bookId",
            [
                user_id,
            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return [
        {
            "bookId": val[0],
            "dateAdded": val[1],
        }
    for val in data]

def getPersonRead(book_id):
    try:
        db = createOrGetDB()
        data = db.execute("SELECT userId, MAX(dateAdded) FROM Books__Read WHERE bookId == ? GROUP BY userId",
            [
                book_id,
            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return [
        {
            "username": val[0],
            "dateAdded": val[1],
        }
    for val in data]

def getNumberOfReaders(book_id):
    try:
        db = createOrGetDB()
        data = db.execute("SELECT userId, MAX(dateAdded) FROM Books__Read WHERE bookId == ? GROUP BY userId",
            [
                book_id,
            ]
        )
        db.commit()
        results = data.fetchall()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return len(results)


def parseBookColl(row):
    return {
        'id' : row[1],
        'date_added' : row[2],
        'title' : row[4],
        'country' : row[5],
        'catagoryId' : row[6],
        'keywords' : row[7],
        'imageURL' : row[9],
        'description': row[10],
    }


#returns pandas dataframe
# we probably should have been doing this from the begining but i didnt know "read_sql_query" existed
def getUsersReviews(username):
    try:
        db = createOrGetDB()
        reviews = pd.read_sql_query("SELECT * FROM Reviews WHERE reviewer == ?", db, params=[username])
    except:
        abort(400, "database error")
        return None
    return reviews


def addGoal(user_id, book_id, dateToRead):
    try:
        db = createOrGetDB()
        date = datetime.today().strftime('%Y-%m-%d')
        db.execute("INSERT INTO goals (userId, bookId, dateToRead, dateAdded, complete) VALUES (?,?,?,?,?);",
            [
                user_id,
                book_id,
                dateToRead,
                date,
                0
            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return True

def complete_goal(user_id, book_id):
    try:
        db = createOrGetDB()
        db.execute('''UPDATE goals
                        SET complete=1
                        WHERE userId=? and bookId=?;''',
            [
                user_id,
                book_id,
            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return True

def clearGoal(user_id, book_id):
    try:
        db = createOrGetDB()
        db.execute("DELETE FROM goals WHERE  userId == ? AND bookId == ?",
            [
                user_id,
                book_id,
            ]
        )
        db.commit()
    except sqlite3.Error as error:
        abort(400, str(error))
        return error
    return True


def getGoals(username):
    try:
        db = createOrGetDB()
        goals = pd.read_sql_query('''
                SELECT * FROM goals
                INNER JOIN Books ON goals.bookId == books.id
                WHERE userId == ?''',
            db, params=[username])
    except:
        abort(400, "database error")
        return None
    goals['complete'] = goals['complete'].astype(bool)
    return json.loads(goals.to_json(orient='records'))

def most_read(limit):
    try:
        db = createOrGetDB()
        reviews = pd.read_sql_query('''
                SELECT * FROM Books__Read
                INNER JOIN Books ON Books__Read.bookId == books.id
                GROUP BY Books__Read.bookId
                ORDER BY COUNT(DISTINCT(Books__Read.userId)) Desc
                LIMIT ?''',
            db, params=[limit])
    except:
        abort(400, "database error")
        return None
    return json.loads(reviews.to_json(orient='records'))

def recently_read(limit):
    try:
        db = createOrGetDB()
        reviews = pd.read_sql_query('''
                SELECT * FROM Books__Read
                INNER JOIN Books ON Books__Read.bookId == books.id
                GROUP BY Books__Read.bookId
                ORDER BY Books__Read.dateAdded Desc
                LIMIT ?''',
            db, params=[limit])
    except:
        abort(400, "database error")
        return None
    return json.loads(reviews.to_json(orient='records'))
