import os

class Config:
    SECRET_KEY = 'your-secret-key-here-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///union.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # مجلدات التحميل
    UPLOAD_FOLDER = 'static/images/uploads'
    PDF_FOLDER = 'static/files'
    
    # إنشاء المجلدات تلقائياً
    @classmethod
    def init_app(cls, app):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)
        print("✅ Upload folders created successfully")