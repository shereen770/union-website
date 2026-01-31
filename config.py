import os


class Config:
    SECRET_KEY = 'your-secret-key-here-change-in-production'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///union.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = 'static/images/uploads'
    PDF_FOLDER = 'static/files'

    # ====================== Mail Config ======================
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = 'your_email@gmail.com'      # ✉️ ضع إيميلك
    MAIL_PASSWORD = 'APP_PASSWORD_HERE'         # 🔑 App Password
    MAIL_DEFAULT_SENDER = 'your_email@gmail.com'

    @classmethod
    def init_app(cls, app):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)
        print("✅ Upload folders created successfully")
