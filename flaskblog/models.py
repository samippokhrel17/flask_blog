from datetime import datetime
from flask import Flask, abort , flash , redirect , url_for,render_template
from flaskblog import db, login_manager, admin
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView 


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#for table creation in DB
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    is_admin = db.Column(db.Boolean, default=False) 



    def __repr__(self):  #object to string representation.
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"



class Controller(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        else:
            # abort(404)
            flash("Only Admin can Acces this page")
        return redirect(url_for('home')) 
    


        #return current_user.is_authenticated
    
    def not_auth(self):
        return"Access Denied"


admin.add_view(Controller(User, db.session))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted},'{self.is_published}','{self.is_published}')"
    