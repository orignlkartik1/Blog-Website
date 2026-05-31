from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone # Use timezone-aware datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True) # Added index
    password_hash = db.Column(db.String(256), nullable=False) # Store hash, not raw password

    posts = db.relationship('Post', back_populates='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    author = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Post {self.title}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    # Use timezone.utc for consistency
    date_posted = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    post = db.relationship('Post', back_populates='comments')
    user = db.relationship('User', back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.id} on Post {self.post_id}>'