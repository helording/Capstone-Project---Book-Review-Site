import sqlite3
import os
import requests
import json

import DataBase as db

current_host = 'http://127.0.0.1:81/'

API_LOGIN = current_host + '/login'
API_REGISTER = current_host + '/register'
API_ALLBOOKS = current_host + '/api/allBooks'
API_ADVBOOKSEARCH = current_host + '/api/advBookSearch'
API_BOOKS= current_host + '/api/books'
API_USERS = current_host + '/api/users'
API_RECENTLYADDEDBOOKS = current_host + '/api/recentlyAddedBooks/'
API_ADDBOOKTOCOLLECTION = current_host + '/collections/<id>/addBook'
API_DELETECOLLECTION = current_host + '/collections'

def setup_database():
    DATABASE_PATH = "./db"
    DATABASE_DATA = "./testdata.sql"
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

class RequestWrapper():

    def __init__(self):
        # Each test we refresh the data base
        setup_database()

        self.session = requests.Session()
        self.session.headers.update({"content-type":"application/json"})

    # Do a post request
    def post(self, url, data=None):
        return self.session.post(
            url,
            json=data
        )

    # Do a get request
    def get(self, url, data=None):
        return self.session.get(
            url,
            json=data
        )

    def setToken(self, d):
        self.session.headers.update(d)

class LoginTest(RequestWrapper):

    def run(self):
        print('### ' + API_LOGIN + ' ###')

        print('testing bad username and password')
        r = self.post(API_LOGIN, {"username":"asdf","password":"asdf"})
        assert('token' not in r.text)
        assert(r.status_code == 400)

        print('testing bad password')
        r = self.post(API_LOGIN, {"username":"jarrod","password":"asdf"})
        assert('token' not in r.text)
        assert(r.status_code == 400)

        print('testing bad username')
        r = self.post(API_LOGIN, {"username":"asdf","password":"jarrod"})
        assert('token' not in r.text)
        assert(r.status_code == 400)

        print('testing bad api request')
        r = self.post(API_LOGIN, {"dummyfield":"asdf"})
        assert('token' not in r.text)
        assert(r.status_code == 400)

        print('testing valid attempt')
        r = self.post(API_LOGIN, {"username":"jarrod","password":"jarrod"})
        assert('token' in r.text)
        assert(r.status_code == 200)

        print()


'''
normal creation
check login after creation
'''
class SignUpTest(RequestWrapper):

    def run(self):
        print('### ' + API_REGISTER + ' ###')
        u = 'new-username'
        p = 'new-password'

        print('test register empty username and password')
        r = self.post(API_REGISTER, {"username":"","password":""})
        assert('token' not in r.text)
        assert(r.status_code == 400)

        print('test register empty password')
        r = self.post(API_REGISTER, {"username":"asdf","password":""})
        assert('token' not in r.text)
        assert(r.status_code == 400)

        print('test register empty username')
        r = self.post(API_REGISTER, {"username":"","password":"asdf"})
        assert('token' not in r.text)
        assert(r.status_code == 400)

        print('test register invalid api request')
        r = self.post(API_REGISTER, {"aaa":"aaa"})
        assert('token' not in r.text)
        assert(r.status_code == 400)

        print('test register user already exists')
        r = self.post(API_REGISTER, {"username":"jarrod","password":"jarrod"})
        assert('token' not in r.text)
        assert(r.status_code == 400)

        print('test login user does not exist')
        r = self.post(API_LOGIN, {"username":u,"password":p})
        assert('token' not in r.text)
        assert(r.status_code == 400)

        print('test valid register api call')
        r = self.post(API_REGISTER, {"username":u,"password":p})
        assert('token' in r.text)
        assert(r.status_code == 200)

        print('test login user DOES exist')
        r = self.post(API_LOGIN, {"username":u,"password":p})
        assert('token' in r.text)
        assert(r.status_code == 200)

        print('test user has main collection')
        r = db.getCollectionsByUser(u)
        assert(len(r) == 1)
        assert(r[0]['name'] == 'main')

        print()

