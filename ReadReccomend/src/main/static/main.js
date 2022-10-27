var token = "";
var userInfo = [];

// Method that calls register end point in the API.
function TrySignUp(){

    // Axios http request call. Requires username and password from user input
    axios({
        method: 'post',
        url: window.location.origin + '/register',
        data: {
            username: document.getElementById('username').value,
            password: document.getElementById('password').value
        }
    })
        .then(response => {
            token = response.data.token;
            alert("Sign up sccsesful!")
            TryLogin();
        }, (error) => {
            alert("user already existed SignUp failed")
        });
}

// Method that calls login end point in the API.
function TryLogin(){
    axios({
        method: 'post',
        url: window.location.origin + '/login',
        data: {
            username: document.getElementById('username').value,
            password: document.getElementById('password').value
        }
    })
        .then(response => {

            if (response.status = 200) {
                token = response.data.token
                window.localStorage.setItem("token", token)

                window.location.replace(window.location.origin + "/userHome")
            }
        }, (error) => {
            alert("invalid login")
        });
}

// Method that calls logout end point in the API.
function TryLogOut() {
  console.log("HERE")
  token = window.localStorage.getItem('token')
  axios({
      method: 'post',
      headers: { "Token": token },
      url: window.location.origin + '/logout'
  })
      .then(response => {

          if (response.status = 200) {
              console.log("SUCCESS")
              window.location.replace(window.location.origin + "/Login")
          }
      }, (error) => {
          alert("Cannot logout")
      });

}

// Method recieves basic account information for certain pages
function TryReadProfile() {
    console.log("here")
    token = window.localStorage.getItem('token')
    console.log(token)
    axios.get(window.location.origin + '/myaccount', {
        headers: { "Token": token }
    })
        .then(response => {
            console.log(response.data);

            window.localStorage.setItem('userInfo', JSON.stringify(response.data));


            if (document.getElementById("usrName") != null) {
                document.getElementById("usrName").innerHTML = response.data["username"] + "'s home page";
            }

        }, (error) => {
            console.log(error)
        })

}

/*
Method that calls gets the users collection data and using it to build a list of a user collections
*/
function CreateCollectionsPage() {
    token = window.localStorage.getItem('token');
    axios.get(window.location.origin + '/myaccount', {
        headers: { "Token": token }
    })
        .then(response => {
            var collections = response.data['collections'];
            var colsDiv = document.getElementById("userCollectionList")
            if (collections != null) {
                collections.forEach(function (collection) {
                    var collectionList = document.getElementById("userCollectionList");
                    var listElement = document.createElement("div");
                    listElement.setAttribute("class", "collection")
                    var colDiv = document.createElement("div");
                    colName = document.createElement("a");
                    colName.innerHTML = collection['name'];

                    colName.setAttribute("href", "Collection");
                    colName.setAttribute("onclick", "saveID(this)");
                    colName.setAttribute("id", collection['id']);

                    var del = document.createElement('a');
                    del.innerHTML = "delete";
                    del.setAttribute('class', "link");
                    deleteColFunction = "DeleteCollection(\"" + collection['id'] + "\")"
                    del.setAttribute("onclick", deleteColFunction);


                    colDiv.appendChild(colName);
                    colDiv.appendChild(del);

                    listElement.appendChild(colDiv);
                    collectionList.appendChild(listElement);
                })
            }

        }, (error) => {
            console.log(error)
        });

}

/*
Method that posts a new collection to database with a name
*/
function TryCreateCollection(name) {
    token = window.localStorage.getItem('token')
    axios({
        method: "post",
        url: window.location.origin + "/collections",
        headers: { "Token": token },
        data: {
            name: name
        }
    }).
        then(response => {
            console.log(response);
            if (response.status = 200) {
                window.location.replace(window.location.origin + "/UserCollections")
            }
        }, (error) => {
            alert("Invalid collection name")
        })

}

/*
Method that makes a post request to delete a collection from a collection id
*/
function DeleteCollection(colId) {
  token = window.localStorage.getItem('token')
  console.log(colId)
  axios({
      method: "delete",
      url: window.location.origin + "/collections",
      headers: { "Token": token },
      data: {
          name: "",
          colId: colId
      }
  }).
      then(response => {
          console.log(response);
          if (response.status = 200) {
              window.location.replace(window.location.origin + "/UserCollections")
          }
      }, (error) => {
          alert("Couldn't delete collection")
      })

}

/*
Method that makes a get request to find another user's (not the current user) collections
and creates links for those collections in the Find Collections page

Method makes sure the user exists

Method then grabs collectiosn of user and
makes links to  restricted collection pages
*/
function FindUsersCols(username) {
    document.getElementById("userCollectionList").innerHTML = "";

    var username = username
    window.localStorage.setItem("otherUsersName", username)
    console.log("HERE USERNAME IS: " + username)
    token = window.localStorage.getItem('token')

    axios({
        method: "get",
        url: window.location.origin + "/getUser/" + username,
        headers: { "Token": token }
    }). then(response => {
        if (response.status = 200) {
            console.log(response)
            if (response.data != null) {
              axios({
                  method: "get",
                  url: window.location.origin + "/userscollections/" + username,
                  headers: { "Token": token }
              }).
                  then(response => {
                      console.log(response);
                      var colsDiv = document.getElementById("userCollectionList")

                      var collections = response.data['collections'];
                      var colsDiv = document.getElementById("userCollectionList")
                      if (collections != null) {
                          collections.forEach(function (collection) {
                              var collectionList = document.getElementById("userCollectionList");
                              var listElement = document.createElement("div");
                              listElement.setAttribute("class", "collection")
                              var colDiv = document.createElement("div");
                              colName = document.createElement("a");
                              colName.innerHTML = collection['name'];

                              colName.setAttribute("href", "OtherUsersCollection");
                              colName.setAttribute("onclick", "saveID(this)");
                              colName.setAttribute("id", collection['id']);
                              colDiv.appendChild(colName);

                              listElement.appendChild(colDiv);
                              collectionList.appendChild(listElement);
                          })
                      }

                  }, (error) => {
                      alert("Couldn't find users collections")
                  })
            } else {
                alert("Couldn't find user")
            }

        }
    }, (error) => {
        alert("Couldn't find user")
    });
}

