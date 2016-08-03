"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    
    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users"""

    users = User.query.all()

    return render_template('user_list.html', users=users)

@app.route('/user_profile/<user_id>')
def show_user_profile(user_id):
    """Show user profile"""
    
    current_user = User.query.get(user_id)
    age = current_user.age
    zipcode = current_user.zipcode
    ratings = current_user.ratings
    email = current_user.email
    
    user_ratings = {}

    for item in ratings:
        score = item.score
        movie_title = Movie.query.get(item.movie_id).title
        user_ratings[movie_title] = score
 
    return render_template('user_profile.html', email=email, age=age, zipcode=zipcode, ratings=user_ratings)

@app.route('/movies')
def movie_list():
    """Show list of movies"""

    movies = db.session.query(Movie).order_by(Movie.title).all()

    return render_template('movie_list.html', movies=movies)

@app.route('/movie_details/<movie_id>')
def show_movie_details(movie_id):
    """Show movie details"""

    current_movie = Movie.query.get(movie_id)

    title = current_movie.title
    released_at = current_movie.released_at
    url = current_movie.imdb_url
    ratings = current_movie.ratings

    movie_ratings = []

    for item in ratings:
        score =item.score
        movie_ratings.append(score)

    average_score = sum(movie_ratings) / len(movie_ratings)

    return render_template('movie_details.html', title=title, released_at=released_at, url=url, movie_ratings= movie_ratings,
                            average_score=average_score)


@app.route('/login')
def login_user():
    """Allows user to input name and password"""


    return render_template('login_form.html')

@app.route('/process_login', methods=['POST'])
def process_login():
    """Checks if user already exists and allows them to login"""

    user_email = request.form.get('email')
    password = request.form.get('password')

    user_exists = User.query.filter_by(email=user_email).first() 

    if user_exists != None and user_exists.password == password:
        flash('Successfully logged in!')
        session['logged_in'] = user_email
        return redirect('/')
    elif user_exists != None and user_exists.password != password:
        flash('Incorrect password. Please reenter.')
        return redirect('/login')
    else:
        flash('User account not found. Please register.')
        return redirect('/login')

@app.route('/logout')
def process_logout():
    """Log out user"""

    del session['logged_in']
    flash("You are successfully logged out!")

    return redirect('/')



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
