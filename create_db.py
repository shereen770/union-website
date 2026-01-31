# create_db.py
from app import app, db   # استورد التطبيق والـ db من app.py

with app.app_context():
    db.create_all()
    print("site.db created successfully ✅")
