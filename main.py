import os
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin  
)
from urllib.parse import urlparse
from config import Config
from forms import RegisterForm, LoginForm, PostForm, CommentForm
from models import db, User, Post, Comment 

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id)) 

with app.app_context():
    db.create_all()
    print("Database tables created (if they didn't exist).")


def is_safe_url(target):
    """Validate that the target URL is safe for redirect"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(db.select(Post).order_by(Post.date_posted.desc()), page=page, per_page=10)
    return render_template('index.html', posts=posts, title="Home")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = db.session.scalar(db.select(User).where(User.username == form.username.data))
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'warning')
            return render_template('register.html', form=form, title="Register")

        existing_email = db.session.scalar(db.select(User).where(User.email == form.email.data))
        if existing_email:
            flash('Email already registered. Please use a different one.', 'warning')
            return render_template('register.html', form=form, title="Register")

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data) 
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title="Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == form.username.data))
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            # Validate the next URL to prevent open redirect attacks
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html', form=form, title="Login")

@app.route('/logout')
@login_required 
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/post/new', methods=['GET', 'POST'])
@login_required 
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created!', 'success')
        return redirect(url_for('view_post', post_id=post.id))
    return render_template('post.html', form=form, title="New Post", post=None, comments=None)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        abort(404) 

    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must be logged in to comment.', 'warning')
            return redirect(url_for('login', next=url_for('view_post', post_id=post_id)))

        comment = Comment(content=form.content.data, post=post, user=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added!', 'success')
        return redirect(url_for('view_post', post_id=post.id))

    comments = db.session.scalars(
        db.select(Comment)
        .where(Comment.post_id == post.id)
        .order_by(Comment.date_posted.desc())
    ).all()

    return render_template('post.html', post=post, comments=comments, form=form, title=post.title)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit an existing post (author only)"""
    post = db.session.get(Post, post_id)
    if not post:
        abort(404)
    
    # Check authorization - only author can edit
    if post.author != current_user:
        abort(403)  # Forbidden
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('view_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    
    return render_template('post.html', form=form, title="Edit Post", post=post, comments=None)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a post (author only)"""
    post = db.session.get(Post, post_id)
    if not post:
        abort(404)
    
    # Check authorization - only author can delete
    if post.author != current_user:
        abort(403)  # Forbidden
    
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/user/<string:username>')
def user_posts(username):
    """View all posts by a specific user"""
    user = db.session.scalar(db.select(User).where(User.username == username))
    if not user:
        abort(404)
    
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(
        db.select(Post).where(Post.author == user).order_by(Post.date_posted.desc()),
        page=page,
        per_page=10
    )
    return render_template('user_posts.html', user=user, posts=posts, title=f"{username}'s Posts")


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    # Use environment variable for debug mode
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode)
