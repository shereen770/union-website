from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from models import db, User
from routes import init_routes
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)  # ✅ مهم جدًا

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)
print("✅ Upload folders created successfully")

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('adminpass')
        db.session.add(admin)
        db.session.commit()

    init_routes(app, mail)

if __name__ == '__main__':
    app.run(debug=False)
