from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask_mail import Message
from models import db, User, Activity, Article, BreakingNews
from translations import translations

# ====================== Upload Config ======================
BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/images/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ====================== Secretariat Members ======================
SECRETARIAT_MEMBERS = [
    {"image": "member1.jpg", "name_en": "DILSHAD MELA HEMZA", "name_ar": "ديلشاد ميلا حمزة",
     "name_de": "DILSHAD MELA HEMZA", "name_ku": "DILSHAD MELA HEMZA",
     "role_en": "Member of the Secretariat Office<br>Responsible for the Media Department",
     "role_ar": "عضو مكتب السكرتارية<br>مسؤول قسم الإعلام",
     "role_de": "Mitglied des Sekretariats<br>Verantwortlich für die Medienabteilung",
     "role_ku": "Endamê Ofîsa Sekretarya<br>Berî vê Beşê Medya"},
    {"image": "member2.jpeg", "name_en": "Ciwan Ali", "name_ar": "جيوان علي",
     "name_de": "Ciwan Ali", "name_ku": "Ciwan Ali",
     "role_en": "Member of the Secretariat Office<br>Responsible for the Organization Department",
     "role_ar": "عضو مكتب السكرتارية<br>مسؤول قسم التنظيم",
     "role_de": "Mitglied des Sekretariats<br>Verantwortlich für die Organisationsabteilung",
     "role_ku": "Endamê Ofîsa Sekretarya<br>Berî vê Beşê Rêveberiyê"},
    {"image": "member3.jpeg", "name_en": "Bengin Teter", "name_ar": "بنجين تتر",
     "name_de": "Bengin Teter", "name_ku": "Bengin Teter",
     "role_en": "Member of the Secretariat Office<br>Responsible for Financial Department",
     "role_ar": "عضو مكتب السكرتارية<br>مسؤول قسم المالية",
     "role_de": "Mitglied des Sekretariats<br>Verantwortlich für die Finanzabteilung",
     "role_ku": "Endamê Ofîsa Sekretarya<br>Berî vê Beşê Aborî"},
    {"image": "member4.jpeg", "name_en": "Renas Abd Alrahman", "name_ar": "ريناس عبد الرحمن",
     "name_de": "Renas Abd Alrahman", "name_ku": "Renas Abd Alrahman",
     "role_en": "Member of the Secretariat Office",
     "role_ar": "عضو مكتب السكرتارية",
     "role_de": "Mitglied des Sekretariats",
     "role_ku": "Endamê Ofîsa Sekretarya"},
    {"image": "member5.jpeg", "name_en": "Mervan Badini", "name_ar": "ميرفان باديني",
     "name_de": "Mervan Badini", "name_ku": "Mervan Badini",
     "role_en": "Member of the Secretariat Office<br>Responsible for the Department of Statistics and Planning",
     "role_ar": "عضو مكتب السكرتارية<br>مسؤول قسم الإحصاء والتخطيط",
     "role_de": "Mitglied des Sekretariats<br>Verantwortlich für die Abteilung Statistik und Planung",
     "role_ku": "Endamê Ofîsa Sekretarya<br>Berî vê Beşê Statîstîk û Plan"},
    {"image": "member6.jpeg", "name_en": "Ehmed Haco", "name_ar": "أحمد حاجو",
     "name_de": "Ehmed Haco", "name_ku": "Ehmed Haco",
     "role_en": "Member of the Secretariat Office<br>Responsible for the Department of Student Affairs",
     "role_ar": "عضو مكتب السكرتارية<br>مسؤول قسم شؤون الطلاب",
     "role_de": "Mitglied des Sekretariats<br>Verantwortlich für die Abteilung Studentenangelegenheiten",
     "role_ku": "Endamê Ofîsa Sekretarya<br>Berî vê Beşê Perwerdeya Xwendekar"},
    {"image": "member7.jpeg", "name_en": "Shereen Abdo", "name_ar": "شيرين عبدو",
     "name_de": "Shereen Abdo", "name_ku": "Shereen Abdo",
     "role_en": "Member of the Secretariat Office<br>Responsible for the Department of Artistic Activities",
     "role_ar": "عضو مكتب السكرتارية<br>مسؤول قسم الأنشطة الفنية",
     "role_de": "Mitglied des Sekretariats<br>Verantwortlich für die Abteilung Künstlerische Aktivitäten",
     "role_ku": "Endamê Ofîsa Sekretarya<br>Berî vê Beşê Çalakiyên Hunerî"},
    {"image": "member8.jpeg", "name_en": "Shivan Ibrahim", "name_ar": "شيفان إبراهيم",
     "name_de": "Shivan Ibrahim", "name_ku": "Shivan Ibrahim",
     "role_en": "Member of the Secretariat Office<br>Responsible for the Relations Department",
     "role_ar": "عضو مكتب السكرتارية<br>مسؤول قسم العلاقات",
     "role_de": "Mitglied des Sekretariats<br>Verantwortlich für die Abteilung Beziehungen",
     "role_ku": "Endamê Ofîsa Sekretarya<br>Berî vê Beşê Têkiliyên"},
    {"image": "number9.jpeg", "name_en": "Mohammad Ismat", "name_ar": "محمد عصمت",
     "name_de": "Mohammad Ismat", "name_ku": "Mohammad Ismat",
     "role_en": "Member of the Secretariat Office<br>Responsible for the Department of Culture and Training",
     "role_ar": "عضو مكتب السكرتارية<br>مسؤول قسم الثقافة والتدريب",
     "role_de": "Mitglied des Sekretariats<br>Verantwortlich für die Abteilung Kultur und Ausbildung",
     "role_ku": "Endamê Ofîsa Sekretarya<br>Berî vê Beşê Çand û Fêrkirinê"},
    {"image": "number9.jpeg", "name_en": "Deham Osman", "name_ar": "دهام عثمان",
     "name_de": "Deham Osman", "name_ku": "Deham Osman",
     "role_en": "Member of the Secretariat Office",
     "role_ar": "عضو مكتب السكرتارية",
     "role_de": "Mitglied des Sekretariats",
     "role_ku": "Endamê Ofîsa Sekretarya"}
]

