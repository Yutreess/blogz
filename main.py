from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import re

# App Initialization
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://build-a-blog:420Hornze!@localhost:8889/build-a-blog"
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# Blog Class
class Blog(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80))
  body = db.Column(db.String(300))

  def __init__(self, title, body):
    self.title = title
    self.body = body

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
    blogs = Blog.query.all()
    return render_template("blog.html", title="Build-A-Blog", blogs=blogs)

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