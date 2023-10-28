import os
import flaskblog
from flask_admin import Admin 
from flask import Flask, abort 
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

admin = Admin(app,name = 'Control Panel')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER']= 'flaskblog/static/images'
db = SQLAlchemy(app)
migrate = Migrate(app,db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info' 

from flaskblog import routes


FLASK_APP=flaskblog