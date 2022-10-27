import DataBase as db
import numpy as np
import math
import pandas as pd
import os


# return all of a user's books and keywords
def get_user_all_books_keywords(username):
    collection_list = db.getCollectionsByUser(username)
    book_list = []
    for c in collection_list:
        temp = db.books_in_collection(c["id"])
        for t in temp:
            book_list.append({"id": t["id"], "keywords": t["keywords"]})
    return book_list


def Norm(list):
    norm = 0
    for i in list:
        norm += (i * i)
    return math.sqrt(norm)


def similarity_calculate(user_books_keywords_dic, book_keywords):
    molecule = 0
    for keyword in book_keywords:

        if keyword in user_books_keywords_dic.keys():
            molecule += user_books_keywords_dic[keyword]
    denominator = 0
    vector_user = user_books_keywords_dic.values()
    vector_book = []
    for keyword in book_keywords:
        vector_book.append(1)
    denominator = Norm(vector_book) * Norm(vector_user)
    #print(denominator)
    #denominator = np.linalg.norm(vector_user) * np.linalg.norm(vector_user)

    return molecule / denominator

def distance(target_books, books):
    union_len = len(set(target_books) & set(books))
    if union_len == 0:
        return 0.0
    product = len(target_books) * len(books)
    cosine = union_len / math.sqrt(product)
    return cosine


def get_user_all_books(username):
    collection_list = db.getCollectionsByUser(username)
    book_list = []
    if collection_list != None:
        for c in collection_list:
            temp = db.books_in_collection(c["id"])
            for t in temp:
                book_list.append(t["id"])
        return list(set(book_list))
    else:
        return None


def getBookIdList(row):
    bookId_list = []
    for t in row:
        bookId_list.append(t[0])
    return bookId_list


def mean_rating(bookId):
    reviews = db.getBook(bookId)["reviews"]

    total_rating = 0
    total_num = 0
    if reviews != None:
        for review in reviews:
            total_rating += int(review["rating"])
            total_num += 1
        return total_rating / total_num
    else:
        return 0


def get_top10_books_by_rating(book_Ids):
    book_ratings = {}
    for book in book_Ids:
        book_ratings[book] = mean_rating(book)

    return sorted(book_ratings.items(), key=lambda item: item[1],
                  reverse=True)[:10]

#===================================================================================
#The following functions are recommendation modes
#===================================================================================

# given a username, it will find all books in the user's collections
# calculate keyword distribution
# find the top 10 books that most similar with the user's taste
def getRecomendationByUserCollections(username):
    book_list = get_user_all_books_keywords(username)
    #print(book_list)
    #user vector
    #keywords_dic is just like {"A":2, "B":3, "C": 1}
    keywords_dic = {}
    similarity_dic = {}

    for book in book_list:
        keywords_temp = book["keywords"].split(" ")
        for t in keywords_temp:
            t = str(t)
            if t in keywords_dic.keys():
                keywords_dic[t] += 1
            else:
                keywords_dic[t] = 1

    all_books = db.getAllBooks()
    # deduplication
    user_books_id = []
    for b in book_list:
        user_books_id.append(b["id"])
    #print(user_books_id)
    num_books = len(all_books)
    i = 0
    while i < num_books:
        if all_books[i]["id"] in user_books_id:
            all_books.pop(i)
            i -= 1
            num_books -= 1
        i += 1

    #calculate similarity and store with bookId in dictionary
    for book in all_books:
        temp_keywords = book["keywords"].split(" ")  #temp_keywords is a list
        similarity_dic[str(book["id"])] = similarity_calculate(
            keywords_dic, temp_keywords)

    similarity_dic = sorted(similarity_dic.items(),
                            key=lambda item: item[1],
                            reverse=True)

    similarity_dic = similarity_dic[:10]

    l = getBookIdList(similarity_dic)
    return [db.getBook(str(x)) for x in l]


def getRecomendationForBookByBoookRating(bookId):

    ratings = db.getReviewsFromBookId(bookId)

    # Was a NoneType error here
    if ratings is None:
        return -1

    users_reviews = []

    for rating in ratings:
        df = db.getUsersReviews(rating["reviewerId"])
        df['super_rating'] = rating['rating']
        users_reviews += [df]

    reviews = pd.concat(users_reviews)
    reviews['points'] = reviews.apply(lambda row: (row['super_rating'] - 2.5) *
                                      (row['rating'] - 2.5),
                                      axis=1)
    reviews['points'] = reviews.groupby(['book'])['points'].transform('sum')

    l = reviews[reviews['book'] != bookId].sort_values(
        'points', ascending=False)['book'].unique()
    return [db.getBook(str(x)) for x in l]



# ------the author of bookId also write these books------
# given a bookId, it will find authors.
# then find all books written by those authors
# find the top 10 books by average rating
def getRecomendationForBookByBoookAuthor(bookId):
    authors = db.getAuthorsFromBookId(bookId)
    author_Ids = []
    try:
        for author in authors:
            author_Ids.append(author["id"])
        book_Ids = []
        for author in author_Ids:
            book_Ids.extend(db.getBookIdsFromAuthorId(author))

        book_Ids = list(set(book_Ids))
        book_Ids.remove(int(bookId))
        book_ratings = get_top10_books_by_rating(book_Ids)

        l = getBookIdList(book_ratings)
        return [db.getBook(str(x)) for x in l]
    except Exception:
        print("book " + str(bookId) + " has no author") 
    


# ------most popular books of the same category with bookId------
def getRecomendationForBookByBoookCategory(bookId):
    category = db.getBook(bookId)["catagory"]["id"]
    allBooks = db.getAllBooks()
    book_Ids = []
    for book in allBooks:
        if book["catagory"]["id"] == category:
            book_Ids.append(book["id"])
    book_Ids.remove(int(bookId))
    book_ratings = get_top10_books_by_rating(book_Ids)
    l = getBookIdList(book_ratings)
    return [db.getBook(str(x)) for x in l]





# ------users with similar taste are also reading these books------
# given a username, it will find the top 10 users with most similar collections
# return the top 10 most common books in these users collections
def getRecomendationForBookByOthersCollections(username):
    try:
        target_books = get_user_all_books(username)
        user_Collections_dic = {}
        Users = db.getAllUsers()
        for user in Users:
            if user[0] != username and get_user_all_books(user[0]) != None:
                user_Collections_dic[user[0]] = get_user_all_books(user[0])
        user_similarity_dic = {}
        for user in user_Collections_dic:
            user_similarity_dic[user] = distance(target_books,
                                                user_Collections_dic[user])
        user_similarity_dic = sorted(user_similarity_dic.items(),
                                    key=lambda item: item[1],
                                    reverse=True)[:10]
        bookId_list = {}
        for user in user_similarity_dic:
            for book in user_Collections_dic[user[0]]:

                if book not in bookId_list.keys():
                    bookId_list[book] = 1
                else:
                    bookId_list[book] += 1
        for book in target_books:
            if book in bookId_list.keys():
                bookId_list.pop(book)

        bookId_list = sorted(bookId_list.items(),
                            key=lambda item: item[1],
                            reverse=True)[:10]
        l = getBookIdList(bookId_list)
        return [db.getBook(str(x)) for x in l]
    except Exception:
        print("error occured when finding others collections") 


if __name__ == '__main__':
    #print(getRecomendationByUserCollections("111"))
    #print(getRecomendationForBookByBoookRating("1"))
    print(getRecomendationForBookByBoookAuthor("26"))
    #print(getRecomendationForBookByCategory("59"))
    #print(getRecomendationForBookByOthersCollections("111"))
