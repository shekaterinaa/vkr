from db import db
from db.models import Users, Advertisements
from sqlalchemy import func
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session
import re

app = Flask(__name__)

app.secret_key = "123"
user_db = "katya"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "katya_rgz"
password="123"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager(app)

login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Главная страница
@app.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        prof = Users.query.filter_by(username = current_user.username).first()
        page = request.args.get('page', 1, type=int)
        per_page = 3
        offset = (page - 1) * per_page
    
        total_page = Advertisements.query.count()
        desk = Advertisements.query.order_by(Advertisements.id.desc()).offset(offset).limit(per_page).all()
        return render_template('index.html', desk=desk, total_page=total_page, page=page, per_page=per_page, prof=prof)
    
    page = request.args.get('page', 1, type=int)
    per_page = 3
    offset = (page - 1) * per_page
    
    total_page = Advertisements.query.count()
    desk = Advertisements.query.order_by(Advertisements.id.desc()).offset(offset).limit(per_page).all()
    return render_template('index.html', desk=desk, total_page=total_page, page=page, per_page=per_page)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    name_user = Users.query.filter_by(username=current_user.username).first()
    adv = Advertisements.query.filter_by(author_id=name_user.id).all()
    return render_template('account.html', name_user=name_user, adv=adv)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username_form = request.form.get("username")
    password_form = request.form.get("password")
    name_form = request.form.get("text_name")
    avatar_form = request.form.get("avatar")
    contact_form = request.form.get("contact")
    about_form = request.form.get("about")

    isUserExist = Users.query.filter_by(username=username_form).first()

    errors = []

    if isUserExist:
        errors.append("Такой пользователь уже существует!")
    elif not username_form:
        errors.append("Введите имя пользователя!")
    elif not password_form:
        errors.append("Введите пароль!")
    elif not re.match("^[a-zA-Z0-9]+$", password_form):
        errors.append("Пароль должен содержать только буквы и цифры!")
    elif re.search("[а-яА-Я]", password_form):
        errors.append("Пароль не должен содержать русские буквы!")
    elif len(password_form) < 5:
        errors.append("Пароль должен содержать не менее 5 символов!")
    elif len(about_form) > 120:
        errors.append("Описание должно содержать не более 120 символов!")

    if errors:
        return render_template("register.html", errors=errors)

    hashedPswd = generate_password_hash(password_form, method="pbkdf2")
    max_id = db.session.query(func.max(Users.id)).scalar()
    if max_id is not None:
        id_adv = int(max_id) + 1
    else:
        id_adv = 1

    newUser = Users(id=id_adv, username=username_form, password=hashedPswd, name=name_form, avatar=avatar_form, contact=contact_form, about=about_form)


    db.session.add(newUser)
    db.session.commit()

    return redirect("/login")


# Страница авторизации
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if current_user.is_authenticated:  # Если пользователь уже авторизован, перенаправляем его на другую страницу
        return redirect(url_for('index'))

    if request.method == "POST":
        errors = []
        username_form = request.form.get("username")
        password_form = request.form.get("password")

        my_user = Users.query.filter_by(username=username_form).first()

        if my_user is not None:
            if check_password_hash(my_user.password, password_form):
                login_user(my_user, remember=False)
                return redirect(url_for('index'))

        if not (username_form or password_form):
            errors.append("Введите имя пользователя и пароль!")
        elif my_user is None or not check_password_hash(my_user.password, password_form):
            errors.append("Неверное имя пользователя или пароль!")

        return render_template("login.html", errors=errors)

    return render_template("login.html")


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    errors = []
    if request.method == 'POST':
        subject_form = request.form['subject']
        main_text_form = request.form['main_text']
        author = Users.query.filter_by(username=current_user.username).first()
        email_form = request.form['email']
        photo_form = request.form['photo']
        max_id = db.session.query(func.max(Advertisements.id)).scalar()

        if not subject_form or not main_text_form or not email_form or not photo_form:
            errors.append("Заполните все поля!")
            return render_template("create_adv.html", errors=errors, subject_form=subject_form, 
                                   main_text_form=main_text_form, email_form=email_form, photo_form=photo_form)
        
        if len(photo_form) > 1000:
            errors.append("Максимальная длина поля 1000 символов!")
            return render_template("create_adv.html", errors=errors, subject_form=subject_form, 
                                   main_text_form=main_text_form, email_form=email_form, photo_form=photo_form)
        

        if max_id is not None:
            id_adv = int(max_id) + 1
        else:
            id_adv = 1
            
        new_adv = Advertisements(id=id_adv, subject=subject_form, main_text=main_text_form, author_id=author.id, 
                                 author_name=author.name, email=email_form, photo=photo_form)
        db.session.add(new_adv)
        db.session.commit()

        return redirect(url_for('account'))

    return render_template('create_adv.html')


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    errors = []
    desk = Advertisements.query.filter_by(author_id=current_user.id).all()
    if request.method == 'POST':
        id_form = request.form['id']
        if not id_form:
            errors.append("Объявление не найдено!")
            return render_template("edit.html", errors=errors, desk=desk)
        
        edit_adv = Advertisements.query.get(id_form)

        if edit_adv.author_id != current_user.id:
            errors.append("У вас нет прав для редактирования данного объявления!")
            return render_template("edit.html", errors=errors, desk=desk)

        subject_form = request.form['subject']
        main_text_form = request.form['main_text']
        email_form = request.form['email']
        photo_form = request.form['photo']

        if not subject_form or not main_text_form or not email_form or not photo_form:
            errors.append("Заполните все поля!")
            return render_template("edit.html", errors=errors, desk=desk, subject=subject_form,
                                   main_text=main_text_form, email=email_form, photo=photo_form)

        if len(photo_form) > 1000:
            errors.append("Максимальная длина поля 1000 символов!")
            return render_template("edit.html", errors=errors, desk=desk, subject=subject_form,
                                   main_text=main_text_form, email=email_form, photo=photo_form)
        
        edit_adv.subject = subject_form
        edit_adv.main_text = main_text_form
        edit_adv.email = email_form
        edit_adv.photo = photo_form
        db.session.commit()
        return redirect(url_for('account'))

    return render_template('edit.html', desk=desk)


