-------------------------------------------------------------------------
-- Every thing in this file is for the unit tests only                 --
--                                                                     --
-- NOTE: If you touch something here, chances are it will stuff up the --
--       tests. Adding something is okay most cases, but changing the  --
--       order will definatly have problems                            --
-------------------------------------------------------------------------

INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId,publisherId,image_url) VALUES (1,'title 1','country 1','keywords 1',1,1,'/images/001.jpg');
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId,publisherId,image_url) VALUES (2,'title 2','country 2','keywords 2',2,2,'/images/002.jpg');
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId,publisherId,image_url) VALUES (3,'title 3','country 3','keywords 3',3,3,'/images/003.jpg');
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId,publisherId,image_url) VALUES (4,'title 4','country 4','keywords 4',4,1,'/images/004.jpg');
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId,publisherId,image_url) VALUES (5,'title 5','country 5','keywords 5',1,2,'/images/005.jpg');
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId,publisherId,image_url) VALUES (6,'title 6','country 6','keywords 6',2,3,'/images/006.jpg');
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId) VALUES (7,'title 7','country 7','keywords 7',3);
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId) VALUES (8,'title 8','country 8','keywords 8',4);
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId) VALUES (9,'title 9','country 9','keywords 9',1);
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId) VALUES (10,'title 10','country 10','keywords 10',2);
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId) VALUES (11,'title 11','country 11','keywords 11',3);
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId) VALUES (12,'title 12','country 12','keywords 12',4);
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId) VALUES (13,'title 13','country 13','keywords 13',1);
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId) VALUES (14,'title 14','country 14','keywords 14',2);
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId) VALUES (15,'title 15','country 15','keywords 15',3);
INSERT INTO "Books" (id,Title,Country,Keywords,catagoryId) VALUES (16,'title 16','country 16','keywords 16',4);

-- Pass=`echo -n john | sha256sum`
-- | username | Pass | selfInfo |
INSERT INTO "Users" VALUES
(
	'jarrod',
	'24048638d9fd0361c3d8d49d61db8955299b074795f72070ab9bffd49351cb46', -- jarrod
	'hi, my name is jarrod'
);

INSERT INTO "Users" VALUES
(
	'user',
	'04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c85b9df8fb', -- user
	'hi, my name is jarrod'
);

INSERT INTO "Users" VALUES
(
	'alex',
	'4135aa9dc1b842a653dea846903ddb95bfb8c5a10c504a7fa16e10bc31d1fdf0', -- alex
	'hi, my name is jarrod'
);

INSERT INTO "Users" VALUES
(
	'john',
	'96d9632f363564cc3032521409cf22a852f2032eec099ed5967c0d000cec607a', -- john
	'hi, my name is john'
);

INSERT INTO "Users" VALUES
(
	'steve',
	'f148389d080cfe85952998a8a367e2f7eaf35f2d72d2599a5b0412fe4094d65c', -- steve
	'hi, my name is steve'
);

INSERT INTO "Followers" (leaderId,followerId) VALUES('jarrod','user');
INSERT INTO "Followers" (leaderId,followerId) VALUES('jarrod','alex');
INSERT INTO "Followers" (leaderId,followerId) VALUES('jarrod','steve');
INSERT INTO "Followers" (leaderId,followerId) VALUES('user','jarrod');
INSERT INTO "Followers" (leaderId,followerId) VALUES('user','steve');

INSERT INTO "Events" (leaderId,eventType,bookId,dateAdded,eventId) VALUES
(
	'user',
	'read',
	4,
	'1999-01-06 01:01:01',
	'1'
);

INSERT INTO "Events" (leaderId,eventType,bookId,dateAdded,eventId) VALUES
(
	'jarrod',
	'read',
	1,
	'1999-01-02 01:01:01',
	'2'
);

INSERT INTO "Events" (leaderId,eventType,bookId,dateAdded,eventId) VALUES
(
	'jarrod',
	'read',
	3,
	'1999-01-05 01:01:01',
	'3'
);

INSERT INTO "Events" (leaderId,eventType,bookId,dateAdded,eventId) VALUES
(
	'jarrod',
	'done',
	1,
	'1999-01-04 01:01:01',
	'4'
);

