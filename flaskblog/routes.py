from operator import pos
import os
from flask import send_from_directory
import secrets
from flask import render_template, url_for, redirect, request, flash, abort
from flask_bcrypt import check_password_hash, generate_password_hash
from flaskblog import app, db
from flaskblog.models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
###---------------------------------------DEFAULT--------------------------------------------###
@app.route("/")
def home():
    # Render Hompage
    POSTS = Post.query.all()
    return render_template('home.html', posts=POSTS)

###---------------------------------------ABOUT ME---------------------------------------------###
@app.route("/about")
@login_required
def about():
    return render_template('about.html', title='About')

###---------------------------------------REGISTER---------------------------------------------###
@app.route("/register", methods=["GET", "POST"])
def register():
    # If user already login -> auto login 
    if current_user.is_authenticated:
        return redirect("/")
    # Render Register Page
    if request.method == "GET":
        return render_template('register.html', title='Register')

    # Get User input
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm = request.form.get("confirmation")

    # Recall that Name or Mail are already exist or not
    check_name = User.query.filter_by(username=request.form.get("username")).first()
    check_mail = User.query.filter_by(email=request.form.get("email")).first()

    if check_name:
        flash("Username already taken", "danger")
        return redirect("/register")
    elif check_mail:
        flash("Email already taken", "danger")
        return redirect("/register")
    elif not username:
        flash("Must provide username", "danger")
        return redirect("/register")
    elif not email:
        flash("Must provide email", "danger")
        return redirect("/register")
    elif not password:
        flash("Must provide password", "danger")
        return redirect("/register")
    elif password != confirm:
        flash("Password do not match", "danger")
        return redirect("/register")

    ## Update User Data to DB
    new_user = User(username=username, email=email,password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    flash(f"Success registerd as {username}", "success")
    return render_template("login.html", title="Login")

###---------------------------------------LOGIN---------------------------------------------###
@app.route("/login", methods=["POST", "GET"])
def login():
    # If user already login -> auto login 
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
    # User Authentication
        email = request.form.get("email")
        password = request.form.get("password")

        ## Pass an object that required, else NONE
        user = User.query.filter_by(email=request.form.get("email")).first()

        ### Verified Email & Hash_Password
        if not user:    
            flash("Invalid Email or Password", "danger")
            return redirect("/login")
        elif not check_password_hash(user.password, request.form.get("password")):
            flash("Invalid Email or Password", "danger")
            return redirect("/login")
        elif not email:
            flash("Must enter email", "danger")
            return redirect("/login")
        elif not password:
            flash("Must enter password", "danger")
            return redirect("/login")

        flash(f"Success Login as {request.form.get('email')}", "success")
        login_user(user, remember=request.form.get('remember'))
        return redirect("/")

    return render_template('login.html', title="Login")

###---------------------------------------LOGOUT---------------------------------------------###
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


# 8 Bytes mean to unchanged file type (PNG, JPEG,...) when save
# spiltext to return Filename & Extension -> use 2 variables
# _ dont use variable
# root_path to save in the same path that we wants
def save_avatar(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_photos', picture_fn)
    form_picture.save(picture_path)

    return picture_fn

###---------------------------------------UPDATE PROFILE---------------------------------------------###
@app.route("/profile", methods=["POST", "GET"])
@login_required
def profile():
    if request.method == "GET":
        avatar = url_for('static', filename='profile_photos/' + current_user.image_file)
        return render_template("profile.html", title="My Profile", avatar=avatar)
    
    username = request.form.get("username")
    password = request.form.get("password")
    confirm = request.form.get("confirmation")
    image = request.files['profile_avatar']

    # Authenticated User Information

    if not password:
        flash("Must provide password", "danger")
        return redirect("/profile")
    elif not check_password_hash(current_user.password, password):
        flash("Invalid password", "danger")
        return redirect("/profile")     
    elif password != confirm:
        flash("Password do not match", "danger")
        return redirect("/profile")
    
    # Update the record
    user = User.query.filter_by(username=current_user.username).first()
    if username:
        user.username = request.form.get("username")

    if image:
        picture_file = save_avatar(image)
        user.image_file = picture_file

    db.session.commit()

    flash("Update Profile Success", "success")
    return redirect("/profile")


###---------------------------------------DELETE PROFILE---------------------------------------------###
@app.route("/delete", methods=["POST", "GET"])
@login_required
def delete():
    if request.method == "POST":

        # Authenticated User
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        if not password:
            flash("Must provide password", "danger")
            return redirect("/delete")
        elif not check_password_hash(current_user.password, password):
            flash("Invalid password", "danger")
            return redirect("/delete") 
        elif password != confirm:
            flash("Password do not match", "danger")
            return redirect("/delete")

        # Remove User & Post from Database
        User.query.filter_by(id=current_user.id).delete()
        Post.query.filter_by(user_id=current_user.id).delete()
        Comment.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash("Oni-chan no Baka!", "danger")
        return redirect("/")


    return render_template("delete.html", title="Sayounara Oni-chan")

###---------------------------------------CREATE NEW POST---------------------------------------------###
@app.route("/post/new", methods=["POST", "GET"])
@login_required
def new_post():
    if request.method == "POST":
        post_title = request.form.get("post_title")
        post_content = request.form.get("post_content")

        # Add new post to DB
        new_post = Post(title=post_title,content=post_content,author=current_user)
        db.session.add(new_post)
        db.session.commit()

        flash("Post Success","success")
        return redirect("/")

    return render_template("create_post.html", title="Create Post")


###---------------------------------------VIEW POSTS---------------------------------------------###
# See other posts
@app.route("/profile/<int:user_id>")
@login_required
def user_profile(user_id):
    post = Post.query.filter_by(user_id=user_id).all()
    return render_template("post_user.html", posts=post)


###---------------------------------------UPDATE POST---------------------------------------------###
# Detect if user is trusted (have full control)
@app.route("/post/update/<int:post_id>", methods=["POST", "GET"])
@login_required
def update_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post.author != current_user:
        abort(403)
    if request.method == "GET":
        return render_template("update.html", post_id=post_id)
    
    new_title = request.form.get("post_title")
    new_content = request.form.get("post_content")

    # Update new post to DB
    post.title = new_title
    post.content = new_content
    db.session.commit()

    flash("Update Success", "success")
    return redirect(url_for('post', post_id = post.id))


###---------------------------------------DELETE USER POST---------------------------------------------###
# Detect if user is trusted (have full control)
@app.route("/post/delete/<int:post_id>", methods=["POST", "GET"])
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    Comment.query.filter_by(post_id=post_id).delete()
    if post.author != current_user:
        abort(403)
    
    # Update to DB
    db.session.delete(post)
    db.session.commit()

    flash("Successfully Deleted", "success")
    return redirect("/")
    


###---------------------------------------ADD USER COMMENT---------------------------------------------###
# Add comment function to the web app
@app.route("/post/<int:post_id>" , methods=["POST", "GET"])
@login_required
def post(post_id):
    if request.method == "POST":
        content = request.form.get("comment")
        new_comment = Comment(content=content, author=current_user, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment Success","success")
        return redirect(url_for('post', post_id = post_id))

    comment = Comment.query.filter_by(post_id=post_id).all()
    post = Post.query.filter_by(id=post_id).all()
    return render_template("post.html",posts=post, comments=comment)


###---------------------------------------DELETE USER COMMENT---------------------------------------------###
@app.route("/post/delete/comment/<int:comment_id>")
@login_required
def update_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    post_id = comment.post_id
    if comment.author != current_user:
        abort(403)
    
    db.session.delete(comment)
    db.session.commit()

    flash("Successfully Deleted", "success")
    return redirect(url_for('post', post_id = post_id))   



