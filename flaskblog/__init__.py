from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_manager


app = Flask(__name__)

app.config['SECRET_KEY'] = '3df099bc6c2ed4455226eeb5d30d82bbdfce647d'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
login_manager  = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'danger'


from flaskblog import routes