#!/usr/bin/env python3

class Book():
    def __init__(self, title, pubId, pubDate, authorIds, cats, reviewIds, Id):

        self.__Id = Id
        self.__authorIds = authorIds
        self.__cats = cats
        self.__pubDate = pubDate
        self.__pubId = pubId
        self.__reviewIds = reviewIds


    def getId(self):
        return self.__Id

    def getAuthorIds(self):
        return self.__authorIds

    def getCats(self):
        return self.__cats

    def getPubDate(self):
        return self.__pubDate

    def getPubId(self):
        return self.__pubId

    def getReviewIds(self):
        return self.__reviewIds

