from flask import Flask, abort, request, render_template
from flask_restplus import Resource, Api, reqparse
from User import *
from Review import *
from Book import *
import DataBase as db
import Recommend as rec
import sqlite3
import auth
import json

bookParser = reqparse.RequestParser()
bookParser.add_argument('title', type=str, help='Title of the book', required=True)
bookParser.add_argument('author', type=str, help='Author of the book', required=True)
bookParser.add_argument('country', type=str, help='Country the book was written in', required=True)
bookParser.add_argument('genre', type=str, help='Genera of the book', required=True) # TODO change to list format
bookParser.add_argument('keywords', type=str, help='keywords of the book', required=True) # TODO change to list format
bookParser.add_argument('imageURL', type=str, help='keywords of the book', required=False)
bookParser.add_argument('description', type=str, help='keywords of the book', required=False)


app = Flask(__name__)
api = Api(app)

# routes for rendering html pages
@app.route('/index',methods=['GET'])
def index():
    return render_template ("Index.html")

@app.route('/SignUp', methods=['GET', 'POST'])
def SignUp():
    return render_template ("SignUp.html")

@app.route('/Login', methods=['GET', 'POST'])
def UserLogin():
    return render_template ("Login.html")

@app.route('/userHome', methods=['GET', 'POST'])
def userHome():
    return render_template ("userHome.html")

@app.route('/createCollection', methods=['GET', 'POST'])
def createCollection():
    return render_template ("createCollection.html")

@app.route('/UserCollections', methods=['GET', 'POST'])
def UserCollections():
    return render_template ("Collections.html")

@app.route('/Collection/', methods=['GET', 'POST'])
def Collection():
    return render_template ("Collection.html")

@app.route('/OtherUsersCollection', methods=['GET', 'POST'])
def OtherUsersCollection():
    return render_template ("OtherUsersCollection.html")

@app.route('/Collection/addBookToCollection', methods=['GET', 'POST'])
def addBookToCollection():
    return render_template ("AddBookToCollection.html")

@app.route('/Collection/RemoveBookFromCollection', methods=['GET', 'POST'])
def RemoveBookFromCollection():
    return render_template ("RemoveBookFromCollection.html")

@app.route('/ViewAllBooks', methods=['GET', 'POST'])
def viewAllBooks():
    return render_template ("ViewAllBooks.html")

@app.route('/Book', methods=['GET', 'POST'])
def Book():
    return render_template ("Book.html")

@app.route('/AddReview', methods=['GET', 'POST'])
def AddReview():
    return render_template ("AddReview.html")

@app.route('/BookSearch', methods=['GET', 'POST'])
def BookSearch():
    return render_template ("BookSearch.html")

@app.route('/UserColSearch', methods=['GET', 'POST'])
def UserColSearch():
    return render_template ("UserColSearch.html")

@app.route('/editUserInfo', methods=['GET', 'POST'])
def editUserInfo():
    return render_template ("editUserInfo.html")

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    return render_template ("recommend.html")

@app.route('/social', methods=['GET', 'POST'])
def social():
    return render_template ("social.html")

@app.route('/addALeader', methods=['GET', 'POST'])
def addALeader():
    return render_template ("addALeader.html")

@app.route('/usersPage', methods=['GET', 'POST'])
def usersPage():
    return render_template ("otherUsersPage.html")

@app.route('/createEvent', methods=['GET', 'POST'])
def createEvent():
    return render_template ("addEvent.html")

@app.route('/finished', methods=['GET'])
def finishedGoal():
    return render_template ("finished.html")


@api.route('/api/allBooks')
class AllBooks(Resource):

    @auth.authenticate(request)
    def get(self, user):
        return db.getAllBooks()

@api.route('/api/advBookSearch')
class AdvBookSearch(Resource):

    @auth.authenticate(request)
    def post(self, user):
        # TODO This is for the front end guys, use this how ever you
        # want. Read the comments above this function to know how it works.
        # NOTE: You need to pass in a dictionary, let me (jarrod) know if/how
        # you want it changed.
        #
        # I know the db.getBookAdvSearch() works, but i can not get the swagger
        # thing to work
        return db.getBookAdvSearch(request.args)