class allBooks(RequestWrapper):

    def run(self):
        print('### ' + API_ALLBOOKS + ' ###')

        print('Before authenticated')
        r = self.get(API_ALLBOOKS)
        assert('token' not in r.text)
        assert(r.status_code == 401)

        print('Log in as jarrod')
        r = self.post(API_LOGIN, {"username":'jarrod',"password":'jarrod'})
        assert('token' in r.text)
        assert(r.status_code == 200)

        self.setToken(json.loads(r.text))

        print('After authentication')
        r = self.get(API_ALLBOOKS)
        assert(r.status_code == 200)
        j = json.loads(r.text)

        print('first book')
        assert(j[0]['id'] == 1)
        assert(j[0]['title'] == 'title 1')
        assert(j[0]['country'] == 'country 1')
        assert(j[0]['catagory']['id'] == 1)
        assert(j[0]['catagory']['catagory'] == 'Arts and Music')

        print('second book')
        assert(j[1]['id'] == 2)
        assert(j[1]['title'] == 'title 2')
        assert(j[1]['country'] == 'country 2')
        assert(j[1]['catagory']['id'] == 2)
        assert(j[1]['catagory']['catagory'] == 'Biographies')

        print('third book')
        assert(j[2]['id'] == 3)
        assert(j[2]['title'] == 'title 3')
        assert(j[2]['country'] == 'country 3')
        assert(j[2]['catagory']['id'] == 3)
        assert(j[2]['catagory']['catagory'] == 'Business')

        print('fourth book')
        assert(j[3]['id'] == 4)
        assert(j[3]['title'] == 'title 4')
        assert(j[3]['country'] == 'country 4')
        assert(j[3]['catagory']['id'] == 4)
        assert(j[3]['catagory']['catagory'] == 'Comics')

        print('fifth book')
        assert(j[4]['id'] == 5)
        assert(j[4]['title'] == 'title 5')
        assert(j[4]['country'] == 'country 5')
        assert(j[4]['catagory']['id'] == 1)
        assert(j[4]['catagory']['catagory'] == 'Arts and Music')

        print()


class advBookSearchValid(RequestWrapper):

    def run(self):
        print('### ' + API_ADVBOOKSEARCH + ' (valid) ###')

        print('valid title')
        books = db.getBookAdvSearch({'Title' : 'le'})
        assert(len(books) == 16)
        for n, book in enumerate(books):
            assert(book['id'] == n+1)

        print('valid country')
        books = db.getBookAdvSearch({'Country' : 'ount'})
        assert(len(books) == 16)
        for n, book in enumerate(books):
            assert(book['id'] == n+1)

        print('valid catagoryId')
        books = db.getBookAdvSearch({'catagoryId' : '1'})
        assert(len(books) == 4)
        assert(books[0]['id'] == 1)
        assert(books[1]['id'] == 5)
        assert(books[2]['id'] == 9)

        print('valid author')
        books = db.getBookAdvSearch({'author' : ' 1'})
        assert(len(books) == 4)
        assert(books[0]['id'] == 4)
        assert(books[1]['id'] == 7)
        assert(books[2]['id'] == 8)
        assert(books[3]['id'] == 9)

        print('valid authorId')
        books = db.getBookAdvSearch({'authorId' : '7'})
        assert(len(books) == 3)
        assert(books[0]['id'] == 1)
        assert(books[1]['id'] == 3)
        assert(books[2]['id'] == 5)

        print('valid publisher')
        books = db.getBookAdvSearch({'publisher' : "ub 1"})
        assert(len(books) == 2)
        assert(books[0]['id'] == 1)
        assert(books[1]['id'] == 4)

        print('valid minRating')
        books = db.getBookAdvSearch({'minRating' : '1'})
        assert(len(books) == 2)
        assert(books[0]['id'] == 1)
        assert(books[1]['id'] == 2)

        print()