@app.route('/edit_adm', methods=['GET', 'POST'])
@login_required
def edit_adm():
    errors = []
    desk = Advertisements.query.all()
    if request.method == 'POST':
        id_form = request.form['id']

        if not id_form:
            errors.append("Объявление не найдено!")
            return render_template("edit.html", errors=errors, desk=desk)

        edit_adv = Advertisements.query.get(id_form)

        subject_form = request.form['subject']
        main_text_form = request.form['main_text']
        email_form = request.form['email']
        photo_form = request.form['photo']

        if not subject_form or not main_text_form or not email_form or not photo_form:
            errors.append("Заполните все поля!")
            return render_template("edit.html", errors=errors, desk=desk, subject=subject_form,
                                   main_text=main_text_form, email=email_form, photo=photo_form)

        if len(photo_form) > 1000:
            errors.append("Максимальная длина поля 1000 символов!")
            return render_template("edit.html", errors=errors, desk=desk, subject=subject_form,
                                   main_text=main_text_form, email=email_form, photo=photo_form)

        edit_adv.subject = subject_form
        edit_adv.main_text = main_text_form
        edit_adv.email = email_form
        edit_adv.photo = photo_form
        db.session.commit()
        return redirect(url_for('account'))

    return render_template('edit.html', desk=desk)


@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    errors = []
    desk = Advertisements.query.filter_by(author_id=current_user.id).all()
    if request.method == 'POST':
        adv_id = request.form['id']

        if not adv_id:
            errors.append("Объявление не найдено!")
            return render_template("delete.html", errors=errors, desk=desk)

        adv_to_delete = Advertisements.query.get(adv_id)

        if adv_to_delete.author_id != current_user.id:
            errors.append("У вас нет прав для удаления данного объявления!")
            return render_template("delete.html", errors=errors, desk=desk)

        db.session.delete(adv_to_delete)
        db.session.commit()
        return redirect(url_for('account'))

    return render_template('delete.html', desk=desk, errors=errors)


@app.route('/delete_adv', methods=['GET', 'POST'])
@login_required
def delete_adv():
    errors = []
    desk = Advertisements.query.all()
    if request.method == 'POST':
        id_adv = request.form['id']

        if not id_adv:
            errors.append("Объявление не найдено!")
            return render_template("delete.html", errors=errors, desk=desk)

        delete = Advertisements.query.get(id_adv)

        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for('account'))

    return render_template('delete.html', desk=desk, errors=errors)


@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    errors = []
    user_v = Users.query.order_by(Users.id).all()
    if request.method == 'POST':
        id_user = request.form['id']

        if not id_user:
            errors.append("Пользователь не найден!")
            return render_template("edit_users.html", errors=errors, user_v=user_v)

        edit_user = Users.query.get(id_user)

        username_form = request.form['username']
        name_form = request.form['name']
        avatar_form = request.form['avatar']
        contact_form = request.form['contact']
        about_form = request.form['about']

        if not username_form or not name_form or not avatar_form or not contact_form or not about_form:
            errors.append("Заполните все поля!")
            return render_template("edit_users.html", errors=errors, user_v=user_v,
                                   username=username_form, name=name_form, avatar=avatar_form,
                                   contact=contact_form, about=about_form)

        if len(username_form) > 50 or len(name_form) > 100 or len(avatar_form) > 1000 or len(contact_form) > 1000 or len(about_form) > 1000:
            errors.append("Превышена максимальная длина одного или нескольких полей!")
            return render_template("edit_users.html", errors=errors, user_v=user_v,
                                   username=username_form, name=name_form, avatar=avatar_form,
                                   contact=contact_form, about=about_form)

        edit_user.username = username_form
        edit_user.name = name_form
        edit_user.avatar = avatar_form
        edit_user.contact = contact_form
        edit_user.about = about_form
        db.session.commit()
        return redirect(url_for('account'))

    return render_template('edit_users.html', user_v=user_v)


@app.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    errors = []
    user_v = Users.query.order_by(Users.id).all()
    if request.method == 'POST':
        id_user = request.form['id']
        
        if not id_user:
            errors.append("Пользователь не найден!")
            return render_template("delete_users.html", errors=errors, user_v=user_v)

        delete_user = Users.query.get(id_user)

        db.session.delete(delete_user)
        db.session.commit()
        return redirect(url_for('account'))

    return render_template('delete_users.html', user_v=user_v, errors=errors)


# Страница выхода из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