@api.route('/books')
class Books(Resource):

    @auth.authenticate(request)
    def get(self, user):
        if("title" not in request.args.keys()):
                abort(400, "no query present")
        return db.find_books(request.args['title'])


@api.route('/books/<id>')
@api.doc(params={'id': 'unique book id'})
class Books(Resource):

    @auth.authenticate(request)
    def get(self, id, user):
        userList = db.getPersonRead(id)
        return {"info": db.getBook(id), "readen": db.ifUserReaden(user['username'], id), "size" : len(userList) }

    @auth.authenticate(request)
    def delete(self, id):
        deleted = db.deleteBook(id)
        if(deleted != True):
            abort(400, str(deleted))


@api.route('/books/add')
class BooksUpload(Resource):

    @auth.authenticate(request)
    def post(self, user):
        args = bookParser.parse_args()
        resp = db.addBook(args)
        if(isinstance(resp, sqlite3.Error)):
            abort(400, str(resp))
        return resp

    # may want add update exclusive endpoint here if we have time

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, help='Username of user', required=True)
user_parser.add_argument('password', type=str, help='Password of user', required=True)


@api.route('/login')
class Login(Resource):

    @api.doc(params={'username': 'User\'s user name', 'password': 'password'})
    def post(self):
        args = user_parser.parse_args()
        token = auth.login(args['username'], args['password'])
        main_collection_message = "collection cannot be created"
        try:
            ret = db.addCollection('main', args['username'])
            main_collection_message = "main collection with with id {} has been made".format(ret)
        except:
            main_collection_message = "collection already exists"
        return {
            "token": str(token),
            "main_collection_message": main_collection_message
        }


@api.route('/register')
class Regester(Resource):

    def post(self):
        args = user_parser.parse_args()
        token = auth.registerAccount(args['username'], args['password'])
        main_collection_message = "collection cannot be created"
        try:
            ret = db.addCollection('main', args['username'])
            main_collection_message = "main collection with with id {} has been made".format(ret)
        except:
            main_collection_message = "collection already exists"
        return {
            "token": str(token),
            "main_collection_message": main_collection_message
        }

@api.route('/logout')
class Login(Resource):

    @auth.authenticate(request)
    def post(self, user):
        auth.logout(user['username'])
        return {"message": "success"}


@api.route('/collections/<id>')
class collections(Resource):

    @auth.authenticate(request)
    def get(self, id, user):
        return {
            "collection": db.getCollection(id),
            "books": db.books_in_collection(id)
        }

@api.route('/userscollections/<name>')
class collections(Resource):

    @auth.authenticate(request)
    def get(self, name, user):
        return {
            "collections": db.getCollectionsByUser(name),
        }


collections__book_parser = reqparse.RequestParser()
collections__book_parser.add_argument('book_id', type=str, help='id of the book you want to add to the collection', required=True)

@api.route('/collections/<id>/addBook')
class collections(Resource):

    @auth.authenticate(request)
    def post(self, id, user):
        args = collections__book_parser.parse_args()
        db.addBookToCollection(id, args['book_id'])
        return {"message": "addition_succesful"}

@api.route('/collections/<colID>/<bookID>/removeBook')
class collections(Resource):

    @auth.authenticate(request)
    def post(self, colID, bookID, user):
        db.rmBookFromCollection(colID, bookID)
        return {"message": "removal_successful"}


collections_parser = reqparse.RequestParser()
collections_parser.add_argument('name', type=str, help='name of collection', required=True)
collections_parser.add_argument('colId', type=str, help='id of collection', required=False)


@api.route('/collections')
class collections(Resource):

    @auth.authenticate(request)
    def post(self, user):
        args = collections_parser.parse_args()
        col_id = db.addCollection(args['name'], user['username'])
        return {"id": col_id}

    @auth.authenticate(request)
    def delete(self, user):
        args = collections_parser.parse_args()
        return db.deleteCollection(args['colId'])

    @auth.authenticate(request)
    def get(self, user):
        if("name" not in request.args.keys()):
                abort(400, "no query present")
        return db.findCollections(request.args['name'])