class advBookSearchInvalid(RequestWrapper):

    def run(self):
        print('### ' + API_ADVBOOKSEARCH + ' (invalid) ###')

        print('invalid dict (with bad fields)')
        books = db.getBookAdvSearch({'aaaa' : '1024'})
        assert(len(books) == 1)
        assert(books == {'error': 'Unkown search parameter: aaaa'})

        print('invalid dict (empty)')
        books = db.getBookAdvSearch({})
        assert(len(books) == 1)
        assert(books == {'error': 'Invalid search parameters'})

        print('invalid Title')
        books = db.getBookAdvSearch({'Title' : 'THIS DOES NOT EXIST!!!'})
        assert(len(books) == 1)
        assert(books == {'error': 'No books with title: THIS DOES NOT EXIST!!!'})

        print('invalid Country')
        books = db.getBookAdvSearch({'Country' : 'THIS DOES NOT EXIST'})
        assert(len(books) == 1)
        assert(books == {'error': 'No books with country: THIS DOES NOT EXIST'})

        print('invalid author')
        books = db.getBookAdvSearch({'author' : 'THIS DOES NOT EXIST'})
        assert(len(books) == 1)
        assert(books == {'error': 'Author does not exist: THIS DOES NOT EXIST'})

        print('invalid authorId (not writtent any books)')
        books = db.getBookAdvSearch({'authorId' : '8'})
        assert(len(books) == 1)
        assert(books == {'error': 'No books with author: Mr 8'})

        print('invalid authorId (author does not exist)')
        books = db.getBookAdvSearch({'authorId' : '-1'})
        assert(len(books) == 1)
        assert(books == {'error': 'No books with author: None'})

        print('invalid publisher')
        books = db.getBookAdvSearch({'publisher' : 'THIS DOES NOT EXIST'})
        assert(len(books) == 1)
        assert(books == {'error': 'No books with publisher: THIS DOES NOT EXIST'})

        print('invalid minRating (big num)')
        books = db.getBookAdvSearch({'minRating' : '69'})
        assert(len(books) == 1)
        assert(books == {'error': 'Rating is outside of valid range: 69'})

        print('invalid minRating (not num)')
        books = db.getBookAdvSearch({'minRating' : 'hello'})
        assert(len(books) == 1)
        assert(books == {'error': 'Rating is not a valid integer: hello'})

        print('invalid catagoryId (no books with catagory ID)')
        books = db.getBookAdvSearch({'catagoryId' : '5'})
        assert(len(books) == 1)
        assert(books == {'error': 'No books with catagoryId: pls dont touch'})

        print('invalid catagoryId (catagoryID does not exist)')
        books = db.getBookAdvSearch({'catagoryId' : '222'})
        assert(len(books) == 1)
        assert(books == {'error': 'No books with catagoryId: None'})

        print()

class advBookSearchCombine(RequestWrapper):

    def run(self):
        print('### ' + API_ADVBOOKSEARCH + ' (combine) ###')

        print('valid title + invalid minRating')
        books = db.getBookAdvSearch({'Title' : 'le', 'minRating' : '99'})
        assert(len(books) == 1)
        assert('error' in books)

        print('invalid Title + valid minRating')
        books = db.getBookAdvSearch({'Title' : 'asdflkjasdkfj', 'minRating' : '1'})
        assert(len(books) == 1)
        assert('error' in books)

        print('valid Title + valid Country')
        books = db.getBookAdvSearch({'Title' : 'le', 'Country' : '1'})
        assert(len(books) == 8)
        assert(books[0]['id'] == 1)
        assert(books[0]['title'] == 'title 1')
        assert(books[0]['country'] == 'country 1')
        assert(books[1]['id'] == 10)
        assert(books[1]['title'] == 'title 10')
        assert(books[1]['country'] == 'country 10')
        assert(books[2]['id'] == 11)
        assert(books[2]['title'] == 'title 11')
        assert(books[2]['country'] == 'country 11')
        assert(books[3]['id'] == 12)
        assert(books[3]['title'] == 'title 12')
        assert(books[3]['country'] == 'country 12')
        assert(books[4]['id'] == 13)
        assert(books[4]['title'] == 'title 13')
        assert(books[4]['country'] == 'country 13')
        assert(books[5]['id'] == 14)
        assert(books[5]['title'] == 'title 14')
        assert(books[5]['country'] == 'country 14')
        assert(books[6]['id'] == 15)
        assert(books[6]['title'] == 'title 15')
        assert(books[6]['country'] == 'country 15')
        assert(books[7]['id'] == 16)
        assert(books[7]['title'] == 'title 16')
        assert(books[7]['country'] == 'country 16')


        print('valid Title + valid catagoryId')
        books = db.getBookAdvSearch({'Title' : 'le', 'catagoryId' : '1'})
        assert(books[0]['id'] == 1)
        assert(books[0]['title'] == 'title 1')
        assert(books[0]['catagory']['id'] == 1)
        assert(books[1]['id'] == 5)
        assert(books[1]['title'] == 'title 5')
        assert(books[1]['catagory']['id'] == 1)
        assert(books[2]['id'] == 9)
        assert(books[2]['title'] == 'title 9')
        assert(books[2]['catagory']['id'] == 1)

        print('valid Title + valid author')
        books = db.getBookAdvSearch({'Title' : 'le', 'author' : '2'})
        assert(len(books) == 2)
        assert(books[0]['id'] == 4)
        assert(books[0]['title'] == 'title 4')
        assert(books[1]['id'] == 9)
        assert(books[1]['title'] == 'title 9')

        print('valid Title + valid authorId')
        books = db.getBookAdvSearch({'Title' : 'le', 'authorId' : '2'})
        assert(len(books) == 2)
        assert(books[0]['id'] == 4)
        assert(books[0]['title'] == 'title 4')
        assert(books[1]['id'] == 9)
        assert(books[1]['title'] == 'title 9')

        print('valid Title + valid publisher')
        books = db.getBookAdvSearch({'Title' : 'le', 'publisher' : '1'})
        assert(len(books) == 2)
        assert(books[0]['id'] == 1)
        assert(books[0]['title'] == 'title 1')
        assert(books[0]['publisherId'] == 1)
        assert(books[1]['id'] == 4)
        assert(books[1]['title'] == 'title 4')
        assert(books[1]['publisherId'] == 1)

        print('valid Title + valid publisher')
        books = db.getBookAdvSearch({'Title' : 'le', 'minRating' : '3'})
        assert(len(books) == 2)
        assert(books[0]['id'] == 1)
        assert(books[0]['title'] == 'title 1')
        assert(books[1]['id'] == 2)
        assert(books[1]['title'] == 'title 2')

        print()