/*
Method that makes a post request to change a user's info.
This method is no longer used.
*/
function TryEditUserInfo(){
    token = window.localStorage.getItem('token');
    let userInfo = document.getElementById("userInfo").value;
    axios({
        method: "post",
        url: window.location.origin + "/myaccount",
        headers: { "Token": token },
        data: {
            info: userInfo
        }
    }).
        then(response => {
            console.log(response);
            if (response.status = 200) {
                window.location.replace(window.location.origin + "/userHome");
            }
        }, (error) => {
                alert("Couldn't edit information");
        });

}

/*
Method that makes finds and creates elements for a collection page
*/
function CreateCollectionPage() {
    token = window.localStorage.getItem('token');
    id = window.localStorage.getItem('idCol');
    url = window.location.origin + '/collections/';
    url = url + id;

    axios.get(url, {
        headers: { "Token": token }
    })
        .then(response => {

            var collection = response.data['collection'];
            var colName = collection["name"];
            var colNameDiv = document.getElementById("CollectionName");
            var colNameH1 = document.createElement("h1");
            colNameH1.innerHTML = "Collection: " + colName;
            colNameDiv.appendChild(colNameH1);
            var books = response.data['books'];
            var booksDiv = document.getElementById("Books");

            if (books != null) {
                createListOfBooksOnClickHref(books, "Books", "saveID(this)", window.location.origin + "/Book")
            }

            url = window.location.origin + '/api/recentlyAddedBooks/';
            url = url + id;

            axios.get(url, {
                headers: { "Token": token }
            })
                .then(response => {
                    var books = response.data;
                    var booksDiv = document.getElementById("NewBooks");
                    console.log(books)
                    if (books != null) {
                      createListOfBooksOnClickHref(books, "NewBooks", "saveID(this)", window.location.origin + "/Book")

                    }


                }, (error) => {
                    console.log(error);
                });

        }, (error) => {
            console.log(error);
        });
}

/*
Method that makes finds and creates elements for another users pages.
This includes finding their events and collections.
*/
function CreateOtherUsersPage() {
    username = window.localStorage.getItem('userID');
    titleDiv = document.getElementById('title');
    titleDiv.innerHTML = username+"'s Page"
    FindUsersCols(username);

    token = window.localStorage.getItem('token')
    axios({
        method: "get",
        url: window.location.origin + "/getEventsByOtherUser/" + username,
        headers: { "Token": token }
    }).
        then(response => {
            if (response.status = 200) {
                console.log("here")
                console.log(response)
                data = response.data
                createEventList(data, "eventList", null, null)
            }
        }, (error) => {
            alert("Couldn't create user's page")
        })
}

/*
Method that makes finds and creates elements for another users specific collection page
*/
function CreateOtherUsersCollectionPage() {

    token = window.localStorage.getItem('token');
    id = window.localStorage.getItem('idCol');
    url = window.location.origin + '/collections/';
    url = url + id;

    axios.get(url, {
        headers: { "Token": token }
    })
        .then(response => {
            username = window.localStorage.getItem("otherUsersName");
            var collection = response.data['collection'];
            var colName = collection["name"];
            var colNameDiv = document.getElementById("CollectionName");
            var colNameH1 = document.createElement("h1");
            colNameH1.innerHTML = "Collection: " + colName + "  By user: " + username;
            colNameDiv.appendChild(colNameH1);
            var books = response.data['books'];
            var booksDiv = document.getElementById("Books");

            if (books != null) {
                createListOfBooksOnClickHref(books, "Books", "saveID(this)", window.location.origin + "/Book")

            }

            url = window.location.origin + '/api/recentlyAddedBooks/';
            url = url + id;

            axios.get(url, {
                headers: { "Token": token }
            })
                .then(response => {
                    var books = response.data;
                    var booksDiv = document.getElementById("NewBooks");
                    console.log(books)
                    if (books != null) {
                      createListOfBooksOnClickHref(books, "NewBooks", "saveID(this)", window.location.origin + "/Book")

                    }


                }, (error) => {
                    console.log(error);
                });

        }, (error) => {
            console.log(error);
        });
}