# collId -> id of collection
@api.route('/api/recentlyAddedBooks/<collId>')
class RecentlyAddedBooks(Resource):

    @auth.authenticate(request)
    def get(self, collId, user):
        # We always get 10 since the spec says only 10
        return db.getNRecentlyAddedFromCollection(collId, 10)


info_parser = reqparse.RequestParser()
info_parser.add_argument('info', type=str, help='Intro of user', required=True)

@api.route('/myaccount')
class UpdateInfo(Resource):
    @auth.authenticate(request)
    def post(self, user):
        args = info_parser.parse_args()
        return db.updateInfo(user['username'], args['info'], "selfInfo")

    @auth.authenticate(request)
    def get(self, user):
        return db.getUserAll(user['username'])


review_parser = reqparse.RequestParser()
review_parser.add_argument('textReview', type=str, help='text review part of review', required=True)
review_parser.add_argument('rating', type=str, help='str from 1 to 5', required=True)


@api.route('/addReview/<id>')
class AddReview(Resource):

    @auth.authenticate(request)
    def post(self, id, user):
        args = review_parser.parse_args()
        db.addReview(args['textReview'], args['rating'], user['username'], id)
        return {"message": "addition_succesful"}

@api.route('/api/books/<id>/read')
class readBook(Resource):

# add a user to a books read list/counter
    @auth.authenticate(request)
    def post(self, id, user):
        return {
            "itemAdded": db.addBookRead(user['username'], id)
        }
# remove a user from a books read list/counter
    @auth.authenticate(request)
    def delete(self, id, user):
        return {
            "itemDeleted": db.removeBookRead(user['username'], id)
        }

# Get the books a user has read
@api.route('/api/books/<id>/readers')
class bookReaders(Resource):

    @auth.authenticate(request)
    def get(self, id, user):
        return db.getPersonRead(id)

# Get the users who have read a book
@api.route('/api/users/<id>/booksRead')
class booksRead(Resource):

    @auth.authenticate(request)
    def get(self, id, user):
        return db.getBooksRead(id)

search_parser = reqparse.RequestParser()
search_parser.add_argument('Title', type=str, help='title field', required=True)
search_parser.add_argument('Country', type=str, help='country of book', required=True)
search_parser.add_argument('catagoryId', type=str, help='category of book', required=True)
search_parser.add_argument('author', type=str, help='author of book', required=True)
search_parser.add_argument('publisher', type=str, help='publisher of book', required=True)
search_parser.add_argument('min_rate', type=str, help='minimal rating of book', required=True)


@api.route('/Search')
class Search(Resource):

    @auth.authenticate(request)
    def post(self, user):
        args = search_parser.parse_args()
        criteria = {}
        if (args['Title']):
            criteria['Title'] = args['Title']
        if (args['Country']):
            criteria['Country'] = args['Country']
        if (args['catagoryId']):
            criteria['catagoryId'] = int(args['catagoryId'])
        if (args['author']):
            criteria['author'] = args['author']
        if (args['publisher']):
            criteria['publisher'] = args['publisher']
        if (args['min_rate']):
            criteria['minRating'] = int(args['min_rate'])
        print(criteria)
        return db.getBookAdvSearch(criteria)

@api.route('/getCategories')
class getCategories(Resource):

    @auth.authenticate(request)
    def get(self, user):
        return db.getAllCatagories()

@api.route('/getReadCount/<bookID>')
class getReadCount(Resource):

    @auth.authenticate(request)
    def get(self, bookID, user):
        return db.getNumberOfReaders(bookID)

@api.route('/recommend/rating/<bookID>')
class getBookRecommend(Resource):

    @auth.authenticate(request)
    def get(self, bookID, user):
        print(bookID)
        return {"books": rec.getRecomendationForBookByBoookRating(bookID)}

@api.route('/recommend/author/<bookID>')
class getBookRecommend1(Resource):

    @auth.authenticate(request)
    def get(self, bookID, user):
        print(bookID)
        return {"books": rec.getRecomendationForBookByBoookAuthor(int(bookID))}

@api.route('/recommend/category/<bookID>')
class getBookRecommend2(Resource):

    @auth.authenticate(request)
    def get(self, bookID, user):
        print(bookID)
        return {"books": rec.getRecomendationForBookByBoookCategory(int(bookID))}

