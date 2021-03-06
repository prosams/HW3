## SI 364 - Winter 2018
## HW 3

# one of the sources I consulted was http://flask.pocoo.org/snippets/64/
# https://stackoverflow.com/questions/50327174/custom-validators-in-wtforms-using-flask
# https://wtforms.readthedocs.io/en/stable/validators.html#custom-validators

####################
## Import statements
####################

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy

############################
# Application configurations
############################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string from si364'
## TODO 364: Create a database in postgresql in the code line below, and fill in your app's database URI. It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME

## Your final Postgres database should be your uniqname, plus HW3, e.g. "jczettaHW3" or "maupandeHW3"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/ulmasHW3"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##################
### App setup ####
##################
db = SQLAlchemy(app) # For database use

#########################
#########################
######### Everything above this line is important/useful setup,
## not problem-solving.##
#########################
#########################

#########################
##### Set up Models #####
#########################

## TODO 364: Set up the following Model classes, as described, with the respective fields (data types).

## The following relationships should exist between them:
# Tweet:User - Many:One

class Tweet(db.Model):
    __tablename__ = 'Tweets'
    TweetId = db.Column(db.Integer, primary_key=True)               ## -- id (Integer, Primary Key)
    TweetText = db.Column(db.String(280))                           ## -- text (String, up to 280 chars)
    UserId = db.Column(db.Integer, db.ForeignKey('Users.UserId'))   ## -- user_id (Integer, ID of user posted -- ForeignKey)

    def __repr__(self):    #### {Tweet text...} (ID: {tweet id})
        return '%s (ID: %s)' % (self.TweetText, self.TweetId)

class User(db.Model):
    __tablename__ = 'Users'
    UserId = db.Column(db.Integer, primary_key=True)     ## -- id (Integer, Primary Key)
    username = db.Column(db.String(64), unique=True)     ## -- username (String, up to 64 chars, Unique=True)
    display_name = db.Column(db.String(124))              ## -- display_name (String, up to 124 chars)
    tweets =  db.relationship('Tweet', backref='User')
    ## ---- Line to indicate relationship between Tweet and User tables (the 1 user: many tweets relationship)
    #### ^^^ How to do this???

    def __repr__(self):      #### {username} | ID: {id}
        return '%s | ID: %s' % (self.username, self.UserId)

########################
##### Set up Forms #####
########################

# TODO 364: Fill in the rest of the below Form class so that someone running this web app will be able to fill in information about tweets they wish existed to save in the database:

class MyForm(FlaskForm):
    text = StringField('Tweet text!', validators=[Required(), Length(min=0,  max=280)])   ## -- text: tweet text (Required, should not be more than 280 characters)
    username = StringField('Twitter username of who should post', validators=[Required(), Length(min=0,  max=64)])  ## -- username: the twitter username who should post it (Required, should not be more than 64 characters)
    display_name = StringField('Display name of the user', validators=[Required()] )    ## -- display_name: the display name of the twitter user with that username (Required, + set up custom validation for this -- see below)
    submit = SubmitField('Submit')

    def validate_username(self, field): # TODO 364: Set up custom validation for this form
        username = field.data
        if username[0] == "@": # the twitter username may NOT start with an "@" symbol (the template will put that in where it should appear)
            raise ValidationError("Your twitter username cannot start with @.")

    def validate_display_name(form, field): # TODO 364: Set up custom validation for this form
        displaydata = field.data
        splitcheck = displaydata.split(" ")
        if len(splitcheck) <  2: #the display name MUST be at least 2 words (this is a useful technique to practice, even though this is not true of everyone's actual full name!)
            raise ValidationError("Your display name must be at least two words.")

# HINT: Check out index.html where the form will be rendered to decide what field names to use in the form class definition
# TODO 364: Make sure to check out the sample application linked in the readme to check if yours is like it!

###################################
##### Routes & view functions #####
###################################

## Error handling routes - PROVIDED
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#############
## Main route
#############

## TODO 364: Fill in the index route as described.

# A template index.html has been created and provided to render what this route needs to show -- YOU just need to fill in this view function so it will work.
# Some code already exists at the end of this view function -- but there's a bunch to be filled in.
## HINT: Check out the index.html template to make sure you're sending it the data it needs.
## We have provided comment scaffolding. Translate those comments into code properly and you'll be all set!