/*
Method that makes creates elements for the remove book from a collection page
*/
function CreateRemoveBookFromCollectionPage() {
    token = window.localStorage.getItem('token');
    id = window.localStorage.getItem('idCol');
    url = window.location.origin + '/collections/';
    url = url + id;
    axios.get(url, {
        headers: { "Token": token }
    })
        .then(response => {

            var collection = response.data['collection'];
            var colName = collection["name"];
            var colNameDiv = document.getElementById("CollectionName");
            var colNameH1 = document.createElement("h1");
            colNameH1.innerHTML = "Which book would you like to remove from " + colName;
            colNameDiv.appendChild(colNameH1);
            var books = response.data['books'];
            var booksDiv = document.getElementById("Books");

            if (books != null) {

                books.forEach(function (book) {
                    var divElement = document.createElement("div");
                    divElement.setAttribute("class", "book");

                    var imageDiv = document.createElement("img");
                    imageUrl = book["imageURL"]
                    if (imageUrl == null){
                        imageDiv.setAttribute("src", "https://upload.wikimedia.org/wikipedia/en/6/6b/Harry_Potter_and_the_Philosopher%27s_Stone_Book_Cover.jpg")
                        imageDiv.setAttribute("class", "bookCoverColPage")
                    } else {
                        imageDiv.setAttribute("src", imageUrl)
                        imageDiv.setAttribute("class", "bookCoverColPage")
                    }
                    divElement.appendChild(imageDiv);

                    var bookDiv = document.createElement("a");
                    bookDiv.innerHTML = book['title'];

                    removeBookURL = window.location.origin + "/collections/" + id + "/" + book['id'] + "/removeBook"
                    removeBookURL = "\"" + removeBookURL + "\""
                    removeBookFunctionString = "RemoveBookFromCollection(" + removeBookURL + ")"
                    bookDiv.setAttribute("onclick", removeBookFunctionString);
                    bookDiv.setAttribute("id", book['id']);
                    bookDiv.setAttribute("class", "bookLink")

                    divElement.appendChild(bookDiv);

                    var keyWordsDiv = document.createElement("div");
                    keyWordsDiv.setAttribute("class", "Keywords");
                    keyWordsDiv.innerHTML = "Keywords: " + book['keywords'];
                    divElement.appendChild(keyWordsDiv);

                    booksDiv.appendChild(divElement);

                });
            }
        }, (error) => {
            console.log(error);
        });
}

/*
Method that does a post request to remove a book from a collection
*/
function RemoveBookFromCollection(url) {
    token = window.localStorage.getItem('token');
    axios({
        method: "post",
        url: url,
        headers: { "Token": token },
    }).then(response => {
        console.log(response);
        if (response.status = 200) {
            window.location.replace(window.location.origin + "/Collection/");
        }
    }, (error) => {
        alert("invalid");
    });
}

/*
Method that makes creates elements for the add book to a collection page
*/
function CreateAddBookCollectionPage(){
    token = window.localStorage.getItem('token');

    id = window.localStorage.getItem('idCol');
    url = window.location.origin + '/collections/';
    url = url + id;

    axios.get(url, {
        headers: { "Token": token }
    })
        .then(response => {
            var collection = response.data['collection'];
            var colName = collection["name"];
            var colNameDiv = document.getElementById("CollectionName");
            var colNameH1 = document.createElement("h1");
            colNameH1.innerHTML = "Which book do you want to add to " + colName + "?";
            colNameDiv.appendChild(colNameH1)
        }, (error) => {
                console.log(error);
    });

}

/*
Method that does a post request to add a book to a collection
*/
function addToCollection(HTMLElementObject) {

    token = window.localStorage.getItem('token');
    bookID = HTMLElementObject.id;
    colID = window.localStorage.getItem('idCol');

    url = window.location.origin + "/collections/" + colID + "/addBook";

    axios({
        method: "post",
        url: url,
        headers: { "Token": token },
        data: {
            book_id: bookID
        }
    }).then(response => {
        if (response.status = 200) {
            window.location.replace(window.location.origin + "/Collection/")
        }
    }, (error) => {
        alert("Couldn't add book to collection");
    });
}

function addToAgivenCol(colID, bookID) {

    url = window.location.origin + "/collections/" + colID + "/addBook";

    axios({
        method: "post",
        url: url,
        headers: { "Token": token },
        data: {
            book_id: bookID
        }
    }).then(response => {
        if (response.status = 200) {
            alert("it has been added");
        }
    }, (error) => {
        alert("Couldn't add to collection");
    });

}

function addToMain() {
    token = window.localStorage.getItem('token');
    bookID = HTMLElementObject.id;
    colID = window.localStorage.getItem('idCol');

    url = window.location.origin + "/collections/" + colID + "/addBook";
}


// Function to create a page to view all books in system with ViewAllBooks.html
function CreateViewAllBooksPage(){
    token = window.localStorage.getItem('token');
    url = window.location.origin + '/api/allBooks';
    axios.get(url, {
        headers: { "Token": token }
    })
        .then(response => {
            var books = response.data
            var booksDiv = document.getElementById("Books")
            books.forEach(function (book) {
                var bookDiv = document.createElement("a");
                bookDiv.innerHTML = book['title'];
                bookDiv.setAttribute("onclick", "saveID(this)");
                bookDiv.setAttribute("id", book['id']);
                booksDiv.appendChild(bookDiv);
            })

        }, (error) => {
            console.log(error)
        });
}

