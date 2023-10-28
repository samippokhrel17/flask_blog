from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from flaskblog import db, login_manager, admin
from flask_login import UserMixin, current_user
from flask import Flask, abort, flash, redirect, url_for, render_template
# from flaskblog.models import Image


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)
    category_permission = db.relationship(
        'CategoryPermission', backref='user', lazy=True)

    def __repr__(self):  # object to string representation.
        return f"{self.username}({self.id})"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class CategoryPermission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'category.id'), nullable=False)
    category = db.relationship('Category',backref='category_permissions')
    # def category_name(self):
    #     return "sasdsadsa"
    # self.category.name if self.category else None

    def __repr__(self):
        return  f"CategoryPermission(user_id: {self.user_id}, category_id: {self.category_id})"

# for table creation in DB


# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     image_file = db.Column(db.String(20), nullable=False,
#                            default='default.jpg')
#     password = db.Column(db.String(60), nullable=False)
#     posts = db.relationship('Post', backref='author', lazy=True)
#     is_admin = db.Column(db.Boolean, default=False)
#     category_permission = db.relationship(
#         'CategoryPermission', backref='user', lazy=True)

#     def __repr__(self):  # object to string representation.
#         return f"{self.username}({self.id})"


# class Controller(ModelView):
#     column_hide_backrefs=False
#     def is_accessible(self):
#         if current_user.is_authenticated and current_user.is_admin:
#             return True
#         else:
#             # abort(404)
#             flash("Only Admin can Acces this page")
#         return redirect(url_for('home'))

        # return current_user.is_authenticateds

    # def not_auth(self):
    #     return"Access Denied"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True, unique=True)
    posts = db.relationship('Post', backref='post', lazy=True)

    def __repr__(self):
        return self.name

# class Permission(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=True, unique=True)
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'category.id'), nullable=False)
    category = db.relationship('Category',backref='post')
    user = db.relationship('User',backref='post')
    image = db.relationship('Image', backref='post', lazy=True)
    #permission= db.Column(db.Integer, db.ForeignKey('permission.id'), nullable=False)
    # category=db.relationship('Category',backref='post',lazy=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted},'{self.is_published}','{self.is_published}''{self.category_id}')"


class CategoryPermissionView(ModelView):
    column_hide_backrefs = False
    column_list = ('user', 'category') #user catagory ra post hane !!categoty permission mile na

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def get_query(self):
        print('Querying CategoryPermission records')
        return super(CategoryPermissionView,self).get_query()
    
    

class PostView(ModelView):
    column_hide_backrefs = False
    column_list = ('title', 'date_posted','content','category','user','is_published') 
    


    def is_accessible(self):
        #print(current_user.category_permission[0].category)
        return current_user.is_authenticated and current_user.is_admin
    

    # def get_query(self):
    #     query = super(PostView, self).get_query()
    #     print(query)
    #     query = query.filter_by(category_id=current_user.category_permission[0].category.id)
    #     print(query)
    #     return query
    
    # def get_query(self):
    #     print('Querying CategoryPermission records')
    #     return super(CategoryPermissionView,self).get_query()    



# Define a function to check category permissions
# Define a function to check category permissions


def has_category_permission(user, category_name):
    for permission in user.category_permissions:
        if permission.category_name == category_name:
            return True
    return False


# admin.add_view(Controller(User, db.session))
# admin.add_view(Controller(Category, db.session))
# admin.add_view(Controller(Post, db.session))

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)

    def __repr__(self):
        return self.filename
    
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    create = db.Column(db.Boolean,default=False)
    read = db.Column(db.Boolean,default=False)
    update = db.Column(db.Boolean,default=False)
    delete = db.Column(db.Boolean,default=False)
    category = db.relationship('Category',backref='role')
    user = db.relationship('User',backref='role')

class RoleView(ModelView):
    column_hide_backrefs = False
    column_list = ('user', 'category','create','read','update','delete') #user catagory ra post hane !!categoty permission mile na

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    # def get_query(self):
    #     print('Querying CategoryPermission records')
    #     return super(CategoryPermissionView,self).get_query()
    



    






# Add Flask-Admin views for your models
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(PostView(Post, db.session))
# admin.add_view(ModelView(CategoryPermission, db.session))
admin.add_view(CategoryPermissionView(CategoryPermission, db.session))
admin.add_view(ModelView(Image, db.session))
admin.add_view(RoleView(Role, db.session))