from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime
from models import db, User, Activity, Article, BreakingNews
from translations import translations

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_routes(app):
    def get_lang_urls():
        try:
            args = dict(request.args)
            args.pop('lang', None)
            
            current_endpoint = request.endpoint or 'index'
            
            lang_urls = {}
            for lang in translations.keys():
                try:
                    if hasattr(request, 'view_args') and request.view_args:
                        view_args = dict(request.view_args)
                        view_args['lang'] = lang
                        lang_urls[lang] = url_for(current_endpoint, **view_args, **args)
                    else:
                        lang_urls[lang] = url_for(current_endpoint, lang=lang, **args)
                except:
                    lang_urls[lang] = url_for('index', lang=lang)
            return lang_urls
        except:
            return {lang: f"/?lang={lang}" for lang in translations.keys()}

    def get_trans():
        lang = session.get('lang', 'en')
        trans_dict = translations.get(lang, translations['en'])
        
        class TranslationDict:
            def __getitem__(self, key):
                if key in trans_dict:
                    return trans_dict[key]
                elif key in translations['en']:
                    return translations['en'][key]
                else:
                    return key
            
            def get(self, key, default=None):
                try:
                    return self[key]
                except:
                    return default if default is not None else key
        
        return TranslationDict()

    # ------------------- Debug Routes -------------------
    @app.route('/debug_database_file')
    def debug_database_file():
        """التحقق من ملف قاعدة البيانات الفعلي"""
        import os
        import sqlite3
        
        db_files = []
        for file in os.listdir('.'):
            if file.endswith('.db'):
                db_files.append({
                    'name': file,
                    'size': os.path.getsize(file),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # محاولة الاتصال بكل قاعدة بيانات
        db_connections = {}
        for db_file in db_files:
            try:
                conn = sqlite3.connect(db_file['name'])
                cursor = conn.cursor()
                
                # الحصول على الجداول
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [table[0] for table in cursor.fetchall()]
                
                # الحصول على عدد الأنشطة
                activities_count = 0
                if 'activity' in tables:
                    cursor.execute("SELECT COUNT(*) FROM activity;")
                    activities_count = cursor.fetchone()[0]
                
                db_connections[db_file['name']] = {
                    'tables': tables,
                    'activities_count': activities_count,
                    'connection': 'success'
                }
                conn.close()
            except Exception as e:
                db_connections[db_file['name']] = {
                    'connection': 'failed',
                    'error': str(e)
                }
        
        return {
            'database_files': db_files,
            'connections': db_connections,
            'current_directory': os.getcwd()
        }

    @app.route('/debug_activities')
    def debug_activities():
        """راوت مفصل لتصحيح الأنشطة"""
        try:
            # تحقق من وجود الجدول
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            # تحقق من عدد الأنشطة
            activities_count = Activity.query.count()
            activities = Activity.query.order_by(Activity.date_posted.desc()).all()
            
            result = {
                'database_tables': tables,
                'activities_count': activities_count,
                'activities': []
            }
            
            for activity in activities:
                result['activities'].append({
                    'id': activity.id,
                    'title_en': activity.title_en,
                    'title_ar': activity.title_ar,
                    'category': activity.category,
                    'date_posted': activity.date_posted.strftime('%Y-%m-%d %H:%M:%S'),
                    'images': activity.images,
                    'description_length_en': len(activity.description_en),
                    'description_length_ar': len(activity.description_ar)
                })
            
            return result
            
        except Exception as e:
            return {'error': str(e)}

    @app.route('/debug_breaking_news')
    def debug_breaking_news():
        """تصحيح مشاكل الأخبار العاجلة"""
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            breaking_news_count = BreakingNews.query.count()
            active_breaking_news = BreakingNews.query.filter_by(is_active=True).all()
            
            result = {
                'has_breaking_news_table': 'breaking_news' in tables,
                'all_tables': tables,
                'breaking_news_count': breaking_news_count,
                'active_breaking_news_count': len(active_breaking_news),
                'breaking_news_list': []
            }
            
            for news in BreakingNews.query.all():
                result['breaking_news_list'].append({
                    'id': news.id,
                    'title_ar': news.title_ar,
                    'title_en': news.title_en,
                    'is_active': news.is_active,
                    'date_posted': news.date_posted.strftime('%Y-%m-%d %H:%M:%S'),
                    'has_image': bool(news.image)
                })
                
            return result
            
        except Exception as e:
            return {'error': str(e), 'type': type(e).__name__}

    @app.route('/debug_db')
    def debug_db():
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            activities_count = Activity.query.count()
            articles_count = Article.query.count()
            users_count = User.query.count()
            breaking_news_count = BreakingNews.query.filter_by(is_active=True).count()
            
            return {
                'tables': tables,
                'activities_count': activities_count,
                'articles_count': articles_count,
                'users_count': users_count,
                'breaking_news_count': breaking_news_count,
                'has_activities_table': 'activity' in tables,
                'database_url': app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
            }
        except Exception as e:
            return {'error': str(e)}

    @app.route('/reset_db')
    def reset_db():
        """إعادة إنشاء الجداول (للتطوير فقط)"""
        try:
            # حذف الجداول وإعادة إنشائها
            db.drop_all()
            db.create_all()
            
            # إضافة مستخدم admin جديد
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('adminpass')
            db.session.add(admin)
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Database reset successfully',
                'tables_created': ['user', 'activity', 'article', 'breaking_news']
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    @app.route('/reset_db_with_breaking_news')
    def reset_db_with_breaking_news():
        """إعادة إنشاء الجداول مع تضمين الأخبار العاجلة (للتطوير فقط)"""
        try:
            # حذف الجداول وإعادة إنشائها
            db.drop_all()
            db.create_all()
            
            # إضافة مستخدم admin جديد
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('adminpass')
            db.session.add(admin)
            
            # إضافة مثال على خبر عاجل
            breaking_news = BreakingNews(
                title_ar="خبر عاجل تجريبي",
                title_en="Test Breaking News",
                content_ar="هذا خبر عاجل تجريبي للاختبار",
                content_en="This is a test breaking news",
                is_active=True
            )
            db.session.add(breaking_news)
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Database reset with Breaking News successfully',
                'tables_created': ['user', 'activity', 'article', 'breaking_news']
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # ------------------- Frontend Routes -------------------
    @app.route('/', methods=['GET'])
    def index():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        
        try:
            # جلب الأنشطة للعرض أسفل الكاروسيل (أحدث 6 أنشطة)
            activities = Activity.query.order_by(Activity.date_posted.desc()).limit(6).all()
            print(f"🔍 [INDEX] Loaded {len(activities)} activities for homepage")
            
            # جلب الأخبار العاجلة النشطة للكاروسيل (أحدث 5 أخبار)
            breaking_news = BreakingNews.query.filter_by(is_active=True).order_by(BreakingNews.date_posted.desc()).limit(5).all()
            print(f"🚨 [INDEX] Loaded {len(breaking_news)} active breaking news for carousel")
            
            # الأنشطة الأخيرة للعرض في الأقسام
            recent_activities = activities[:3] if activities else []
            
        except Exception as e:
            print(f"❌ [INDEX] Error loading data: {e}")
            print(f"🔍 [INDEX] Checking if BreakingNews table exists...")
            
            # التحقق من وجود الجدول
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"🔍 [INDEX] Database tables: {tables}")
            
            activities = []
            breaking_news = []
            recent_activities = []
            
        return render_template('index.html', 
                             trans=trans, 
                             activities=activities,
                             recent_activities=recent_activities, 
                             breaking_news=breaking_news,
                             lang=lang, 
                             lang_urls=get_lang_urls())

    @app.route('/activities', methods=['GET'])
    def activities():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        category = request.args.get('category')
        
        try:
            if category:
                acts = Activity.query.filter_by(category=category).order_by(Activity.date_posted.desc()).all()
                print(f"🔍 [ACTIVITIES] Loaded {len(acts)} activities for category: {category}")
            else:
                acts = Activity.query.order_by(Activity.date_posted.desc()).all()
                print(f"🔍 [ACTIVITIES] Loaded {len(acts)} total activities")
                
            # طباعة تفاصيل الأنشطة
            for i, act in enumerate(acts):
                print(f"   {i+1}. ID: {act.id}, Title: '{act.title_en}', Category: {act.category}")
                
        except Exception as e:
            print(f"❌ Error loading activities: {e}")
            acts = []
            
        return render_template('activities.html', 
                             trans=trans, 
                             activities=acts, 
                             category=category, 
                             lang=lang, 
                             lang_urls=get_lang_urls())

    @app.route('/articles', methods=['GET'])
    def articles():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        
        try:
            arts = Article.query.order_by(Article.date_posted.desc()).all()
            print(f"✅ Loaded {len(arts)} articles")
        except Exception as e:
            print(f"❌ Error loading articles: {e}")
            arts = []
            
        return render_template('articles.html', 
                             trans=trans, 
                             articles=arts, 
                             lang=lang, 
                             lang_urls=get_lang_urls())

    @app.route('/article/<int:id>', methods=['GET'])
    def article(id):
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        
        try:
            art = Article.query.get_or_404(id)
        except:
            flash('Article not found.', 'error')
            return redirect(url_for('articles'))
            
        return render_template('article.html', 
                             trans=trans, 
                             article=art, 
                             lang=lang, 
                             lang_urls=get_lang_urls())

    @app.route('/about')
    def about():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        return render_template('about.html', 
                             trans=trans, 
                             lang=lang, 
                             lang_urls=get_lang_urls())

    @app.route('/secretariat')
    def secretariat():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        return render_template('secretariat.html', 
                             trans=trans, 
                             lang=lang, 
                             lang_urls=get_lang_urls())

    @app.route('/bylaws')
    def bylaws():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        pdf_path = url_for('static', filename='files/bylaws.pdf')
        return render_template('bylaws.html', 
                             trans=trans, 
                             pdf_path=pdf_path, 
                             lang=lang, 
                             lang_urls=get_lang_urls())

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            
            if name and email and message:
                print(f"📧 Contact form: {name}, {email}, {message}")
                flash(trans['message_sent_successfully'], 'success')
            else:
                flash(trans['please_fill_all_fields'], 'error')
            return redirect(url_for('contact', lang=lang))
            
        return render_template('contact.html', 
                             trans=trans, 
                             lang=lang, 
                             lang_urls=get_lang_urls())

    # ------------------- Admin Dashboard -------------------
    @app.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()

        if request.method == 'POST':
            # --- Add Activity ---
            if 'add_activity' in request.form:
                try:
                    print("🎯 === محاولة إضافة نشاط جديد ===")
                    
                    # الحصول على البيانات
                    title_en = request.form.get('title_en', '').strip()
                    title_ar = request.form.get('title_ar', '').strip()
                    title_ku = request.form.get('title_ku', '').strip()
                    title_de = request.form.get('title_de', '').strip()
                    desc_en = request.form.get('description_en', '').strip()
                    desc_ar = request.form.get('description_ar', '').strip()
                    desc_ku = request.form.get('description_ku', '').strip()
                    desc_de = request.form.get('description_de', '').strip()
                    cat = request.form.get('category', '').strip()
                    
                    print(f"📝 Activity Data Received:")
                    print(f"   Title EN: {title_en}")
                    print(f"   Title AR: {title_ar}") 
                    print(f"   Category: {cat}")
                    print(f"   Desc EN: {desc_en[:50]}...")
                    print(f"   Desc AR: {desc_ar[:50]}...")
                    
                    # التحقق من الحقول المطلوبة
                    if not title_en or not title_ar or not desc_en or not desc_ar or not cat:
                        missing = []
                        if not title_en: missing.append('Title EN')
                        if not title_ar: missing.append('Title AR')
                        if not desc_en: missing.append('Description EN')
                        if not desc_ar: missing.append('Description AR')
                        if not cat: missing.append('Category')
                        print(f"❌ Missing fields: {missing}")
                        flash(trans['fill_required_fields'], 'error')
                        return redirect(url_for('dashboard', lang=lang))
                    
                    # معالجة الصور
                    filenames = []
                    files = request.files.getlist('images')
                    print(f"🖼️ Number of images: {len(files)}")
                    
                    for file in files:
                        if file and file.filename:
                            if not allowed_file(file.filename):
                                flash(trans['invalid_file_type'], 'warning')
                                continue
                                
                            filename = secure_filename(file.filename)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{timestamp}_{filename}"
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            
                            try:
                                file.save(file_path)
                                filenames.append(filename)
                                print(f"✅ Image saved: {filename}")
                            except Exception as e:
                                print(f"❌ Error saving image: {str(e)}")
                                flash(f'Error saving image: {str(e)}', 'error')
                                continue
                    
                    images_str = ','.join(filenames) if filenames else None
                    
                    # إنشاء النشاط الجديد
                    new_activity = Activity(
                        title_en=title_en,
                        title_ar=title_ar,
                        title_ku=title_ku if title_ku else None,
                        title_de=title_de if title_de else None,
                        description_en=desc_en,
                        description_ar=desc_ar,
                        description_ku=desc_ku if desc_ku else None,
                        description_de=desc_de if desc_de else None,
                        category=cat,
                        images=images_str
                    )
                    
                    print(f"✅ New activity object created: {new_activity}")
                    
                    # حفظ في قاعدة البيانات
                    db.session.add(new_activity)
                    db.session.commit()
                    
                    print("🎉 ✅ Activity saved to database successfully!")
                    print(f"📌 New activity ID: {new_activity.id}")
                    
                    # التحقق من الإضافة
                    activities_count = Activity.query.count()
                    print(f"📊 Total activities in database now: {activities_count}")
                    
                    flash(trans['activity_added_successfully'], 'success')
                    return redirect(url_for('dashboard', lang=lang))
                    
                except Exception as e:
                    db.session.rollback()
                    error_msg = f'Error adding activity: {str(e)}'
                    print(f"❌ {error_msg}")
                    import traceback
                    print(f"🔍 Stack trace: {traceback.format_exc()}")
                    flash(error_msg, 'error')
                    return redirect(url_for('dashboard', lang=lang))

            # --- Add Article ---
            elif 'add_article' in request.form:
                try:
                    print("📝 === محاولة إضافة مقال جديد ===")
                    
                    title_en = request.form.get('title_en', '').strip()
                    title_ar = request.form.get('title_ar', '').strip()
                    title_ku = request.form.get('title_ku', '').strip()
                    title_de = request.form.get('title_de', '').strip()
                    content_en = request.form.get('content_en', '').strip()
                    content_ar = request.form.get('content_ar', '').strip()
                    content_ku = request.form.get('content_ku', '').strip()
                    content_de = request.form.get('content_de', '').strip()
                    
                    if not title_en or not title_ar or not content_en or not content_ar:
                        flash('Please fill all required fields', 'error')
                        return redirect(url_for('dashboard', lang=lang))
                    
                    author_image = None
                    author_image_file = request.files.get('author_image')
                    if author_image_file and author_image_file.filename:
                        if allowed_file(author_image_file.filename):
                            filename = secure_filename(author_image_file.filename)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{timestamp}_{filename}"
                            author_image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            author_image = filename
                            print(f"✅ Author image saved: {author_image}")
                    
                    new_article = Article(
                        title_en=title_en,
                        title_ar=title_ar,
                        title_ku=title_ku if title_ku else None,
                        title_de=title_de if title_de else None,
                        content_en=content_en,
                        content_ar=content_ar,
                        content_ku=content_ku if content_ku else None,
                        content_de=content_de if content_de else None,
                        author_image=author_image
                    )
                    
                    db.session.add(new_article)
                    db.session.commit()
                    
                    print("✅ Article saved to database successfully")
                    flash(trans['article_added_successfully'], 'success')
                    return redirect(url_for('dashboard', lang=lang))
                    
                except Exception as e:
                    db.session.rollback()
                    error_msg = f'Error adding article: {str(e)}'
                    print(f"❌ {error_msg}")
                    flash(error_msg, 'error')
                    return redirect(url_for('dashboard', lang=lang))

            # --- Add Breaking News ---
            elif 'add_breaking_news' in request.form:
                try:
                    print("🚨 === محاولة إضافة خبر عاجل جديد ===")
                    
                    title_ar = request.form.get('breaking_title_ar', '').strip()
                    title_en = request.form.get('breaking_title_en', '').strip()
                    title_ku = request.form.get('breaking_title_ku', '').strip()
                    title_de = request.form.get('breaking_title_de', '').strip()
                    content_ar = request.form.get('breaking_content_ar', '').strip()
                    content_en = request.form.get('breaking_content_en', '').strip()
                    content_ku = request.form.get('breaking_content_ku', '').strip()
                    content_de = request.form.get('breaking_content_de', '').strip()
                    
                    if not title_ar or not title_en or not content_ar or not content_en:
                        flash('Please fill all required fields for breaking news.', 'error')
                        return redirect(url_for('dashboard', lang=lang))
                    
                    # Handle image upload
                    image = None
                    image_file = request.files.get('breaking_image')
                    if image_file and image_file.filename:
                        if allowed_file(image_file.filename):
                            filename = secure_filename(image_file.filename)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"breaking_{timestamp}_{filename}"
                            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            image = filename
                            print(f"✅ Breaking news image saved: {image}")
                    
                    breaking_news = BreakingNews(
                        title_ar=title_ar,
                        title_en=title_en,
                        title_ku=title_ku if title_ku else None,
                        title_de=title_de if title_de else None,
                        content_ar=content_ar,
                        content_en=content_en,
                        content_ku=content_ku if content_ku else None,
                        content_de=content_de if content_de else None,
                        image=image
                    )
                    
                    db.session.add(breaking_news)
                    db.session.commit()
                    
                    print("✅ Breaking news saved to database successfully")
                    flash('Breaking news added successfully!', 'success')
                    return redirect(url_for('dashboard', lang=lang))
                    
                except Exception as e:
                    db.session.rollback()
                    error_msg = f'Error adding breaking news: {str(e)}'
                    print(f"❌ {error_msg}")
                    flash(error_msg, 'error')
                    return redirect(url_for('dashboard', lang=lang))

        # Load data for display
        try:
            activities = Activity.query.order_by(Activity.date_posted.desc()).all()
            articles = Article.query.order_by(Article.date_posted.desc()).all()
            breaking_news = BreakingNews.query.order_by(BreakingNews.date_posted.desc()).all()
            print(f"📊 Dashboard: {len(activities)} activities, {len(articles)} articles, {len(breaking_news)} breaking news")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            activities = []
            articles = []
            breaking_news = []
        
        return render_template('dashboard.html', 
                             trans=trans, 
                             activities=activities,
                             articles=articles,
                             breaking_news=breaking_news,
                             lang=lang, 
                             lang_urls=get_lang_urls())

    # ------------------- Edit Routes -------------------
    @app.route('/edit_activity/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_activity(id):
        if not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('index'))
        
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        
        try:
            activity = Activity.query.get_or_404(id)
        except Exception as e:
            flash('Activity not found.', 'error')
            return redirect(url_for('dashboard', lang=lang))
        
        if request.method == 'POST':
            try:
                activity.title_en = request.form.get('title_en', activity.title_en)
                activity.title_ar = request.form.get('title_ar', activity.title_ar)
                activity.title_ku = request.form.get('title_ku', activity.title_ku)
                activity.title_de = request.form.get('title_de', activity.title_de)
                activity.description_en = request.form.get('description_en', activity.description_en)
                activity.description_ar = request.form.get('description_ar', activity.description_ar)
                activity.description_ku = request.form.get('description_ku', activity.description_ku)
                activity.description_de = request.form.get('description_de', activity.description_de)
                activity.category = request.form.get('category', activity.category)
                
                # Handle new images
                new_images = request.files.getlist('new_images')
                if new_images and any(img.filename for img in new_images):
                    filenames = []
                    for file in new_images:
                        if file and file.filename and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{timestamp}_{filename}"
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            filenames.append(filename)
                    
                    if filenames:
                        # Keep existing images and add new ones
                        existing_images = activity.images.split(',') if activity.images else []
                        all_images = existing_images + filenames
                        activity.images = ','.join(all_images)
                
                db.session.commit()
                flash('Activity updated successfully.', 'success')
                return redirect(url_for('dashboard', lang=lang))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating activity: {str(e)}', 'error')
        
        return render_template('edit_activity.html', trans=trans, activity=activity, lang=lang, lang_urls=get_lang_urls())

    @app.route('/edit_article/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_article(id):
        if not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('index'))
        
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        
        try:
            article = Article.query.get_or_404(id)
        except Exception as e:
            flash('Article not found.', 'error')
            return redirect(url_for('dashboard', lang=lang))
        
        if request.method == 'POST':
            try:
                article.title_en = request.form.get('title_en', article.title_en)
                article.title_ar = request.form.get('title_ar', article.title_ar)
                article.title_ku = request.form.get('title_ku', article.title_ku)
                article.title_de = request.form.get('title_de', article.title_de)
                article.content_en = request.form.get('content_en', article.content_en)
                article.content_ar = request.form.get('content_ar', article.content_ar)
                article.content_ku = request.form.get('content_ku', article.content_ku)
                article.content_de = request.form.get('content_de', article.content_de)
                
                # Handle new author image
                new_author_image = request.files.get('new_author_image')
                if new_author_image and new_author_image.filename and allowed_file(new_author_image.filename):
                    filename = secure_filename(new_author_image.filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}_{filename}"
                    new_author_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    article.author_image = filename
                
                db.session.commit()
                flash('Article updated successfully.', 'success')
                return redirect(url_for('dashboard', lang=lang))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating article: {str(e)}', 'error')
        
        return render_template('edit_article.html', trans=trans, article=article, lang=lang, lang_urls=get_lang_urls())

    @app.route('/edit_breaking_news/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_breaking_news(id):
        if not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('index'))
        
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        
        try:
            breaking_news = BreakingNews.query.get_or_404(id)
        except Exception as e:
            flash('Breaking news not found.', 'error')
            return redirect(url_for('dashboard', lang=lang))
        
        if request.method == 'POST':
            try:
                breaking_news.title_ar = request.form.get('title_ar', breaking_news.title_ar)
                breaking_news.title_en = request.form.get('title_en', breaking_news.title_en)
                breaking_news.title_ku = request.form.get('title_ku', breaking_news.title_ku)
                breaking_news.title_de = request.form.get('title_de', breaking_news.title_de)
                breaking_news.content_ar = request.form.get('content_ar', breaking_news.content_ar)
                breaking_news.content_en = request.form.get('content_en', breaking_news.content_en)
                breaking_news.content_ku = request.form.get('content_ku', breaking_news.content_ku)
                breaking_news.content_de = request.form.get('content_de', breaking_news.content_de)
                breaking_news.is_active = 'is_active' in request.form
                
                # Handle new image
                new_image = request.files.get('new_image')
                if new_image and new_image.filename and allowed_file(new_image.filename):
                    filename = secure_filename(new_image.filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"breaking_{timestamp}_{filename}"
                    new_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    breaking_news.image = filename
                
                db.session.commit()
                flash('Breaking news updated successfully.', 'success')
                return redirect(url_for('dashboard', lang=lang))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating breaking news: {str(e)}', 'error')
        
        return render_template('edit_breaking_news.html', trans=trans, breaking_news=breaking_news, lang=lang, lang_urls=get_lang_urls())

    # ------------------- Delete Routes -------------------
    @app.route('/delete_activity/<int:id>', methods=['POST'])
    @login_required
    def delete_activity(id):
        if not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('index'))
        
        lang = session.get('lang', 'en')
        
        try:
            activity = Activity.query.get_or_404(id)
            db.session.delete(activity)
            db.session.commit()
            flash('Activity deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting activity: {str(e)}', 'error')
            
        return redirect(url_for('dashboard', lang=lang))

    @app.route('/delete_article/<int:id>', methods=['POST'])
    @login_required
    def delete_article(id):
        if not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('index'))
        
        lang = session.get('lang', 'en')
        
        try:
            article = Article.query.get_or_404(id)
            db.session.delete(article)
            db.session.commit()
            flash('Article deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting article: {str(e)}', 'error')
            
        return redirect(url_for('dashboard', lang=lang))

    @app.route('/delete_breaking_news/<int:id>', methods=['POST'])
    @login_required
    def delete_breaking_news(id):
        if not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('index'))
        
        lang = session.get('lang', 'en')
        
        try:
            breaking_news = BreakingNews.query.get_or_404(id)
            db.session.delete(breaking_news)
            db.session.commit()
            flash('Breaking news deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting breaking news: {str(e)}', 'error')
            
        return redirect(url_for('dashboard', lang=lang))

    # ------------------- Auth Routes -------------------
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        
        if current_user.is_authenticated:
            return redirect(url_for('dashboard' if current_user.is_admin else 'index'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please enter both username and password.', 'error')
                return render_template('login.html', trans=trans, lang=lang, lang_urls=get_lang_urls())
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get('next')
                print(f"✅ User {username} logged in successfully")
                flash(f'Welcome back, {username}!', 'success')
                return redirect(next_page or ('dashboard' if user.is_admin else 'index'))
            else:
                print(f"❌ Login failed for user: {username}")
                flash('Invalid username or password.', 'error')
                
        return render_template('login.html', trans=trans, lang=lang, lang_urls=get_lang_urls())

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        trans = get_trans()
        
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not username or not email or not password:
                flash('Please fill all required fields.', 'error')
                return render_template('register.html', trans=trans, lang=lang, lang_urls=get_lang_urls())
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('register.html', trans=trans, lang=lang, lang_urls=get_lang_urls())
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists.', 'error')
                return render_template('register.html', trans=trans, lang=lang, lang_urls=get_lang_urls())
            
            if User.query.filter_by(email=email).first():
                flash('Email already exists.', 'error')
                return render_template('register.html', trans=trans, lang=lang, lang_urls=get_lang_urls())
            
            try:
                user = User(username=username, email=email)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                print(f"✅ New user registered: {username}")
                flash('Registered successfully. Please login.', 'success')
                return redirect(url_for('login', lang=lang))
            except Exception as e:
                db.session.rollback()
                flash(f'Error during registration: {str(e)}', 'error')
        
        return render_template('register.html', trans=trans, lang=lang, lang_urls=get_lang_urls())

    @app.route('/logout')
    @login_required
    def logout():
        lang = session.get('lang', 'en')
        logout_user()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('index', lang=lang))

    print("🎉 ✅ All routes initialized successfully!")