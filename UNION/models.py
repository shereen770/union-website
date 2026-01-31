from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.String(100), nullable=False)
    title_ar = db.Column(db.String(100), nullable=False)
    title_ku = db.Column(db.String(100), nullable=True)
    title_de = db.Column(db.String(100), nullable=True)
    description_en = db.Column(db.Text, nullable=False)
    description_ar = db.Column(db.Text, nullable=False)
    description_ku = db.Column(db.Text, nullable=True)
    description_de = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    images = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Activity {self.title_en}>'

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.String(100), nullable=False)
    title_ar = db.Column(db.String(100), nullable=False)
    title_ku = db.Column(db.String(100), nullable=True)
    title_de = db.Column(db.String(100), nullable=True)
    content_en = db.Column(db.Text, nullable=False)
    content_ar = db.Column(db.Text, nullable=False)
    content_ku = db.Column(db.Text, nullable=True)
    content_de = db.Column(db.Text, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author_image = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Article {self.title_en}>'

class BreakingNews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_ar = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    title_ku = db.Column(db.String(200), nullable=True)
    title_de = db.Column(db.String(200), nullable=True)
    content_ar = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=False)
    content_ku = db.Column(db.Text, nullable=True)
    content_de = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<BreakingNews {self.id}: {self.title_ar}>'