# NOTE: The index route should:
# - Show the Tweet form.
# - If you enter a tweet with identical text and username to an existing tweet, it should
# redirect you to the list of all the tweets and a message that you've already saved a tweet like that.
# - If the Tweet form is entered and validates properly, the data from the form should be saved properly to the database, and the user should see the form again with a message flashed: "Tweet successfully saved!"
# Try it out in the sample app to check against yours!

@app.route('/', methods=['GET', 'POST'])
def index():
    form = MyForm()
    tweets = Tweet.query.all() # Initialize the form
    num_tweets = len(tweets)    # Get the number of Tweets
    if form.validate_on_submit():
        textform = form.text.data
        username = form.username.data       ## Get the data from the form
        display = form.display_name.data
        user = ""

        ok = db.session.query(User).filter_by(username=username).first()
        if ok:
            user = db.session.query(User).filter_by(username=username).first()
        if not ok:
            user = User(username = username, display_name = display)
            db.session.add(user)
            db.session.commit()

        trying = db.session.query(Tweet).filter_by(TweetText=textform, UserId = user.UserId).first()
        if trying:
            flash("This tweet already exists in the database!")                 # Then flash a message about the tweet already existing
            return redirect(url_for("see_all_tweets"))                          ## And redirect to the list of all tweets

        if not trying:
            newtweet = Tweet(TweetText=textform, UserId=user.UserId)                ## Create a new tweet object with the text and user id
            db.session.add(newtweet)                                            ## And add it to the database
            db.session.commit()
            flash("This tweet has been successfully added.")                    ## Flash a message about a tweet being successfully added
            return redirect(url_for("index"))

    # PROVIDED: If the form did NOT validate / was not submitted
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('index.html', form=form, num_tweets=num_tweets) # TODO 364: Add more arguments to the render_template invocation to send data to index.html

@app.route('/all_tweets')
def see_all_tweets(): # LIKE THE MOVIES AND MOVIE DIRECTOR THING #####################
    tweets = Tweet.query.all()
    tweetlist = []
    for t in tweets:
        tweet = Tweet.query.filter_by(UserId=t.UserId).first() # HINT #2: You'll have to make a query for the tweet and
        user = User.query.filter_by(UserId=tweet.UserId).first()
        tweetlist.append((tweet.TweetText, user.username))
    return render_template('all_tweets.html', all_tweets=tweetlist)

    # TODO 364: Fill in this view function so that it can successfully render the template all_tweets.html, which is provided.
    # HINT: Careful about what type the templating in all_tweets.html is expecting! It's a list of... not lists, but...
    # HINT #2: You'll have to make a query for the tweet and, based on that, another query for the username that goes with it...

@app.route('/all_users')
def see_all_users():     # TODO 364: Fill in this view function so it can successfully
    bigusers = User.query.all()
    print(bigusers)
    return render_template('all_users.html', users=bigusers)    # render the template all_users.html, which is provided.

# TODO 364: Create another route (no scaffolding provided) at /longest_tweet with a view function get_longest_tweet (see details below for what it should do)
# NOTE:This view function should compute and render a template (as shown in the sample application) that shows the text of the tweet currently saved in the database which has the most NON-WHITESPACE characters in it, and the username AND display name of the user that it belongs to.

@app.route('/longest_tweet')
def get_longest_tweet():
    tweets = Tweet.query.all()
    biglist = []
    for t in tweets:
        tweet = Tweet.query.filter_by(UserId=t.UserId).first()
        user = User.query.filter_by(UserId=tweet.UserId).first()
        split = tweet.TweetText.split(" ")
        length = len(split)
        biglist.append((tweet.TweetText, user.username, user.display_name, length))
    sortbylast = sorted(biglist, key=lambda tup: tup[-1], reverse = True)
    biggesttweettup = sortbylast[0]
    return render_template('longest_tweet.html', finaltup = biggesttweettup)
# TODO 364: Create a template to accompany it called longest_tweet.html that extends from base.html.

# NOTE: This is different (or could be different) from the tweet with the most characters including whitespace!
# Any ties should be broken alphabetically (alphabetically by text of the tweet).
# HINT: Check out the chapter in the Python reference textbook on stable sorting.
# Check out /longest_tweet in the sample application for an example.
# could pull all tweets and length tweet....
# could look at other query filters... there are some sorting methods
# could sort by text length itself! — LOOK AT LECTURE 5! import func and filter by a lentgth/sort

if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
