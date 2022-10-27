#!/usr/bin/env python3

import hashlib

class User():
    def __init__(self, u, p_hash):
        self.__username = u
        self.__phash = p_hash
        self.__email = ''
        self.__selfIntro = ''
        self.__goal = ''
        self.__collections = []
        self.__booksReadIds = []
        self.__goalStarted = None # Date type

    # Given a regular python3 string return its sha256 hash.
    # Returns an ascii string, not as effecient as bytes but alot easier to
    # copy/paste
    def __sha256(s):
        return hashlib.sha256(s.encode('UTF-8')).hexdigest()

    def isValidCreds(name, pword):
        if name != self.__username:
            return False

        if self.__sha256(pword) != self.__phash:
            return False

        return True

    def getName(self):
        return self.__username

    def getEmail(self):
        return self.__email

    def getSelfIntro(self):
        return self.__selfIntro