/*
Method that finds data for a book and creates elements in a book page dynamically
given the books data
*/
function CreateBookPage(){
    token = window.localStorage.getItem('token');
    idBook = window.localStorage.getItem('idBook');
    url = window.location.origin + '/books/' + idBook;
    axios.get(url, {
        headers: { "Token": token }
    })
        .then(response => {
            console.log(response)
            var book = response.data["info"];

            bookCoverImageUrl = book['imageURL']
            var bookCoverDiv = document.getElementById("Book Cover");
            if (bookCoverImageUrl == null){
                bookCoverDiv.setAttribute("src", "https://upload.wikimedia.org/wikipedia/en/6/6b/Harry_Potter_and_the_Philosopher%27s_Stone_Book_Cover.jpg")
            } else {
                bookCoverDiv.setAttribute("src", bookCoverImageUrl)
            }
            var dateInput = document.getElementById("dateInput");
            dateInput.style.visibility = "hidden";
            var goalButton = document.getElementById("goalButton");
            goalButton.innerHTML = "add to goal";
            goalButton.addEventListener("click", setDateVisiable);



            var descriptionCotent = document.getElementById("descriptionCotent");
            descriptionCotent.innerHTML = book["description"];

            var readingStaus = response.data["readen"];
            var readenButton = document.getElementById("readenButton");
            var reviewLink = document.getElementById("reviewLink");

            if (readingStaus == true) {
                readenButton.innerHTML = "Unread";
                readenButton.addEventListener("click", markAsUnread);
                reviewLink.style.visibility = "true";
            } else {
                readenButton.innerHTML = "Readen";
                readenButton.addEventListener("click", markAsReaden);
                reviewLink.style.visibility = "hidden";
            }
            document.getElementById("title").innerHTML = book['title'];


            var names = book['Authors'];
            var authors = document.getElementById("Authors");

            if (names == null) {
                authors.innerHTML = "unknown"
            } else {
                for (i = 0; i < names.length; i++) {

                    var n = names[i]["name"] + " ";
                    authors.append(n);
                }
            }

            document.getElementById("Country").innerHTML = book['country'];
            document.getElementById("Keywords").innerHTML = book['keywords'];

            var categoryDiv = document.getElementById("Category");
            categoryDict = book['catagory'];
            if (categoryDict != null){
                categoryDiv.innerHTML = categoryDict['catagory'];
            } else {
                categoryDiv.innerHTML = "This book doesn't have a category."
            }
            var reviews = book['reviews'];
            var reviewsDiv = document.getElementById("Reviews");
            var aveRating = document.getElementById("aveRating");

            var overAll = 0;
            var times = 0;
            var startCount = {
                header: ["star", "count"],
                rows: [
                    ["1 star", 0],
                    ["2 star", 0],
                    ["3 star", 0],
                    ["4 star", 0],
                    ["5 star", 0]
                ]
            }

            if (reviews == null) {
                reviewsDiv.innerHTML = "Nobody has reviewed this book yet";
                aveRating.innerHTML = "Nobody has reviewed this book yet";
            } else {
                reviews.forEach(function (review) {
                    var reviewDiv = document.createElement("div");
                    reviewDiv.setAttribute('class', reviewsDiv)

                    var comment = document.createElement("div");

                    var CommentText = document.createElement("p") ;
                    CommentText.innerHTML = review["text"];
                    comment.appendChild(CommentText);

                    var rating = document.createElement("div");
                    rating = starRating(review["rating"]);
                    startCount["rows"][review["rating"] - 1][1]++;

                    overAll += review["rating"];
                    times++;

                    var comWriter = document.createElement("p");
                    comWriter.innerHTML = "Author: "+review["reviewerId"];
                    comWriter.style.textAlign = "right";
                    reviewDiv.appendChild(comment);
                    reviewDiv.appendChild(rating);
                    reviewDiv.appendChild(comWriter);

                    var line = document.createElement("hr");
                    comWriter.appendChild(line);

                    reviewsDiv.appendChild(reviewDiv);
                })
                aveRating.innerHTML = (overAll / times);
                var chart = anychart.bar();
                chart.data(startCount);
                chart.container("barChart");
                chart.draw();
                chart.title("score");
                chart.yScale().minimum(0);
                chart.yScale().ticks().interval(1);
            }
        }, (error) => {
            console.log(error);
        });

}

function setDateVisiable() {
    var dateInput = document.getElementById("dateInput");
    dateInput.style.visibility = "visible";
}

function starRating(num) {
    var stars = document.createElement("div");
    for (i = 0; i < 5; i++) {
        if (i < num) {
            var checked = document.createElement("span");
            checked.setAttribute('class', "fa fa-star checked");
            stars.appendChild(checked);
        }
    }
    return stars;
}

function addToReadList() {
    idBook = window.localStorage.getItem('idBook');
    token = window.localStorage.getItem('token');
    var date =  document.getElementById("readTime").value;

    url = window.location.origin + '/api/books/' + idBook + '/' + date + '/goal';

    console.log(date)
    axios({
        method: "post",
        url: url,
        headers: { "Token": token }
    }).then(response => {
        alert("suessfully added");
    }, (error) => {
        alert("Goal date has been set! You may remove it first");
    });
}

function removeReadList(id) {

    token = window.localStorage.getItem('token');

    url = window.location.origin + '/api/books/' + id + '/goal';


    axios({
        method: "delete",
        url: url,
        id: id,
        headers: { "Token": token }
    }).then(response => {
        alert("suessfully delected");
    }, (error) => {
        alert("Goal date has been set! You may remove it first");
    });

}

function getAllGoal(completeStatus, DueStatus, div) {
    token = window.localStorage.getItem('token');
    axios({
        method: "get",
        url: window.location.origin + '/api/me/goals',
        headers: { "Token": token }
    }).then(response => {
        console.log(response.data);
        createListOfgoal(response.data, div, "saveID(this)", window.location.origin + "/Book", completeStatus, DueStatus);
    }, (error) => {
        alert("error");
    });
}

function completeGoal(id) {
    token = window.localStorage.getItem('token');
    axios({
        method: "post",
        url: window.location.origin + '/api/books/' +id+'/completeGoal',
        headers: {"Token": token }
    }).then(response => {
        console.log("done");
    }, (error) => {
        alert("error");
    });
}

function getNumberOfReaders() {
    idBook = window.localStorage.getItem('idBook');
    token = window.localStorage.getItem('token');
    url = window.location.origin + '/getReadCount/' + idBook;
    axios.get(url, {
        headers: { "Token": token }
    }).then(response => {
        var readerNum = document.getElementById("readerNum");
        readerNum.setAttribute('style', 'font-size: 15px; cursor: pointer; text-align:center;');
        if (response.data == 0) {
            readerNum.innerHTML = "Nobody has read it.";
        } else if (response.data == 1) {
            readerNum.innerHTML = "There is only one person read it";
        } else {
            readerNum.innerHTML = "There has been " + response.data+" read it";
        };
    });
}

