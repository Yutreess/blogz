from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

# App Initialization
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://blogz:420Hornze!@localhost:8889/blogz"
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'YeetusYanLeetus'
db = SQLAlchemy(app)

# Blog Class
class Blog(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80))
  body = db.Column(db.String(300))
  post_time = db.Column(db.DateTime)
  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __init__(self, title, body, post_time=None):
    self.title = title
    if post_time is None:
      post_time = datetime.utcnow()
    self.post_time = post_time
    self.body = body

# User Class
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80))
  password = db.Column(db.String(30))
  blogs = db.relationship('Blog', backref='owner')

  def __init__(self, username, password):
    self.username = username
    self.password = password

# Main Blog page
@app.route('/blog', methods=['POST', 'GET'])
def index():
  blog_id = request.args.get('id')

  # Find blog id query parameter, and load the blog post
  if blog_id:
    blog = Blog.query.filter_by(id=blog_id).all()
    return render_template("post.html", blog=blog)
  # If there's no query parameter, load all blog posts in a list
  else:
    blogs = Blog.query.order_by(Blog.post_time.desc()).all()
    return render_template("blog.html", title="Blogz", blogs=blogs)

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
  if user and user.password == password:
    session['username'] = username
    flash("Logged in!")
  # If username is in database, but incorrect password
  elif user and user.password != password:
    password_error = 'Incorrect password'
  # If username is not in database
  elif not user:
    uname_error = 'Username does not exist'

  # Check for any previous errors. Rerender if present.
  if uname_error or password_error:
    return redirect("/login", title="Login",
    username=username,
    uname_error=uname_error, password_error=password_error)
  # If no error messages are present, good to go.
  else:
    return redirect('/newpost')



# Render Signup Page
@app.route('/signup')
def signup():
  return render_template("signup.html", title="Signup")

# Process Signup Form
@app.route('/signup', methods=['POST'])
# TODO - write function "def check_signup():" to validate form
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
    flash("Logged in!")
    return redirect('/newpost')

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
    new_post = Blog(post_title, post_body)
    db.session.add(new_post)
    db.session.commit()
    # Redirect to that blog post
    return redirect("/blog?id={0}".format(new_post.id))

  

if __name__ == "__main__":
  app.run()