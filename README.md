# Wibu Hall

## Author
Bao Tran <baotran1109.hnue@gmail.com>
## Requirements
Read and install from the `requirements.txt` by using
```
$ pip install -r requirements.txt
```
## Description
This is a simple web app that built with **Python & Flask**

This web app contains 4 difference methods: **CRUD** (more detail below)
```
CREATE
READ
UPDATE
DELETE
```
### 1. Creat:
Using `SQLALCHEMY` to create and store objects in two models 


I use **sqlite3** for this project `app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'`
- **User**
```
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
``` 
- **Post**
```
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content  = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```
Using `backref='author'` in **User** to linked with the **Post** by to `"callback"` when you want to call the User's attribute
- **Table Schema**
```
CREATE TABLE user (
        id INTEGER NOT NULL, 
        username VARCHAR(20) NOT NULL,   
        email VARCHAR(100) NOT NULL,     
        image_file VARCHAR(20) NOT NULL, 
        password VARCHAR(60) NOT NULL,   
        PRIMARY KEY (id), 
        UNIQUE (username), 
        UNIQUE (email)
);
CREATE TABLE post (
        id INTEGER NOT NULL,
        title VARCHAR(100) NOT NULL,
        time_stamp DATETIME NOT NULL,
        content TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(user_id) REFERENCES user (id)
);
```
### 2. Read:
Read the data from **blog.db** that have something similar to this
```sh
id  username  email              image_file            password
--  --------  -----------------  --------------------  ------------------------------------------------------------
1   Katty     example@gmail.com  6cf850898615d110.png  $2b$12$piG8ZN/FjYQ8yIRVK.xVgOuTa7AyRqTvXsBtLmZx7sXaPFjASn0gi
```
We store the `hash_password` by using **flask_bcryp**.

Read information from the Database and compare with the user's input to verify the current user by something like this
```
if not password:
    flash("Must provide password", "danger")
    return redirect("/profile")
``` 
### 3. Update
We can also modify the user's information in Database

They can upload their own image, the OS will re-render the image and store its in `flaskblog\static\profile_photos`
```
# 8 Bytes mean to unchanged file type (PNG, JPEG,...) when save
# spiltext to return Filename & Extension -> use 2 variables
# _ dont use variable
# root_path to save in the same path that we want

def save_avatar(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_photos', picture_fn)
    form_picture.save(picture_path)

    return picture_fn
```
### 4. Delete
Delete user's information and their posts. Make sure that the user has to login first
```
@login_required
```