/*
Method that creates elements for a review page
*/
function CreateReviewPage() {
    idBook = window.localStorage.getItem('idBook');
    token = window.localStorage.getItem('token');

    url = window.location.origin + '/books/' + idBook;
    axios.get(url, {
        headers: { "Token": token }
    })
        .then(response => {
            var book = response.data;
            var titleDiv = document.getElementById("Title");
            titleDiv.innerHTML = "Wirte a review for "+ book['info']['Title'];
        });

}

/*
Method that adds a review for a book
when review is submitted in the review page
*/
function addReview(dictData) {
    idBook = window.localStorage.getItem('idBook');
    token = window.localStorage.getItem('token');

    url = window.location.origin + '/addReview/' + idBook;

    axios({
        method: "post",
        url: url,
        headers: { "Token": token },
        data: {
            textReview: dictData["textReview"],
            rating: dictData["rate"]
        }
    }).then(response => {
        window.location.replace(window.location.origin + "/Book")
    });
}

function markAsReaden() {
    id = window.localStorage.getItem('idBook');
    token = window.localStorage.getItem('token');
    url = window.location.origin + "/api/books/" + id + "/read"
    axios({
        method: "post",
        url: url,
        headers: { "Token": token }
    }).then(response => {
        location.reload();
    })

}

function markAsUnread() {
    id = window.localStorage.getItem('idBook');
    token = window.localStorage.getItem('token');
    url = window.location.origin + "/api/books/" + id + "/read"
    axios({
        method: "delete",
        url: url,
        headers: { "Token": token }
    }).then(response => {
        url = window.location.origin + '/getReadCount/' + idBook
        axios.get(url, {
          headers: {"Token": token}
        }).then(response => {
            location.reload();
        })
    })
}

/*
Method that creates elements for the book search page.
The method mostly finds and adds the book categories to the
drop down menu options dynamically.
*/
function CreateSearchPage(){

    token = window.localStorage.getItem('token');

    url = window.location.origin + '/getCategories';
    axios.get(url, {
        headers: { "Token": token }
    })
        .then(response => {

            var categories = response.data;
            var search_list_container = document.getElementById("search-list-container");
            categories.forEach(function (category) {
                categoryName = category['catagory']
                categoryID = category['id']
                var categoryA = document.createElement("a");
                categoryA.setAttribute("tabindex", "0")
                functionCallString = "clieckedDropDownSearchOption(\"" + categoryName + "\",\"divinestaroptions[font][font2]\",\"" + categoryID + "\")"
                categoryA.setAttribute("onclick", functionCallString)
                categoryA.setAttribute("class", "ds-dropdown-search-item")
                categoryA.setAttribute("data-value", categoryName)
                categoryA.setAttribute("style", "display: block;")
                categoryA.innerHTML = categoryName

                search_list_container.appendChild(categoryA)
            })
        });
}

/*
Method that executes a search given a dictionary of data
*/
function TrySearch(dictData) {
    document.getElementById("results").innerHTML = "";

    token = window.localStorage.getItem('token');
    url = window.location.origin + '/Search';

    if (!("rate" in dictData)) {
        dictData['rate'] = '';
    }
    console.log(dictData)

    axios({
        method: 'post',
        url: url,
        headers: { "Token": token },
        data: {
            Title: dictData['Title'],
            Country: dictData['Country'],
            catagoryId: dictData['category'],
            author: dictData['author'],
            publisher: dictData['publisher'],
            min_rate: dictData['rate']
        }
    })
        .then(response => {
            console.log(response)
            data = response.data

            if (("error" in data)) {
                var resultsDiv = document.getElementById("results");
                resultsDiv.innerHTML = data['error'] + " and search criteria";
            } else {
                var books = response.data
                console.log("here")

                createListOfBooksOnClickHref(books, "results", "saveID(this)", window.location.origin + "/Book")
            }
          });
}

/*
Method executes a search and creates results for the
add book to collection page
*/
function AddBookToCollectionSearch(dictData) {
    document.getElementById("results").innerHTML = "";
    token = window.localStorage.getItem('token');
    url = window.location.origin + '/Search';

    if (!("rate" in dictData)) {
        dictData['rate'] = '';
    }
    axios({
        method: 'post',
        url: url,
        headers: { "Token": token },
        data: {
            Title: dictData['Title'],
            Country: dictData['Country'],
            catagoryId: dictData['category'],
            author: dictData['author'],
            publisher: dictData['publisher'],
            min_rate: dictData['rate']
        }
    })
    .then(response => {

      data = response.data;
      var resultsDiv = document.getElementById("results");

      if (("error" in data)) {
          resultsDiv.innerHTML = data['error'] + " and search criteria";
      } else {
          var books = response.data;
          createListOfBooksOnClickHref(books, "results", "addToCollection(this)", null)
    };
  })
}

/*
Method executes a search and creates
book results for the recommendation page
*/
function SearchForRecommendation(dictData) {
    document.getElementById("results").innerHTML = "";
    token = window.localStorage.getItem('token');
    url = window.location.origin + '/Search';

    if (!("rate" in dictData)) {
        dictData['rate'] = '';
    }
    axios({
        method: 'post',
        url: url,
        headers: { "Token": token },
        data: {
            Title: dictData['Title'],
            Country: dictData['Country'],
            catagoryId: dictData['category'],
            author: dictData['author'],
            publisher: dictData['publisher'],
            min_rate: dictData['rate']
        }
    })
    .then(response => {

      data = response.data;

      if (("error" in data)) {
          resultsDiv = document.getElementById("results");
          resultsDiv.innerHTML = data['error'] + " and search criteria";
      } else {
          var books = response.data;

          if (books != null) {
            createListOfBooksOnClickHref(books, "results", "saveID(this)", null);

          }
    };
  })
}

