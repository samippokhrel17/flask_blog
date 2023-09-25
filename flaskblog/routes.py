import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session 
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post, Category,Image as Photo
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename




@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.filter_by(is_published=True)
    categories = Category.query.all()
    return render_template('home.html', posts=posts,categories=categories)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


# @app.route("/post/new", methods=['GET', 'POST'])
# @login_required
# def new_post():
#     form = PostForm()

#     categories = Category.query.all()
#     form.category_id.choices = [(category.id, category.name) for category in categories]

#     #form.category.choices = [(category.id, category.name) for category in Category.query.all()]

#     if form.validate_on_submit():
#         # default_category_id = 1
#         post = Post(title=form.title.data, content=form.content.data, author=current_user, is_published=form.is_published.data, category_id=form.category_id.data)

#         db.session.add(post)
#         db.session.commit()
#         flash('Your post has been created!', 'success')
#         return redirect(url_for('home'))
#     return render_template('create_post.html', title='New Post',
#                            form=form, legend='New Post')


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()

    # categories = Category.query.all()
    # form.category_id.choices = [(category.id, category.name) for category in categories]

    if form.validate_on_submit():
        
        if len(current_user.category_permission) == 0:
            return redirect('/')
        
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
            is_published=form.is_published.data,
            #category_id=1
            category_id= current_user.category_permission[0].category.id 

        )
        try:
           db.session.add(post)
           db.session.commit()
           image = form.image.data
           if image:
                print("oddu")
                print(post.id)
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save the image to a folder
                
                # Create a new Image record and associate it with the post
                image_record = Photo(filename=filename, post=post)
                db.session.add(image_record)
                db.session.commit()
                print("123helo")

        except Exception as e:
            print(e)


        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', title='New Post', form=form, legend='New Post')



@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id) #we will get post id , if not return errror
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/table")
@login_required
def table():
    # is_admin = current_user.is_admin
    users= User.query.all()
    # if is_admin== True:
    return render_template('table.html', title='Table',data=users)  
    # else:
    #     flash("Sorry you must be the admin to access Admin Page") 
    #     return redirect(url_for('home'))




# @app.route("/creat_admin", methods=['GET', 'POST'])
# def creat_admin():
#     if request.method == 'POST':
#         hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
#         new_user=User(email=request.form['email'],password=hashed_password,username=request.form['username'],is_admin=True)
#         db.session.add(new_user)
#         db.session.commit()
#         return "Admin Account Created"
    
#     return render_template("admin_signup.html")





@app.route("/creat_admin", methods=['GET', 'POST'])
@login_required  # Add the login_required decorator
def creat_admin():
    # Check if the current user is an admin
    
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))  # Redirect to another page (e.g., home page) or handle the access denial

    if request.method == 'POST':
        hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(email=request.form['email'], password=hashed_password, username=request.form['username'], is_admin=True)
        db.session.add(new_user)
        db.session.commit()
        print("hello")
        flash("Admin Account Created", "success")
        return redirect(url_for('home'))  # Redirect to another page after successful creation

    return render_template("creat_admin.html")

# Example route that checks category permissions
@app.route('/category/<category_name>')
def category_content(category_name):
    if has_category_permission(current_user, category_name):
        # User has permission to access the category
        # Your logic here
        return render_template('category_content.html', category_name=category_name)
    else:
        flash("You do not have permission to access this category.")
        return redirect(url_for('home'))

# Route to handle user input for adding category permissions
@app.route('/add_category_permission', methods=['POST'])
def add_category_permission():
    category_name = request.form.get('category_name')
    
    # Ensure that the category_name is valid and not empty
    
    if category_name:
        # Add the category permission to the current user
        permission = CategoryPermission(user_id=current_user.id, category_name=category_name)
        db.session.add(permission)
        db.session.commit()
        flash(f'Permission added for category: {category_name}')
    else:
        flash('Invalid category name')

    return redirect(url_for('home'))




