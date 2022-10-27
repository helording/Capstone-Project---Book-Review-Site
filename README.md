Mario party
capstone-project-mario-party created by GitHub Classroom


Environment setup
Essentially all that is involved here is running the setup environment script (setupENV.sh). What it does is downgrade werkzeug for flask restplus and uninstall the default jwt so we can use PYjwt. Due to the way we have ports set up for use in our AWS server you will need to run the Flask.py in sudo, (run startServer.sh). The other thing you should do is run refreshdb.sh once to load our sample data.

IE If you would like to test outside of our implementation outside of our AWS server i would recommend the following.

./setupENV.sh
./refreshdb.sh
./startServer.sh

And that should set up our server with dest data. You can test a login with:

Username: john password: john


To test social features, additional user may need to be created.
