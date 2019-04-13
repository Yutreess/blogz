from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

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

@app.route('/blog', methods=['POST', 'GET'])
def index():
  

  blogs = Blog.query.all()
  return render_template("blog.html", title="Build-A-Blog", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def add_post():

  if request.method == 'POST':
    post_title = request.form['title']
    post_body = request.form['body']
    new_post = Blog(post_title, post_body)
    db.session.add(new_post)
    db.session.commit()

  return render_template("add-post.html", title="Add Post")

if __name__ == "__main__":
  app.run()