# Import python files for using dates and times
from datetime import datetime

# Import database object from app.py
from app import db

# Hashing passwords
from hash_utils import hash_password

# Blog Class
class Blog(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80))
  body = db.Column(db.String(300))
  post_time = db.Column(db.DateTime)
  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  likes = db.Column(db.Integer)

  def __init__(self, title, body, owner, post_time=None):
    self.title = title
    if post_time is None:
      post_time = datetime.utcnow()
    self.post_time = post_time
    self.body = body
    self.owner = owner
    self.likes = 0

# User Class
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80))
  password_hash = db.Column(db.String(80))
  blogs = db.relationship('Blog', backref='owner')

  def __init__(self, username, password):
    self.username = username
    self.password_hash = hash_password(password)