@api.route('/recommend/otherReaders')
class getOthersRecommend(Resource):

    @auth.authenticate(request)
    def get(self, user):
        return {"books": rec.getRecomendationForBookByOthersCollections(user['username'])}

@api.route('/recommend/keywords')
class getUserRecommend(Resource):

    @auth.authenticate(request)
    def get(self, user):
        return {"books": rec.getRecomendationByUserCollections(user['username'])}


goal_parser = reqparse.RequestParser()
goal_parser.add_argument('dateToRead', type=str, help='text review part of review', required=True)

@api.route('/api/books/<id>/<date>/goal')
class readBook(Resource):

# add a user to a books read list/counter
    @auth.authenticate(request)
    def post(self, id, date, user):
        return {
            "itemAdded": db.addGoal(user['username'], id, date)
        }

@api.route('/api/books/<id>/goal')
class goals(Resource):
# remove a user from a books read list/counter
    @auth.authenticate(request)
    def delete(self, id, user):
        return {
            "itemDeleted": db.clearGoal(user['username'], id)
        }

@api.route('/api/books/<id>/completeGoal')
class goals(Resource):
# remove a user from a books read list/counter
    @auth.authenticate(request)
    def post(self, id, user):
        return {
            "itemCompleted": db.complete_goal(user['username'], id)
        }

@api.route('/api/me/goals')
class goals(Resource):

# add a user to a books read list/counter
    @auth.authenticate(request)
    def get(self, user):
        return db.getGoals(user['username'])


@api.route('/api/books/mostRead/<limit>')
class mostRead(Resource):

# add a user to a books read list/counter
    @auth.authenticate(request)
    def get(self, limit, user):
        return db.most_read(limit)

@api.route('/api/books/recentlyRead/<limit>')
class recentlyRead(Resource):

# add a user to a books read list/counter
    @auth.authenticate(request)
    def get(self, limit, user):
        return db.recently_read(limit)


@api.route('/getFollowers')
class followers(Resource):

    # Returns a list of users that are following the user
    @auth.authenticate(request)
    def get(self, user):
        return db.getFollowers(user['username'])

@api.route('/getLeaders')
class leader(Resource):

    # Returns a list of users that the user  is following
    @auth.authenticate(request)
    def get(self, user):
        return db.getLeaders(user['username'])


@api.route('/addLeader/<leaderName>')
class leader(Resource):

    # add a leader to the users account
    @auth.authenticate(request)
    def post(self, leaderName, user):
        return db.followLeader(leaderName, user['username'])

    @auth.authenticate(request)
    def get(self, leaderName, user):
        return db.isFollowing(leaderName, user['username'])

@api.route('/unfollow/<leaderName>')
class unfollow(Resource):

    # add a leader to the users account
    @auth.authenticate(request)
    def post(self, leaderName, user):
        return db.unfollowLeader(leaderName, user['username'])

@api.route('/createEvent/<eventType>/<BookID>/<date>')
class event(Resource):

    # create event
    @auth.authenticate(request)
    def post(self, eventType, BookID, date, user):
        return db.addEventToTable(user['username'], eventType, BookID, date)

@api.route('/getEventsForUser')
class event(Resource):

    # get events from users leaders
    @auth.authenticate(request)
    def get(self, user):
        return db.getEventsForUser(user['username'])

@api.route('/getEventsByUser')
class event(Resource):

    # get events that user has created
    @auth.authenticate(request)
    def get(self, user):
        return db.getEventsFromUser(user['username'])

@api.route('/getEventsByOtherUser/<username>')
class event(Resource):

    # get events that another user has created
    @auth.authenticate(request)
    def get(self, username, user):
        return db.getEventsFromUser(username)

@api.route('/completeEvent/<eventId>')
class event(Resource):

    # complete event
    @auth.authenticate(request)
    def post(self, eventId, user):
        return db.deleteEventByEventId(eventId)


@api.route('/getUser/<username>')
class user(Resource):

    # finds if a user exists given a username
    @auth.authenticate(request)
    def get(self, username, user):
        return db.getUser(username)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
