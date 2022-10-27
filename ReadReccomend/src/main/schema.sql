CREATE TABLE IF NOT EXISTS Books (
  id SERIAL PRIMARY KEY NOT NULL,
  Title TEXT default NULL,
  Country varchar(100) default NULL,
  catagoryId INT NOT NULL REFERENCES Catagorys(id),
  Keywords TEXT default NULL,
  publisherId SERIAL REFERENCES Publishers(id),
  image_url TEXT default NULL,
  description TEXT default NULL
);

-- I don't know if there is a better way to do enums in sql
CREATE TABLE IF NOT EXISTS Catagorys (
  id SERIAL PRIMARY KEY NOT NULL,
  catagory varchar(255) default NULL
);

CREATE TABLE IF NOT EXISTS Publishers (
  id SERIAL PRIMARY KEY NOT NULL,
  publisher varchar(255) default NULL
);

CREATE TABLE IF NOT EXISTS Authors (
  id SERIAL PRIMARY KEY NOT NULL,
  name varchar(255) default NULL
);

-- joining table for authors and books due to M:M relationship
CREATE TABLE IF NOT EXISTS Authors_Books (
  authorId INT NOT NULL REFERENCES Authors (id),
  bookId INT NOT NULL REFERENCES Books (id)
);

CREATE TABLE IF NOT EXISTS Reviews (
  id SERIAL PRIMARY KEY NOT NULL,
  review varchar(255) NOT NULL,
  rating INTEGER CHECK(0 <= rating AND rating <= 5),
  reviewer TEXT REFERENCES Users(id), -- Person who did the review
  book SERIAL REFERENCES Books(id)    -- Book being reviewd
);

CREATE TABLE IF NOT EXISTS Users (
  username TEXT PRIMARY KEY NOT NULL,
  Pass TEXT NOT NULL,
  selfInfo TEXT default NULL
);

CREATE TABLE IF NOT EXISTS Followers (
  leaderId TEXT NOT NULL REFERENCES Users,    -- User being followed
  followerId TEXT NOT NULL REFERENCES Users   -- User doing the following
);

-- eventType
-- "read" -> The leader has read the book
-- "done" -> The leader is no longer reading the book
CREATE TABLE IF NOT EXISTS Events (
  --id TEXT PRIMARY KEY NOT NULL,               -- Event ID
  leaderId TEXT NOT NULL REFERENCES Users,    -- User who created to event
  eventType TEXT NOT NULL,                    -- What is the type of event
  bookId TEXT NOT NULL REFERENCES Books(id),  -- ID of book
  dateAdded datetime(3) NOT NULL, -- Format: YYYY-MM-DD HH:MM:SS.SSS
                                  --strftime('%Y-%m-%d %H:%M:%S', ...)
  eventId TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Collections (
  id TEXT PRIMARY KEY NOT NULL,
  name TEXT NOT NULL,
  user_created TEXT REFERENCES Users(username) -- User who owns this collection
  --user_created TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS Collections__Book (
  --collections_id TEXT NOT NULL,
  collections_id TEXT REFERENCES Collections (id),
--  book_id TEXT NOT NULL,
  book_id SERIAL REFERENCES Books (id),
  dateAdded date(1) NOT NULL -- Format: YYYY-MM-DD
);

CREATE TABLE IF NOT EXISTS Books__Read (
  userId INT NOT NULL REFERENCES Users (username),
  bookId INT NOT NULL REFERENCES Books (id),
  dateAdded date(1) NOT NULL, -- Format: YYYY-MM-DD
  UNIQUE(userId,bookId)
);

CREATE TABLE IF NOT EXISTS goals (
  userId INT NOT NULL REFERENCES Users (username),
  bookId INT NOT NULL REFERENCES Books (id),
  dateToRead date(1) NOT NULL, -- Format: YYYY-MM-DD
  dateAdded date(1) NOT NULL, -- Format: YYYY-MM-DD
  complete INT NOT NULL,
  UNIQUE(userId,bookId)
);


--RATING_TABLE