class booksRead(RequestWrapper):

    def run(self):
        print('### (readBooksFunction) ###')

        print("Books Added ok")
        res = db.addBookRead("asdf", 1)
        assert(res == True)
        res = db.addBookRead("jarrod", 1)
        assert(res == True)
        res = db.addBookRead("asdf", 2)
        assert(res == True)
        res = db.addBookRead("jarrod", 2)
        assert(res == True)

        print("Added books are displayed")
        res = db.getBooksRead("asdf")
        assert(res[0]['bookId'] == 1)
        assert(res[1]['bookId'] == 2)
        res = db.getBooksRead("jarrod")
        assert(res[0]['bookId'] == 1)
        assert(res[1]['bookId'] == 2)

        print("Added users are displayed")
        res = db.getPersonRead(1)
        assert(res[0]['username'] == "asdf")
        assert(res[1]['username'] == "jarrod")
        res = db.getPersonRead(2)
        assert(res[0]['username'] == "asdf")
        assert(res[1]['username'] == "jarrod")

        print("Added books are displayed only once")
        res = db.getBooksRead("asdf")
        assert(len(res) < 3)
        res = db.getBooksRead("jarrod")
        assert(len(res) < 3)


        print("Added users are displayed only once")
        res = db.getPersonRead(1)
        assert(len(res) < 3)
        res = db.getPersonRead(2)
        assert(len(res) < 3)

        print("Books Removed ok")
        res = db.removeBookRead("asdf", 1)
        assert(res == True)
        res = db.removeBookRead("jarrod", 1)
        assert(res == True)
        res = db.removeBookRead("asdf", 2)
        assert(res == True)
        res = db.removeBookRead("jarrod", 2)
        assert(res == True)

        print("Added books are not displayed once removed")
        res = db.getBooksRead("asdf")
        assert(len(res) == 0)
        res = db.getBooksRead("jarrod")
        assert(len(res) == 0)


        print("Added Users are not displayed once removed")
        res = db.getPersonRead(2)
        assert(len(res) == 0)
        res = db.getPersonRead(2)
        assert(len(res) == 0)

        print()

class recentlyAddedBooksTest(RequestWrapper):

    def run(self):
        print('### ' + API_RECENTLYADDEDBOOKS + ' ###')

        print('book_id + imageURL')
        books = db.getNRecentlyAddedFromCollection(collId=1, n=10)
        assert(len(books) == 10)
        assert(books[0]['id'] == 5)
        assert(books[0]['imageURL'] == '/images/005.jpg')
        assert(books[1]['id'] == 6)
        assert(books[1]['imageURL'] == '/images/006.jpg')
        assert(books[2]['id'] == 8)
        assert(books[2]['imageURL'] == None)
        assert(books[3]['id'] == 12)
        assert(books[3]['imageURL'] == None)
        assert(books[4]['id'] == 3)
        assert(books[4]['imageURL'] == '/images/003.jpg')
        assert(books[5]['id'] == 7)
        assert(books[5]['imageURL'] == None)
        assert(books[6]['id'] == 11)
        assert(books[6]['imageURL'] == None)
        assert(books[7]['id'] == 4)
        assert(books[7]['imageURL'] == '/images/004.jpg')
        assert(books[8]['id'] == 2)
        assert(books[8]['imageURL'] == '/images/002.jpg')
        assert(books[9]['id'] == 10)
        assert(books[9]['imageURL'] == None)

        print()

