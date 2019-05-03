# Flask FUnctionality
from flask import request, redirect, render_template, session, flash

# Objects and app from local files
from models import User, Blog
from app import app, db

# Regular Expression
import re

# Hash passwords and check hashes
from hash_utils import check_hash, hash_password

# Default to signup or login page if user is not logged in
@app.before_request
def require_login():
  allowed_routes = ['login', 'check_login',
    'signup', 'check_signup',
    'list_blogs', 'index']
  if request.endpoint not in allowed_routes \
    and 'username' not in session \
    and '/static/' not in request.path:

    flash("You need to be logged in to create a post or log out")
    return redirect('/login')

# Begin /blog

# Main Blog page
@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
  # Find Query parameters and arguments
  blog_id = request.args.get('id')
  userId = request.args.get('userId')

  # Find blog id query parameter, and load the blog post
  if blog_id:
    blog = Blog.query.filter_by(id=blog_id).all()
    return render_template("post.html", blog=blog)

  # Find userId, and load posts by user
  elif userId:
    blogs = Blog.query.filter_by(owner_id=userId).all()
    author_username = User.query.filter_by(id=userId).first().username
    return render_template("blog.html", title="Blogz", blogs=blogs,
    page_header="Blogs by {0}".format(author_username))

  # If there's no query parameter, load all blog posts in a list
  else:
    blogs = Blog.query.order_by(Blog.post_time.desc()).all()
    return render_template("blog.html", title="Blogz", page_header="Blog Entries",
    blogs=blogs)

# End /blog

# Begin /

# Index or "Home" Page
@app.route('/', methods=['POST', 'GET'])
def index():
  # Get all usernames from all accounts
  users = User.query.order_by(User.username.asc()).all()
  return render_template("index.html", users=users)

# End /

# Begin /like
@app.route('/like', methods=['POST'])
def like_post():
  # Find id of blog post
  blog_id = request.form['blog_id']
  # Find post to like
  liked_post = Blog.query.filter_by(id=blog_id).first()
  # Add like to post
  liked_post.likes += 1
  # Add and commit to db session
  db.session.add(liked_post)
  db.session.commit()

  return redirect('/blog?id={0}'.format(blog_id))


# End /like

# Begin /login

# Render Login Page
@app.route('/login', methods=['GET'])
def login():
  return render_template("login.html", title="Login")

# Process Login Form
@app.route('/login', methods=['POST'])
def check_login():
  # Get Username and password from the form
  username = request.form['username']
  password = request.form['password']
  uname_error = ''
  password_error = ''

  # Get User from database
  user = User.query.filter_by(username=username).first()
 
  # If username and password are correct as in the database
  if user and check_hash(password, user.password_hash):
    session['username'] = username
    flash("Logged in as " + username)
  # Check if username is empty
  elif not username:
    uname_error = 'Please enter a Username'
  # If username is in database, but incorrect password
  elif user and user.password != password:
    password_error = 'Incorrect password'
  # If username is not in database
  elif not user:
    uname_error = 'Username does not exist'

  # Check for any previous errors. Rerender if present.
  if uname_error or password_error:
    return render_template("login.html", title="Login",
    username=username,
    uname_error=uname_error, password_error=password_error)
  # If no error messages are present, good to go.
  else:
    return redirect('/newpost')

# End /login

# Begin /logout

# Log out
@app.route('/logout')
def logout():
  if session['username']:
    del session['username']
    flash("Logged Out!")
    return redirect('/blog')

# End /logout

# Begin /signup

# Render Signup Page
@app.route('/signup')
def signup():
  return render_template("signup.html", title="Signup")

# Process Signup Form
@app.route('/signup', methods=['POST'])
def check_signup():
  # Get Form input
  username = request.form['username']
  password = request.form['password']
  verified_password = request.form['verify-password']
  uname_error = ''
  password_error = ''
  verify_password_error = ''

  # In case username alrady exists, query for that username
  existing_user = User.query.filter_by(username=username).first()

  # USERNAME CHECKS

  # Check if Username is empty
  if not username:
    uname_error = 'Please enter a Username'

  # Check if username is between 3 and 20 characters 
  elif re.match("^.{3,20}$", username) == None:
    uname_error = 'Username must be between 3 and 20 characters long'

  # Check if username has any spaces
  elif re.search("^\s", username) != None:
    uname_error = 'Username cannot contain spaces'

  # Check if username has special characters
  elif re.match("^[a-zA-Z0-9]{3,20}$", username) == None:
    uname_error = "Username can only contain letters and/or numbers."

  # Check if username already exists
  elif existing_user:
    uname_error = "Username already exists"

  # END USERNAME CHECKS

  # PASSWORD CHECKS

  # Check if password is empty
  if not password:
    password_error = 'Please enter a password and retype it below'
  # Check if password has spaces
  elif re.search("^\s", password) != None:
    password_error = "Password cannot contain spaces"
  # Check if password is in the character range
  elif re.match("^.{3,20}$", password) == None:
    password_error = "Password must be between 3 and 20 characters"

  # Check if verified password is empty
  if not verified_password:
    verify_password_error = 'Remember to retype the password from above'
    
  # Check if verified password has spaces
  elif re.search("^\s", verified_password) != None:
    verify_password_error = "Password cannot contain spaces"

  # Check if verified password is in the character range
  elif re.match("^.{3,20}$", verified_password) == None:
    verify_password_error = "Password must be between 3 and 20 characters"

  # Check if passwords match
  if password != verified_password:
    verify_password_error = ''
    password_error = 'Passwords do not match'

  # END PASSWORD CHECKS

  # If any errors are present, rerender signup page with messages
  if uname_error or password_error or verify_password_error:
    return render_template("signup.html", title="Sign Up",
    username=username, uname_error=uname_error,
    password_error=password_error, verify_password_error=verify_password_error)
  # If no errors are present, good to go
  else:
    # Add User to database
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()

    # Remember user's login
    session['username'] = username
    flash("Logged in as " + username)
    return redirect('/newpost')

# End /signup

# /newpost

# New Post Form
@app.route('/newpost', methods=['GET'])
def render_form():
  return render_template("add-post.html", title="Add Post")

# Process New Post Form
@app.route('/newpost', methods=['POST'])
def add_post():
  post_title = request.form['title']
  post_body = request.form['body']
  title_error = ''
  body_error = ''

  # Find Username of poster
  owner = User.query.filter_by(username=session['username']).first()

  # Check if title is empty
  if not post_title:
    title_error = "Please enter a post title"
  
  # Check if body is empty
  if not post_body:
    body_error = "Please enter body text for your post"

  # If there's any errors, rerender the form with the messages
  if title_error or body_error:
    return render_template("add-post.html", title="Add Post", 
    title_error=title_error, body_error=body_error, 
    post_title=post_title, post_body=post_body)

  # If there's no errors, good to add the post
  else:
    # Add new post to the Database
    new_post = Blog(post_title, post_body, owner)
    db.session.add(new_post)
    db.session.commit()

    # Redirect to that blog post
    return redirect("/blog?id={0}".format(new_post.id))

# Run app

if __name__ == "__main__":
  app.run()