/*
Method executes a recommendation search given a book and a recommendation mode.
Loads the results in the recommendations div in the recommendation page.
*/
function ExecuteRecommendation(bookID, recMode) {
    token = window.localStorage.getItem('token');
    if(bookID!=-1){
        url = window.location.origin + '/recommend/' + recMode + "/" + bookID;
    }
    else{
        url = window.location.origin + '/recommend/' + recMode;
    }
    console.log(url)

    axios.get(url, {
        headers: { "Token": token }
    })
        .then(response => {
            data = response.data
            books = data["books"]
            if (books == -1){
              errorDiv = document.getElementById("error");
              errorDiv.innerHTML = "This book has no ratings. No recommendation can be made."
            } else {
                if (books != null) {
                  document.getElementById("recommendations").innerHTML = "Recommendations:"
                  createListOfBooksOnClickHref(books, "recommendations", "saveIDRecResults(this)", window.location.origin + "/Book")
                };
            };
        });
}

/*
Method that given a list of books and a div, loads book links into that div.
onclick and href attributes can also be added if needed (not set to null)
*/
function createListOfBooksOnClickHref(books, targetDivId, onClick, hRef) {
    targetDiv = document.getElementById(targetDivId)
    books.forEach(function (book) {
    var divElement = document.createElement("div");
    divElement.setAttribute("class", "book");

    var imageDiv = document.createElement("img");
    imageUrl = book["imageURL"]
    if (imageUrl == null){
        imageDiv.setAttribute("src", "https://upload.wikimedia.org/wikipedia/en/6/6b/Harry_Potter_and_the_Philosopher%27s_Stone_Book_Cover.jpg")
        imageDiv.setAttribute("class", "bookCoverColPage")
    } else {
        imageDiv.setAttribute("src", imageUrl)
        imageDiv.setAttribute("class", "bookCoverColPage")
    }
    divElement.appendChild(imageDiv);

    var bookDiv = document.createElement("a");
    bookDiv.innerHTML = book['title'];

    if (hRef != null) {
      bookDiv.setAttribute("href", hRef);
    }
    bookDiv.setAttribute("onclick", onClick);
    bookDiv.setAttribute("id", book['id']);
    bookDiv.setAttribute("class", "bookLink")

    divElement.appendChild(bookDiv);

    var keyWordsDiv = document.createElement("div");
    keyWordsDiv.setAttribute("class", "Keywords");
    if (book['keywords'] != null) {
      keyWordsDiv.innerHTML = "Keywords: " + book['keywords'];
    } else {
      keyWordsDiv.innerHTML = "This book doesn't have any keywords"
    }
    divElement.appendChild(keyWordsDiv);

    var authorsDiv = document.createElement("div");
    authorsDiv.setAttribute("class", "Authors");
    authors = ""
    if (book['Authors'] != null) {
      book['Authors'].forEach(function (author) {
        authors = authors + author["name"] + " "
      })
    }

    if (authors != "") {
      authorsDiv.innerHTML = "Authors: " + authors;
    } else {
      authorsDiv.innerHTML = "Authors: The authors of this book are unknown"
    }

    divElement.appendChild(authorsDiv);

    var catDiv = document.createElement("div");
    catDiv.setAttribute("class", "Category");
    if (book['catagory'] != null) {
      catDiv.innerHTML = "Category: " + book['catagory']['catagory'];
    } else {
      catDiv.innerHTML = "Category: This book doesn't have a category"
    }
    divElement.appendChild(catDiv);

    var reviewsDiv = document.createElement("div");
    reviewsDiv.setAttribute("class", "Reviews");
    overAll = 0;
    times = 0;
    if (book['reviews'] != null) {
      book['reviews'].forEach(function (review) {
        overAll += review["rating"];
        times++;
      })
    }

    if (times != 0) {
      average = (overAll / times)
      average = (Math.round(average * 100) / 100).toFixed(2);
      reviewsDiv.innerHTML = "Avergae rating: " + average;
    } else {
      reviewsDiv.innerHTML = "Avergae rating: There are no reviews for this book yet";
    }

    divElement.appendChild(reviewsDiv);

    targetDiv.appendChild(divElement);

  })

}


function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    return [year, month, day].join('-');
}

function createListOfgoal(books, targetDivId, onClick, hRef, completeStatus, DueStatus) {
    targetDiv = document.getElementById(targetDivId);
    console.log(books);
    if (books.length != 0) {
        books.forEach(function (book) {
            var today = new Date();
            if (book['complete'] == completeStatus && (today < new Date(book['dateToRead']) == DueStatus)) {
                var divElement = document.createElement("div");
                divElement.setAttribute("class", "column");

                var imageDiv = document.createElement("img");

                imageUrl = book["imageURL"]
                if (imageUrl == null) {
                    imageDiv.setAttribute("src", "https://upload.wikimedia.org/wikipedia/en/6/6b/Harry_Potter_and_the_Philosopher%27s_Stone_Book_Cover.jpg")
                    imageDiv.setAttribute("class", "columnImg")
                } else {
                    imageDiv.setAttribute("src", imageUrl)
                    imageDiv.setAttribute("class", "columnImg")
                }



                var bookDiv = document.createElement("a");

                bookDiv.innerHTML = book['Title'];

                if (hRef != null) {
                    bookDiv.setAttribute("href", hRef);
                }
                bookDiv.setAttribute("onclick", onClick);
                bookDiv.setAttribute("id", book['id']);


                var dateToFinish = document.createElement("t");
                dateToFinish.innerHTML = "Finish by ";

                var date = document.createElement("t");
                date.innerHTML = book['dateToRead'];
                dateToFinish.appendChild(document.createElement('br'));
                dateToFinish.appendChild(date);
                dateToFinish.appendChild(document.createElement('br'));
                dateToFinish.setAttribute("class", "columnText")

                divElement.appendChild(bookDiv);
                divElement.appendChild(document.createElement("br"));

                divElement.appendChild(imageDiv);
                divElement.appendChild(dateToFinish);

                if (completeStatus == false && DueStatus == true) {
                    var remove = document.createElement("t");
                    remove.innerHTML = "remove";
                    remove.setAttribute("class", "link");

                    remove.addEventListener('click', function () {
                        removeReadList(book['id']);
                        location.reload();
                    });
                    dateToFinish.appendChild(remove);
                    dateToFinish.appendChild(document.createElement('br'));

                    var finished = document.createElement("t");
                    finished.innerHTML = "finished";
                    finished.setAttribute("class", "link");
                    finished.addEventListener('click', function () {
                        completeGoal(book['id']);
                        location.reload();
                    });
                    dateToFinish.appendChild(finished);

                }

                targetDiv.appendChild(divElement);
            }
        })
    };

}

