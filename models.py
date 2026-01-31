from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# ======================
# User
# ======================

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)

    date_created = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # 🔐 Set password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 🔐 Check password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# ======================
# Activity
# ======================

class Activity(db.Model):
    __tablename__ = 'activity'

    id = db.Column(db.Integer, primary_key=True)

    title_en = db.Column(db.String(255), nullable=False)
    title_ar = db.Column(db.String(255), nullable=False)
    title_ku = db.Column(db.String(255))
    title_de = db.Column(db.String(255))

    description_en = db.Column(db.Text, nullable=False)
    description_ar = db.Column(db.Text, nullable=False)
    description_ku = db.Column(db.Text)
    description_de = db.Column(db.Text)

    category = db.Column(db.String(100))

    # multiple images separated by comma
    images = db.Column(db.Text)

    date_posted = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f'<Activity {self.title_en}>'


# ======================
# Article
# ======================

class Article(db.Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True)

    title_en = db.Column(db.String(255), nullable=False)
    title_ar = db.Column(db.String(255), nullable=False)
    title_ku = db.Column(db.String(255))
    title_de = db.Column(db.String(255))

    content_en = db.Column(db.Text, nullable=False)
    content_ar = db.Column(db.Text, nullable=False)
    content_ku = db.Column(db.Text)
    content_de = db.Column(db.Text)

    author_image = db.Column(db.String(255))

    date_posted = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f'<Article {self.title_en}>'


# ======================
# Breaking News
# ======================

class BreakingNews(db.Model):
    __tablename__ = 'breaking_news'

    id = db.Column(db.Integer, primary_key=True)

    title_en = db.Column(db.String(255), nullable=False)
    title_ar = db.Column(db.String(255), nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    date_posted = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f'<BreakingNews {self.title_en}>'
