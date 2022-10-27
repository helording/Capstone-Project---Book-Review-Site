#!/usr/bin/env python3

class Review():
    def __init__(self, Id, text, rating, reviewerId, bookId):
        self.__Id = Id
        self.__text = text
        self.__rating = rating
        self.__reviewerId = reviewerId
        self.__bookId = bookId

    def getRating(self):
        return self.__rating

    def getReview(self):
        return self.__review

    def getReviewerId(self):
        return self.__reviewerId