function createListOfInterest(books, targetDivId, onClick, hRef) {
    targetDiv = document.getElementById(targetDivId)
    books.forEach(function (book) {
        var divElement = document.createElement("div");
        divElement.setAttribute("class", "column");

        var imageDiv = document.createElement("img");

        imageUrl = book["imageURL"]
        if (imageUrl == null) {
            imageDiv.setAttribute("src", "https://upload.wikimedia.org/wikipedia/en/6/6b/Harry_Potter_and_the_Philosopher%27s_Stone_Book_Cover.jpg")
            imageDiv.setAttribute("class", "columnImg")
        } else {
            imageDiv.setAttribute("src", imageUrl)
            imageDiv.setAttribute("class", "columnImg")
        }

        var bookDiv = document.createElement("a");
        bookDiv.innerHTML = book['Title'];

        if (hRef != null) {
            bookDiv.setAttribute("href", hRef);
        }
        bookDiv.setAttribute("onclick", onClick);
        bookDiv.setAttribute("id", book['id']);

        divElement.appendChild(bookDiv);
        divElement.appendChild(document.createElement("br"));
        divElement.appendChild(imageDiv);

        targetDiv.appendChild(divElement);
    })
}


function topThreeMostRead() {
    token = window.localStorage.getItem('token');
    axios({
        method: 'get',
        url: window.location.origin + '/api/books/recentlyRead/3',
        headers: { "Token": token }

    }).then(response => {
        createListOfInterest(response.data, "interestBooks", "saveID(this)", window.location.origin + "/Book");
    });

}

/*
Method that gets a users social data and then creates the users social page
*/
function CreateSocialPage() {
  token = window.localStorage.getItem('token')
  axios({
      method: "get",
      url: window.location.origin + "/getLeaders",
      headers: { "Token": token }
  }).
      then(response => {
          if (response.status = 200) {
            console.log(response)
            data = response.data
            followingDiv = document.getElementById("following");
            data.forEach(function (user) {
                  console.log(user);
                  var listElement = document.createElement("li");
                  listElement.setAttribute("class", "personLink");

                  var divElement = document.createElement("a");
                  divElement.innerHTML = user['username'];
                  divElement.setAttribute("href", "usersPage");
                  divElement.setAttribute("id", user['username']);
                  divElement.setAttribute("onclick", "saveID(this)");
                  listElement.appendChild(divElement);
                  followingDiv.appendChild(listElement);
            })

          }
      }, (error) => {
          alert("Couldn't get who you are following")
      })

  token = window.localStorage.getItem('token')
  axios({
      method: "get",
      url: window.location.origin + "/getFollowers",
      headers: { "Token": token }
  }).
      then(response => {
          if (response.status = 200) {
              console.log(response);
              data = response.data;
              followersDiv = document.getElementById("followers")
              data.forEach(function (user) {
                    console.log(user);
                    var listElement = document.createElement("li");
                    listElement.setAttribute("class", "personLink");

                    var divElement = document.createElement("a");
                    divElement.innerHTML = user['username'];
                    divElement.setAttribute("href", "usersPage");
                    divElement.setAttribute("id", user['username']);
                    divElement.setAttribute("onclick", "saveID(this)");
                    listElement.appendChild(divElement);
                    followersDiv.appendChild(listElement);
              })
          }
      }, (error) => {
          alert("Couldn't find who is following you")
      })

      token = window.localStorage.getItem('token')
      axios({
          method: "get",
          url: window.location.origin + "/getEventsForUser",
          headers: { "Token": token }
      }).
          then(response => {
              if (response.status = 200) {
                  console.log(response)
                  data = response.data
                  createEventList(data, "leadersEvents", 1, null)
              }
          }, (error) => {
              alert("Can't find events for you")
          })

      token = window.localStorage.getItem('token')
      axios({
          method: "get",
          url: window.location.origin + "/getEventsByUser",
          headers: { "Token": token }
      }).
          then(response => {
              if (response.status = 200) {
                  console.log(response)
                  data = response.data
                  createEventList(data, "yourEvents", null, null)
              }
          }, (error) => {
              alert("Can't find your events")
          })

}

/*
Method that makes a post request to follow a user given their name
*/
function FollowSomeone(dictData) {
    var username = dictData["username"]
    console.log("HERE USERNAME IS: " + username)
    token = window.localStorage.getItem('token')

    axios({
        method: "get",
        url: window.location.origin + "/getUser/" + username,
        headers: { "Token": token }
    }). then(response => {
        if (response.status = 200) {
            console.log(response)
            if (response.data != null) {
              axios({
                  method: "post",
                  url: window.location.origin + "/addLeader/" + username,
                  headers: { "Token": token }
              }).
                  then(response => {
                      if (response.status = 200) {
                          window.location.replace(window.location.origin + "/social")
                      }
                  }, (error) => {
                      alert("couldn't follow this user try again")
                  })
            } else {
                alert("Couldn't find user")
            }

        }
    }, (error) => {
        alert("Couldn't find user")
    })
}

