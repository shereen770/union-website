from flask import Flask
from config import Config
from models import db, User, Activity, Article, BreakingNews
from routes import init_routes, login_manager

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات
db.init_app(app)

# إنشاء الجداول في context
with app.app_context():
    db.create_all()
    
    # التحقق من الجداول
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"✅ Database tables: {tables}")
    
    # التحقق المكثف من جدول الأخبار العاجلة
    if 'breaking_news' in tables:
        print("✅ BreakingNews table exists!")
        breaking_news_count = BreakingNews.query.count()
        print(f"📊 Current breaking news count: {breaking_news_count}")
        
        # إضافة خبر تجريبي إذا لم يكن هناك أخبار
        if breaking_news_count == 0:
            test_news = BreakingNews(
                title_ar="خبر عاجل تجريبي - النظام جاهز",
                title_en="Test Breaking News - System Ready", 
                content_ar="🎉 نظام الأخبار العاجلة يعمل الآن! يمكنك إضافة أخبار عاجلة جديدة من لوحة التحكم.",
                content_en="🎉 Breaking news system is now working! You can add new breaking news from the dashboard.",
                is_active=True
            )
            db.session.add(test_news)
            db.session.commit()
            print("✅ Test breaking news added!")
    else:
        print("❌ CRITICAL: BreakingNews table NOT found!")
        print("💡 Solution: Visit /fix_breaking_news to create the table")
    
    # إضافة مستخدم admin
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('adminpass')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created")
    
    print("🎉 Database initialization completed!")

# تهيئة باقي المكونات
login_manager.init_app(app)
init_routes(app)

if __name__ == '__main__':
    print("🚀 Starting Flask application...")
    print("🔧 Debug URLs available:")
    print("   - /debug_db - Check database status")
    print("   - /debug_breaking_news - Check breaking news")
    print("   - /fix_breaking_news - Fix breaking news issue")
    app.run(debug=True, host='0.0.0.0', port=5000)