class addBookToCollectionTest(RequestWrapper):

    def run(self):
        print('### ' + API_ADDBOOKTOCOLLECTION + ' ###')

        print('getting a collection')
        c = db.getCollection(2)
        assert(c['id'] == '2')
        assert(c['name'] == 'main')
        assert(c['user'] == 'alex')

        print('getting books from collection')
        b = db.books_in_collection(2)
        assert(len(b) == 3)
        assert(b[0]['id'] == 1)
        assert(b[0]['title'] == 'title 1')
        assert(b[1]['id'] == 2)
        assert(b[1]['title'] == 'title 2')
        assert(b[2]['id'] == 3)
        assert(b[2]['title'] == 'title 3')

        print('Adding unique book to a collection')
        db.addBookToCollection(collection_id=2, book_id=10)
        b = db.books_in_collection(2)
        assert(len(b) == 4)
        assert(b[0]['id'] == 1)
        assert(b[0]['title'] == 'title 1')
        assert(b[1]['id'] == 2)
        assert(b[1]['title'] == 'title 2')
        assert(b[2]['id'] == 3)
        assert(b[2]['title'] == 'title 3')
        assert(b[3]['id'] == 10)
        assert(b[3]['title'] == 'title 10')

        print('Adding duplicate book to a collection')
        db.addBookToCollection(collection_id=2, book_id=10)
        b = db.books_in_collection(2)
        assert(len(b) == 4)
        assert(b[0]['id'] == 1)
        assert(b[0]['title'] == 'title 1')
        assert(b[1]['id'] == 2)
        assert(b[1]['title'] == 'title 2')
        assert(b[2]['id'] == 3)
        assert(b[2]['title'] == 'title 3')
        assert(b[3]['id'] == 10)
        assert(b[3]['title'] == 'title 10')

        print()

class deleteCollectionTest(RequestWrapper):

    def run(self):
        print('### ' + API_DELETECOLLECTION + ' (delete) ###')

        print('Check collection exists')
        c = db.getCollection(2)
        assert(c['id'] == '2')
        assert(c['name'] == 'main')
        assert(c['user'] == 'alex')

        print('getting books from collection')
        b = db.books_in_collection(2)
        assert(len(b) == 3)
        assert(b[0]['id'] == 1)
        assert(b[0]['title'] == 'title 1')
        assert(b[1]['id'] == 2)
        assert(b[1]['title'] == 'title 2')
        assert(b[2]['id'] == 3)
        assert(b[2]['title'] == 'title 3')

        print('Delete collection')
        ret = db.deleteCollection(2)

        print('Check collection does not exist')
        c = db.getCollection(2)
        assert(c == None)

        print('Check no books are linked to collection')
        b = db.books_in_collection(2)
        assert(b == [])

        print()

class getLeadersTest(RequestWrapper):

    def run(self):
        print('### (get leaders) ###')

        print('Get leaders for jarrod')
        l = db.getLeaders('jarrod')
        assert(len(l) == 1)
        assert(l[0]['username'] == 'user')

        print('Get leaders for user')
        l = db.getLeaders('user')
        assert(len(l) == 1)
        assert(l[0]['username'] == 'jarrod')

        print('get leaders for alex')
        l = db.getLeaders('alex')
        assert(len(l) == 2)
        assert(l[0]['username'] == 'jarrod')
        assert(l[1]['username'] == 'user')

        print('get leaders for john')
        l = db.getLeaders('john')
        assert(len(l) == 0)

        print()