# ====================== Init Routes ======================
def init_routes(app, mail):
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # ====================== Helpers ======================
    def get_trans():
        lang = session.get('lang', 'en')
        base = translations.get(lang, translations['en'])
        class T(dict):
            def __getitem__(self, key):
                return base.get(key, translations['en'].get(key, key))
        return T()

    def get_lang_urls():
        lang_urls = {}
        endpoint = request.endpoint or 'index'
        args = dict(request.view_args or {})
        query = dict(request.args)
        for lang in translations.keys():
            try:
                args['lang'] = lang
                lang_urls[lang] = url_for(endpoint, **args, **query)
            except Exception:
                lang_urls[lang] = url_for('index', lang=lang)
        return lang_urls

    def get_by_lang(obj, field):
        lang = session.get('lang', 'en')
        value = getattr(obj, f"{field}_{lang}", None)
        return value if value else getattr(obj, f"{field}_en", "")

    # ====================== Frontend Pages ======================
    @app.route('/')
    def index():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        return render_template(
            'index.html',
            trans=get_trans(),
            activities=Activity.query.order_by(Activity.date_posted.desc()).limit(5).all(),
            breaking_news=BreakingNews.query.filter_by(is_active=True).order_by(BreakingNews.date_posted.desc()).limit(5).all(),
            latest_articles=Article.query.order_by(Article.date_posted.desc()).limit(3).all(),
            get_by_lang=get_by_lang,
            lang=lang,
            lang_urls=get_lang_urls()
        )

    @app.route('/activities')
    def activities():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        category = request.args.get('category')
        query = Activity.query
        if category:
            query = query.filter_by(category=category)
        return render_template(
            'activities.html',
            trans=get_trans(),
            activities=query.order_by(Activity.date_posted.desc()).all(),
            get_by_lang=get_by_lang,
            category=category,
            lang=lang,
            lang_urls=get_lang_urls()
        )

    @app.route('/activity/<int:id>')
    def activity_detail(id):
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        return render_template(
            'activity_detail.html',
            activity=Activity.query.get_or_404(id),
            trans=get_trans(),
            get_by_lang=get_by_lang,
            lang=lang,
            lang_urls=get_lang_urls()
        )

    @app.route('/articles')
    def articles():
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        return render_template(
            'articles.html',
            trans=get_trans(),
            articles=Article.query.order_by(Article.date_posted.desc()).all(),
            get_by_lang=get_by_lang,
            lang=lang,
            lang_urls=get_lang_urls()
        )

    @app.route('/article/<int:id>')
    def article_detail(id):
        lang = request.args.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        return render_template(
            'article.html',
            trans=get_trans(),
            article=Article.query.get_or_404(id),
            get_by_lang=get_by_lang,
            lang=lang,
            lang_urls=get_lang_urls()
        )

    # ====================== Static Pages ======================
    @app.route('/about')
    def about():
        return render_template(
            'about.html',
            trans=get_trans(),
            lang=session.get('lang', 'en'),
            lang_urls=get_lang_urls()
        )
    @app.route('/secretariat')
    def secretariat():
      return render_template(
        'secretariat.html',
        trans=get_trans(),
        secretariat_members=SECRETARIAT_MEMBERS,  # تأكد من نفس الاسم هنا
        get_by_lang=get_by_lang,
        lang=session.get('lang', 'en'),
        lang_urls=get_lang_urls()
    )


    @app.route('/bylaws')
    def bylaws():
        return render_template(
            'bylaws.html',
            trans=get_trans(),
            lang=session.get('lang', 'en'),
            lang_urls=get_lang_urls()
        )

    @app.route('/contact', methods=['GET','POST'])
    def contact():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            try:
                msg = Message(
                    subject=f"New Contact Message from {name}",
                    sender=email,
                    recipients=["your_email@gmail.com"],
                    body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
                )
                mail.send(msg)
                flash("✅ Message sent successfully!", "success")
                return redirect(url_for('contact'))
            except Exception as e:
                print(e)
                flash("❌ Failed to send message. Please try again.", "danger")
        return render_template(
            'contact.html',
            trans=get_trans(),
            lang=session.get('lang','en'),
            lang_urls=get_lang_urls()
        )

    # ====================== Auth ======================
    @app.route('/login', methods=['GET','POST'])
    def login():
        lang = request.args.get('lang', session.get('lang','en'))
        session['lang'] = lang
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            user = User.query.filter_by(username=request.form['username']).first()
            if user and user.check_password(request.form['password']):
                login_user(user)
                return redirect(url_for('dashboard'))
            flash(get_trans()['invalid_credentials'], 'danger')
        return render_template('login.html', trans=get_trans(), lang=lang, lang_urls=get_lang_urls())

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))
    @app.route('/register', methods=['GET', 'POST'])
    def register():
     return render_template(
        'register.html',
        trans=get_trans(),
        lang=session.get('lang', 'en'),
        lang_urls=get_lang_urls()
    )

    # ====================== Dashboard & CRUD ======================
    @app.route('/dashboard', methods=['GET','POST'])
    @login_required
    def dashboard():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        # ➤ Add Activity
        if request.method=='POST' and 'add_activity' in request.form:
            filenames=[]
            for f in request.files.getlist('images'):
                if f and allowed_file(f.filename):
                    name=secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'],name))
                    filenames.append(name)
            db.session.add(Activity(
                title_en=request.form['title_en'],
                title_ar=request.form['title_ar'],
                title_ku=request.form.get('title_ku'),
                title_de=request.form.get('title_de'),
                description_en=request.form['description_en'],
                description_ar=request.form['description_ar'],
                description_ku=request.form.get('description_ku'),
                description_de=request.form.get('description_de'),
                category=request.form['category'],
                images=",".join(filenames),
                date_posted=datetime.utcnow()
            ))
            db.session.commit()
            flash("Activity added successfully!", "success")
            return redirect(url_for('dashboard'))

        # ➤ Add Article
        if request.method=='POST' and 'add_article' in request.form:
            author_image=""
            f=request.files.get('author_image')
            if f and allowed_file(f.filename):
                name=secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],name))
                author_image=name
            db.session.add(Article(
                title_en=request.form['title_en'],
                title_ar=request.form['title_ar'],
                title_ku=request.form.get('title_ku'),
                title_de=request.form.get('title_de'),
                content_en=request.form['content_en'],
                content_ar=request.form['content_ar'],
                content_ku=request.form.get('content_ku'),
                content_de=request.form.get('content_de'),
                author_image=author_image,
                date_posted=datetime.utcnow()
            ))
            db.session.commit()
            flash("Article added successfully!", "success")
            return redirect(url_for('dashboard'))

        return render_template(
            'dashboard.html',
            trans=get_trans(),
            activities=Activity.query.all(),
            articles=Article.query.all(),
            get_by_lang=get_by_lang,
            lang=session.get('lang','en'),
            lang_urls=get_lang_urls()
        )

    # ====================== Edit/Delete Activity & Article ======================
    @app.route('/edit-activity/<int:id>', methods=['GET','POST'])
    @login_required
    def edit_activity(id):
        if not current_user.is_admin:
            return redirect(url_for('index'))
        activity=Activity.query.get_or_404(id)
        if request.method=='POST':
            activity.title_en=request.form['title_en']
            activity.title_ar=request.form['title_ar']
            activity.title_ku=request.form.get('title_ku')
            activity.title_de=request.form.get('title_de')
            activity.description_en=request.form['description_en']
            activity.description_ar=request.form['description_ar']
            activity.description_ku=request.form.get('description_ku')
            activity.description_de=request.form.get('description_de')
            activity.category=request.form['category']
            files=request.files.getlist('images')
            if files:
                filenames=[]
                for f in files:
                    if f and allowed_file(f.filename):
                        name=secure_filename(f.filename)
                        f.save(os.path.join(app.config['UPLOAD_FOLDER'],name))
                        filenames.append(name)
                if filenames:
                    activity.images=",".join(filenames)
            db.session.commit()
            flash("Activity updated successfully!", "success")
            return redirect(url_for('dashboard'))
        return render_template('edit_activity.html', activity=activity)

    @app.route('/delete-activity/<int:id>', methods=['POST'])
    @login_required
    def delete_activity(id):
        if not current_user.is_admin:
            return redirect(url_for('dashboard'))
        activity=Activity.query.get_or_404(id)
        db.session.delete(activity)
        db.session.commit()
        flash("Activity deleted!", "warning")
        return redirect(url_for('dashboard'))

    @app.route('/edit-article/<int:id>', methods=['GET','POST'])
    @login_required
    def edit_article(id):
        if not current_user.is_admin:
            return redirect(url_for('index'))
        article=Article.query.get_or_404(id)
        if request.method=='POST':
            article.title_en=request.form['title_en']
            article.title_ar=request.form['title_ar']
            article.title_ku=request.form.get('title_ku')
            article.title_de=request.form.get('title_de')
            article.content_en=request.form['content_en']
            article.content_ar=request.form['content_ar']
            article.content_ku=request.form.get('content_ku')
            article.content_de=request.form.get('content_de')
            f=request.files.get('author_image')
            if f and allowed_file(f.filename):
                name=secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],name))
                article.author_image=name
            db.session.commit()
            flash("Article updated successfully!", "success")
            return redirect(url_for('dashboard'))
        return render_template('edit_article.html', article=article)

    @app.route('/delete-article/<int:id>', methods=['POST'])
    @login_required
    def delete_article(id):
        if not current_user.is_admin:
            return redirect(url_for('dashboard'))
        article=Article.query.get_or_404(id)
        db.session.delete(article)
        db.session.commit()
        flash("Article deleted!", "warning")
        return redirect(url_for('dashboard'))

    print("✅ routes.py loaded successfully")
