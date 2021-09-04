from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User(primary_key(id), username, email, avatar, hash_password, relationship with Post table)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

# Post(primary_ket(id), title, current_time, content to display, FOREIGN_KEY(user_id))
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content  = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Content(primary_ket(id), current_time, content to display, FOREIGN_KEY(user_id), FOREIGN_KEY(post_id))
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content  = db.Column(db.Text, nullable=False)