INSERT INTO "Events" (leaderId,eventType,bookId,dateAdded,eventId) VALUES
(
	'jarrod',
	'read',
	2,
	'1999-01-03 01:01:01',
	'5'
);


INSERT INTO "Followers" (leaderId,followerId) VALUES('user','alex');

INSERT INTO "Collections" (id,name,user_created) VALUES(1, 'main', 'jarrod');
INSERT INTO "Collections" (id,name,user_created) VALUES(2, 'main', 'alex');

INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 1,  date('1999-01-03'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 2,  date('1999-01-06'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 3,  date('1999-01-10'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 4,  date('1999-01-07'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 5,  date('1999-01-14'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 6,  date('1999-01-13'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 7,  date('1999-01-09'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 8,  date('1999-01-12'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 9,  date('1999-01-01'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 10, date('1999-01-05'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 11, date('1999-01-08'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 12, date('1999-01-11'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 13, date('1999-01-04'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(1, 14, date('1999-01-02'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(2, 1, date('1999-01-01'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(2, 2, date('1999-01-02'));
INSERT INTO "Collections__Book" (collections_id,book_id,dateAdded) VALUES(2, 3, date('1999-01-03'));

INSERT INTO "Reviews" (id,review,rating,reviewer,book) VALUES (1, "review 1", 4, 'jarrod', 1);
INSERT INTO "Reviews" (id,review,rating,reviewer,book) VALUES (2, "review 2", 4, 'user', 1);
INSERT INTO "Reviews" (id,review,rating,reviewer,book) VALUES (3, "review 3", 4, 'alex', 1);

INSERT INTO "Reviews" (id,review,rating,reviewer,book) VALUES (4, "review 4", 5, 'jarrod', 2);
INSERT INTO "Reviews" (id,review,rating,reviewer,book) VALUES (5, "review 5", 5, 'user', 2);
INSERT INTO "Reviews" (id,review,rating,reviewer,book) VALUES (6, "review 6", 5, 'alex', 2);

INSERT INTO "Reviews" (id,review,rating,reviewer,book) VALUES (7, "review 7", 2, 'jarrod', 2);
INSERT INTO "Reviews" (id,review,rating,reviewer,book) VALUES (8, "review 8", 2, 'user', 2);
INSERT INTO "Reviews" (id,review,rating,reviewer,book) VALUES (9, "review 9", 2, 'alex', 2);

-- All possible catagorys
-- | id | catagory |
INSERT INTO "Catagorys" VALUES (1, "Arts and Music");
INSERT INTO "Catagorys" VALUES (2, "Biographies");
INSERT INTO "Catagorys" VALUES (3, "Business");
INSERT INTO "Catagorys" VALUES (4, "Comics");
INSERT INTO "Catagorys" VALUES (5, "pls dont touch");

INSERT INTO "Authors" (id,name) VALUES (1, "Mr 1");
INSERT INTO "Authors" (id,name) VALUES (2, "Mr 2");
INSERT INTO "Authors" (id,name) VALUES (3, "Mr 3");
INSERT INTO "Authors" (id,name) VALUES (4, "Mr 4");
INSERT INTO "Authors" (id,name) VALUES (5, "Mr 5");
INSERT INTO "Authors" (id,name) VALUES (6, "Mr 6");
INSERT INTO "Authors" (id,name) VALUES (7, "Mr 7");
INSERT INTO "Authors" (id,name) VALUES (8, "Mr 8");
INSERT INTO "Authors" (id,name) VALUES (9, "Mr 9");
INSERT INTO "Authors" (id,name) VALUES (10, "Mr 10");
INSERT INTO "Authors" (id,name) VALUES (11, "Mr 11");
INSERT INTO "Authors" (id,name) VALUES (12, "Mr 12");

INSERT INTO "Authors_Books" (authorId,bookId) VALUES (1,9);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (2,4);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (2,9);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (3,3);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (4,3);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (4,7);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (5,2);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (6,6);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (7,1);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (7,3);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (7,5);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (10,4);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (10,7);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (10,8);
INSERT INTO "Authors_Books" (authorId,bookId) VALUES (12,4);

INSERT INTO "Publishers" (id,publisher) VALUES (1,"pub 1");
INSERT INTO "Publishers" (id,publisher) VALUES (2,"pub 2");
INSERT INTO "Publishers" (id,publisher) VALUES (3,"pub 3");