class getFollowersTest(RequestWrapper):

    def run(self):
        print('### (get followers) ###')

        print('Get followers for jarrod')
        f = db.getFollowers('jarrod')
        assert(len(f) == 3)
        assert(f[0]['username'] == 'user')
        assert(f[1]['username'] == 'alex')
        assert(f[2]['username'] == 'steve')

        print('Get followers for user')
        f = db.getFollowers('user')
        assert(len(f) == 3)
        assert(f[0]['username'] == 'jarrod')
        assert(f[1]['username'] == 'steve')
        assert(f[2]['username'] == 'alex')

        print('get followers for alex')
        f = db.getFollowers('alex')
        assert(len(f) == 0)

        print('get followers for john')
        f = db.getFollowers('john')
        assert(len(f) == 0)

        print()

class followUserTest(RequestWrapper):

    def run(self):
        print('### (followe a user) ###')

        print('Get followers')
        f = db.getFollowers('jarrod')
        assert(len(f) == 3)
        assert(f[0]['username'] == 'user')
        assert(f[1]['username'] == 'alex')

        print('Follow user')
        db.followLeader('jarrod', 'john')
        f = db.getFollowers('jarrod')
        assert(len(f) == 4)
        assert(f[0]['username'] == 'user')
        assert(f[1]['username'] == 'alex')
        assert(f[2]['username'] == 'steve')
        assert(f[3]['username'] == 'john')

        print('Follow same user again')
        db.followLeader('jarrod', 'john')
        f = db.getFollowers('jarrod')
        assert(len(f) == 4)
        assert(f[0]['username'] == 'user')
        assert(f[1]['username'] == 'alex')
        assert(f[2]['username'] == 'steve')
        assert(f[3]['username'] == 'john')

        print('Follow self')
        db.followLeader('jarrod', 'jarrod')
        f = db.getFollowers('jarrod')
        assert(len(f) == 4)
        assert(f[0]['username'] == 'user')
        assert(f[1]['username'] == 'alex')
        assert(f[2]['username'] == 'steve')
        assert(f[3]['username'] == 'john')

        print()

class unfollowUserTest(RequestWrapper):

    def run(self):

        print('### (unfollow a user) ###')

        print('Get followers')
        f = db.getFollowers('jarrod')
        assert(len(f) == 3)
        assert(f[0]['username'] == 'user')
        assert(f[1]['username'] == 'alex')
        assert(f[2]['username'] == 'steve')

        print('Unfollow user')
        db.unfollowLeader('jarrod', 'alex')
        f = db.getFollowers('jarrod')
        assert(len(f) == 2)
        assert(f[0]['username'] == 'user')
        assert(f[1]['username'] == 'steve')

        print('Unfollow user that you are not following')
        db.unfollowLeader('jarrod', 'alex')
        f = db.getFollowers('jarrod')
        assert(len(f) == 2)
        assert(f[0]['username'] == 'user')
        assert(f[1]['username'] == 'steve')

        print('Unfollow self')
        db.unfollowLeader('jarrod', 'jarrod')
        f = db.getFollowers('jarrod')
        assert(len(f) == 2)
        assert(f[0]['username'] == 'user')
        assert(f[1]['username'] == 'steve')

        print()

class getEventsTest(RequestWrapper):

    def run(self):
        print('### (getEvents) ###')

        print('events for alex')
        events = db.getEventsForUser('alex')
        assert(len('alex') == 4)
        assert(events[0]['leader'] == 'jarrod')
        assert(events[0]['type'] == 'read')
        assert(events[0]['book']['id'] == 1)
        assert(events[0]['date'] == '1999-01-02 01:01:01')
        assert(events[1]['leader'] == 'jarrod')
        assert(events[1]['type'] == 'read')
        assert(events[1]['book']['id'] == 2)
        assert(events[1]['date'] == '1999-01-03 01:01:01')
        assert(events[2]['leader'] == 'jarrod')
        assert(events[2]['type'] == 'done')
        assert(events[2]['book']['id'] == 1)
        assert(events[2]['date'] == '1999-01-04 01:01:01')
        assert(events[3]['leader'] == 'jarrod')
        assert(events[3]['type'] == 'read')
        assert(events[3]['book']['id'] == 3)
        assert(events[3]['date'] == '1999-01-05 01:01:01')

        print('events for steve')
        events = db.getEventsForUser('steve')
        assert(len('steve') == 5)
        assert(events[0]["leader"] == "jarrod")
        assert(events[0]["type"] == "read")
        assert(events[0]["book"]["id"] == 1)
        assert(events[0]["date"] == "1999-01-02 01:01:01")
        assert(events[1]["leader"] == "jarrod")
        assert(events[1]["type"] == "read")
        assert(events[1]["book"]["id"] == 2)
        assert(events[1]["date"] == "1999-01-03 01:01:01")
        assert(events[2]["leader"] == "jarrod")
        assert(events[2]["type"] == "done")
        assert(events[2]["book"]["id"] == 1)
        assert(events[2]["date"] == "1999-01-04 01:01:01")
        assert(events[3]["leader"] == "jarrod")
        assert(events[3]["type"] == "read")
        assert(events[3]["book"]["id"] == 3)
        assert(events[3]["date"] == "1999-01-05 01:01:01")
        assert(events[4]["leader"] == "user")
        assert(events[4]["type"] == "read")
        assert(events[4]["book"]["id"] == 4)
        assert(events[4]["date"] == "1999-01-06 01:01:01")

        print()