/*
Method that makes a creates an event.
*/
function createEventt() {
    token = window.localStorage.getItem('token')
    var bookID = window.localStorage.getItem('idRecBook')
    var date =  document.getElementById("readTime").value;
    var eventType =  document.getElementById("eventType").value;

    url = window.location.origin + "/createEvent/" + eventType + "/" + bookID + "/" + date

    axios({
        method: "post",
        url: url,
        headers: { "Token": token }
    }).
        then(response => {
            if (response.status = 200) {
                console.log(response)
                window.location.replace(window.location.origin + "/social")
            }
        }, (error) => {
            alert("Couldn't create event")
        })
}

/*
Method that makes a creates a list of events in a given div.
Has option to add a link to the person who create the event (if in users own page not needed)
Has option to create a list of events which are "done"
*/
function createEventList (events, targetDiv, leadersNeeded, done){
  eventsDiv = document.getElementById(targetDiv)
  events.forEach(function (e) {
        console.log(e)
        var divElement = document.createElement("div");
        divElement.setAttribute("class", "event");

        var linkElement = document.createElement("div");
        linkElement.innerHTML = "Event: " + e['type']
        linkElement.setAttribute("class", "eventElement");
        linkElement.setAttribute("id", e['eventId']);
        divElement.appendChild(linkElement)

        if (leadersNeeded != null) {
          var leaderElement = document.createElement("a");
          leaderElement.innerHTML = "Made By: " + e['leader']
          leaderElement.setAttribute("href", "usersPage")
          leaderElement.setAttribute("id", e['leader'])
          leaderElement.setAttribute("onclick", "saveID(this)")
          leaderElement.setAttribute("class", "eventElement");
          divElement.appendChild(leaderElement)
        }

        var bookElement = document.createElement("a");
        bookElement.innerHTML = "Book Involved: " + e['book']['title']
        bookElement.setAttribute("href", "Book")
        bookElement.setAttribute("id", e['book']['id'])
        bookElement.setAttribute("onclick", "saveBookID(this)")
        bookElement.setAttribute("class", "eventElement");
        divElement.appendChild(bookElement)

        var dateElement = document.createElement("a");
        dateElement.innerHTML = "On day: " + e['date']
        dateElement.setAttribute("class", "eventElement");
        divElement.appendChild(dateElement)

        eventsDiv.appendChild(divElement)
  })
}

/*
Method that changes div elements on the social page after unfollow button is clicked.
Makes followers links turn red and changes their onclick functions.
*/
function unfollowSomeone() {
  followingDiv = document.getElementById("following");

  followingDiv.innerHTML = ("");

  token = window.localStorage.getItem('token')
  axios({
      method: "get",
      url: window.location.origin + "/getLeaders",
      headers: { "Token": token }
  }).
      then(response => {
          if (response.status = 200) {
            console.log(response)
            data = response.data
            console.log(data)
            data.forEach(function (user) {
                  var listElement = document.createElement("li");
                  listElement.setAttribute("class", "personLink");

                  var divElement = document.createElement("a");
                  divElement.innerHTML = user['username'];
                  divElement.setAttribute("style", "color:#FF0000;")
                  divElement.setAttribute("id", user['username']);
                  onclickFunction = "unfollow(\'" + user['username'] + "\')"
                  divElement.setAttribute("onclick", onclickFunction)
                  listElement.appendChild(divElement);
                  followingDiv.appendChild(listElement);
            })
            unfollowDiv =  document.getElementById('unfollow');
            unfollowDiv.innerHTML = "Cancel unfollow"
            unfollowDiv.setAttribute("href", "social")
            unfollowDiv.setAttribute("style", "color:#FF0000;")
          }
    })
}

/*
Method that unfollows a user
(executed through the onclick function that is made through unfollowSomeone() )
*/
function unfollow(username) {

  token = window.localStorage.getItem('token')
  axios({
      method: "post",
      url: window.location.origin + '/unfollow/' + username,
      headers: { "Token": token }
  }).
      then(response => {
          window.location.replace(window.location.origin + "/social")
      })
}

/*
Method that changes div elements on the social page after complete event button is clicked.
Makes event divs turn green and creates a cancel complete event button on page.
*/
function completeEventButton() {
  token = window.localStorage.getItem('token')
  axios({
      method: "get",
      url: window.location.origin + "/getEventsByUser",
      headers: { "Token": token }
  }).
      then(response => {
          if (response.status = 200) {
              console.log(response)
              data = response.data
              data.forEach( function (e) {
                eventDiv = document.getElementById(e['eventId'])
                eventDiv.setAttribute("style", "color:#00FF00;");
                onclickFunctionName = "thisEventDone(\'" + e['eventId'] + "\')"
                eventDiv.setAttribute("onclick", onclickFunctionName);
              })
              completeDiv =  document.getElementById('completeE');
              completeDiv.innerHTML = "Cancel complete event"
              completeDiv.setAttribute("href", "social")
              completeDiv.setAttribute("style", "color:#FF0000;")

          }
      }, (error) => {
          alert("Error. Can't complete event.")
  })
}

/*
Method that completes event given a event id.
*/
function thisEventDone(eventId) {
  token = window.localStorage.getItem('token')
  axios({
      method: "post",
      url: window.location.origin + "/completeEvent/" + eventId,
      headers: { "Token": token }
  }).
      then(response => {
        alert("Event completed!")
        window.location.replace(window.location.origin + "/social")
      })
}