class leaderReadsBookTest(RequestWrapper):

    def run(self):
        print('### (leaderReadsBook) ###')

        print('check jarrod')
        events = db.getEventsForUser('jarrod')
        assert(len(events) == 1)
        assert(events[0]['leader'] == 'user')
        assert(events[0]['type'] == 'read')
        assert(events[0]['book']['id'] == 4)

        print('check user reads a book')
        db.addEventReadingBook('user', 9)
        events = db.getEventsForUser('jarrod')
        assert(len(events) == 2)
        assert(events[0]['leader'] == 'user')
        assert(events[0]['type'] == 'read')
        assert(events[0]['book']['id'] == 4)
        assert(events[1]['leader'] == 'user')
        assert(events[1]['type'] == 'read')
        assert(events[1]['book']['id'] == 9)

        print('check user is done with a book')
        db.addEventDoneBook('user', 4)
        events = db.getEventsForUser('jarrod')
        assert(len(events) == 3)
        assert(events[0]['leader'] == 'user')
        assert(events[0]['type'] == 'read')
        assert(events[0]['book']['id'] == 4)
        assert(events[1]['leader'] == 'user')
        assert(events[1]['type'] == 'read')
        assert(events[1]['book']['id'] == 9)
        assert(events[2]['leader'] == 'user')
        assert(events[2]['type'] == 'done')
        assert(events[2]['book']['id'] == 4)

        print()

class getEventByEventIdTest(RequestWrapper):

    def run(self):
        print('### (getEventByEventIdTest) ###')

        print('check get event by id: 1')
        e = db.getEventByEventId('1')
        assert(e['leader'] == 'user')
        assert(e['type'] == 'read')
        assert(e['eventId'] == '1')
        assert(e['book']['id'] == 4)

        print('check get event by id: 5')
        e = db.getEventByEventId('5')
        assert(e['leader'] == 'jarrod')
        assert(e['type'] == 'read')
        assert(e['eventId'] == '5')
        assert(e['book']['id'] == 2)

        print()

class deleteEventByEventIdTest(RequestWrapper):

    def run(self):
        print('### (deleteEventByEventId) ###')

        print('check get event by id: 3')
        e = db.getEventByEventId('3')
        assert(e['leader'] == 'jarrod')
        assert(e['type'] == 'read')
        assert(e['eventId'] == '3')
        assert(e['book']['id'] == 3)

        print('delete event id: 3')
        db.deleteEventByEventId('3')

        print('check get event by id, after being deleted: 3')
        e = db.getEventByEventId('3')
        assert('error' in e)

        print()

if __name__ == '__main__':

    lt = LoginTest()
    lt.run()

    su = SignUpTest()
    su.run()

    ab = allBooks()
    ab.run()

    absv = advBookSearchValid()
    absv.run()

    absi = advBookSearchInvalid()
    absi.run()

    absc = advBookSearchCombine()
    absc.run()

    br = booksRead()
    br.run()

    rabt = recentlyAddedBooksTest()
    rabt.run()

    abtct = addBookToCollectionTest()
    abtct.run()

    dct = deleteCollectionTest()
    dct.run()

    glt = getLeadersTest()
    glt.run()

    gft = getFollowersTest()
    gft.run()

    fut = followUserTest()
    fut.run()

    uut = unfollowUserTest()
    uut.run()

    get = getEventsTest()
    get.run()

    lrbt = leaderReadsBookTest()
    lrbt.run()

    gebeit = getEventByEventIdTest()
    gebeit.run()

    debeit = deleteEventByEventIdTest()
    debeit.run()
