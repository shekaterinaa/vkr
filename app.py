from db import db
from db.models import Users, Advertisements, Portfolio, AdPhoto, JournalApplication
from sqlalchemy import func
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from db.models import Img 
import re
from flask_cors import CORS
import base64


import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

app = Flask(__name__)
CORS(app)

# Получаем настройки из переменных окружения
app.secret_key = os.getenv('SECRET_KEY', '123')  # Значение по умолчанию '123'
user_db = os.getenv('DB_USER', 'katya')
host_ip = os.getenv('DB_HOST', '0.0.0.0')
host_port = os.getenv('DB_PORT', '10000')
database_name = os.getenv('DB_NAME', 'katya_rgz')
password = os.getenv('DB_PASSWORD', '123')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"  # Указываем, какой маршрут использовать для логина

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def home_redirect():
    return redirect(url_for('home_page'))

@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    # Пример статических данных
    desk = [
        {
            'subject': 'Объявление 1',
            'main_text': 'Описание объявления 1',
            'author_name': 'Автор 1',
            'email': 'author1@example.com'
        },
        {
            'subject': 'Объявление 2',
            'main_text': 'Описание объявления 2',
            'author_name': 'Автор 2',
            'email': 'author2@example.com'
        },
        {
            'subject': 'Объявление 3',
            'main_text': 'Описание объявления 3',
            'author_name': 'Автор 3',
            'email': 'author3@example.com'
        },
    ]

    if request.method == 'POST':
        # Получаем данные из формы
        data = request.get_json()
        team_details = data.get('team_details')
        cloud_link = data.get('cloud_link')
        social_link = data.get('social_link')

        # Здесь можно добавить логику для сохранения данных в базу данных
        # Например, создание нового объекта и добавление его в базу данных

        # Например, логируем полученные данные (замените это вашей логикой обработки)
        print(f"Received team details: {team_details}")
        print(f"Received cloud link: {cloud_link}")
        print(f"Received social link: {social_link}")

        # После обработки возвращаем ответ
        return jsonify(success=True), 201  # Возвращаем успешный статус

    # Если метод GET, продолжаем как и раньше
    total_page = len(desk)  # Общее количество объявлений
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Количество объявлений на странице
    offset = (page - 1) * per_page
    
    # Срез для получения нужной страницы
    desk = desk[offset:offset + per_page]

    # Получение аватара пользователя
    avatar = None
    if current_user.is_authenticated:
        user_avatar = Img.query.filter_by(user_id=current_user.id).first()
        if user_avatar:
            avatar = base64.b64encode(user_avatar.img).decode('utf-8')  # Кодируем в base64

    return render_template('index.html', desk=desk, total_page=total_page, page=page, per_page=per_page, avatar=avatar)


@app.route('/account', methods=['GET'])
@login_required
def account():
    name_user = current_user  # Используем current_user напрямую
    adv = Advertisements.query.filter_by(author_id=name_user.id).all()

    # Получение аватара пользователя из таблицы Img
    user_avatar = Img.query.filter_by(user_id=name_user.id).first()
    avatar = None
    if user_avatar:
        avatar = base64.b64encode(user_avatar.img).decode('utf-8')


    return render_template('account.html', name_user=name_user, adv=adv, avatar=avatar)

@app.route('/journal_applications', methods=['GET'])
@login_required
def journal_applications():
    # Получение всех заявок из журнала
    applications = JournalApplication.query.all()
    return render_template('journal_applications.html', applications=applications)


@app.route('/logout')
@login_required
def logout():
    logout_user()  # Выход из системы
    session.clear()  # Очистка сессии

    return redirect(url_for('home_page'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username_form = request.form.get("username")
    password_form = request.form.get("password")
    name_form = request.form.get("name")
    avatar_form = request.files.get("avatar")  # Получение файла
    contact_form = request.form.get("contact")
    about_form = request.form.get("about")
    specialization_form = request.form.get("specialization")
    social_form = request.form.get("social")  # Получение ссылки на соц.сети

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
    elif len(about_form) > 1800:
        errors.append("Описание должно содержать не более 1800 символов!")

    if errors:
        return render_template("register.html", errors=errors)

    hashedPswd = generate_password_hash(password_form)

    # Создаем нового пользователя
    newUser = Users(username=username_form, 
                    password=hashedPswd, 
                    name=name_form,
                    contact=contact_form, 
                    about=about_form,
                    social=social_form,  # Сохраняем ссылку на соц.сети
                    specialization=specialization_form if specialization_form != "не выбрано" else None)

    db.session.add(newUser)
    db.session.commit()  # Сначала сохраняем пользователя, присваиваем user_id

    # Сохраняем аватар, если он загружен
    if avatar_form:
        filename = secure_filename(avatar_form.filename)
        img_data = avatar_form.read()
        newAvatar = Img(img=img_data, name=filename, user_id=newUser.id)  # Получаем user_id для нового пользователя
        db.session.add(newAvatar)

    db.session.commit()  # Сохраняем аватар

    flash("Регистрация успешна!", "success")
    return redirect("/login")





@app.route('/api/users/<specialization>', methods=['GET'])
def get_users_by_specialization(specialization):
    # Предположим, что есть множество специализаций, получаем их
    specialization_exists = db.session.query(Users).filter_by(specialization=specialization).first() is not None

    # Проверяем существование специализации
    if not specialization_exists:
        return jsonify({"error": "Специализация не найдена."}), 404

    users = Users.query.filter_by(specialization=specialization).all()
    
    if not users:
        return jsonify({"message": "Нет пользователей в данной специализации."}), 404

    users_data = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'contact': user.contact,
            'about': user.about,
            'portfolio': []
        }

        # Получение аватара
        user_avatar = Img.query.filter_by(user_id=user.id).first()
        if user_avatar:
            user_data['avatar'] = base64.b64encode(user_avatar.img).decode('utf-8')

        # Получение портфолио
        portfolio_images = Portfolio.query.filter_by(user_id=user.id).limit(5).all()
        for img in portfolio_images:
            user_data['portfolio'].append({
                'image': base64.b64encode(img.img).decode('utf-8'),
                'name': img.name
            })

        users_data.append(user_data)

    return jsonify(users_data)



@app.route('/account/<int:user_id>', methods=['GET'])
def profile(user_id):
    specialist = Users.query.get_or_404(user_id)
    portfolio_images = Portfolio.query.filter_by(user_id=user_id).all()
    
    # Получаем аватар пользователя
    user_avatar = Img.query.filter_by(user_id=specialist.id).first()
    avatar = None
    if user_avatar:
        avatar = base64.b64encode(user_avatar.img).decode('utf-8')

    return render_template('profile.html', specialist=specialist, portfolio_images=portfolio_images, avatar=avatar)



# Страница авторизации
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        errors = []
        username_form = request.form.get("username")
        password_form = request.form.get("password")

        my_user = Users.query.filter_by(username=username_form).first()

        if my_user is not None and check_password_hash(my_user.password, password_form):
            print(f"User logged in: {my_user.username}")  # Для отладки
            login_user(my_user)  # Важно: добавьте здесь вызов login_user
            return redirect(url_for('index'))

        if not username_form or not password_form:
            errors.append("Введите имя пользователя и пароль!")
        else:
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
        link = request.form['link']
        cooperation_condition = request.form['cooperation_condition']
        price_form = request.form.get('price')

        author = Users.query.filter_by(username=current_user.username).first()

        # Сохраняем объявление
        new_adv = Advertisements(
            subject=subject_form,
            main_text=main_text_form,
            author_id=author.id,
            author_name=author.name,
            link=link,
            cooperation_condition=cooperation_condition,
            price=price_form
        )
        
        db.session.add(new_adv)
        db.session.commit()  # Сначала сохраняем само объявление, чтобы получить его ID

        # Обработка загружаемых фотографий
        photos = request.files.getlist('photo')  # Получаем список файлов
        for photo in photos:
            if photo:
                img_data = photo.read()
                new_photo = AdPhoto(img=img_data, ad_id=new_adv.id)  # Указываем ID нового объявления
                db.session.add(new_photo)  # Сохраняем каждую фотографию

        db.session.commit()  # Сохраняем все фотографии

        return redirect(url_for('account'))

    return render_template('create_adv.html', errors=errors)




@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    errors = []
    if request.method == 'POST':
        id_form = request.form.get('id')

        if not id_form:
            errors.append("Объявление не найдено!")
            return render_template("edit.html", errors=errors)

        edit_adv = Advertisements.query.get(id_form)

        if edit_adv is None or edit_adv.author_id != current_user.id:
            errors.append("У вас нет прав для редактирования данного объявления!")
            return render_template("edit.html", errors=errors)

        subject_form = request.form['subject']
        main_text_form = request.form['main_text']
        link_form = request.form['link']
        photo_form = request.files.get('photo')  # Получаем файл из формы

        # Валидация обязательных полей
        if not subject_form or not main_text_form or not link_form:
            errors.append("Заполните все обязательные поля!")
            return render_template("edit.html", errors=errors, desk=[edit_adv])

        # Обновление полей объявления
        edit_adv.subject = subject_form
        edit_adv.main_text = main_text_form
        edit_adv.link = link_form

        # Обработка изображения
        if photo_form:  # Проверка, загружено ли новое изображение
            img_data = photo_form.read()  # Чтение содержимого файла
            new_photo = AdPhoto(img=img_data, ad_id=edit_adv.id)  # Создание новой записи в таблице AdPhoto
            db.session.add(new_photo)  # Добавление фото в сессию базы данных

        db.session.commit()  # Сохраняем изменения в базе данных
        return redirect(url_for('account'))  # Перенаправление на страницу аккаунта

    # Подборка объявления по id и отображение формы редактирования
    edit_adv = Advertisements.query.filter_by(author_id=current_user.id).all()
    return render_template('edit.html', desk=edit_adv)



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
        link_form = request.form['link']
        photo_form = request.form['photo']

        if not subject_form or not main_text_form or not link_form or not photo_form:
            errors.append("Заполните все поля!")
            return render_template("edit.html", errors=errors, desk=desk, subject=subject_form,
                                   main_text=main_text_form, link=link_form, photo=photo_form)

        if len(photo_form) > 1000:
            errors.append("Максимальная длина поля 1000 символов!")
            return render_template("edit.html", errors=errors, desk=desk, subject=subject_form,
                                   main_text=main_text_form, link=link_form, photo=photo_form)

        edit_adv.subject = subject_form
        edit_adv.main_text = main_text_form
        edit_adv.link = link_form
        edit_adv.photo = photo_form
        db.session.commit()
        return redirect(url_for('account'))

    return render_template('edit.html', desk=desk)


@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    errors = []
    # Получаем все объявления текущего пользователя или все объявления для администратора
    if current_user.username == 'shekaterina':
        desk = Advertisements.query.all()  # Получаем все объявления для администратора
    else:
        desk = Advertisements.query.filter_by(author_id=current_user.id).all()  # Только свои объявления

    if request.method == 'POST':
        adv_id = request.form.get('id')

        if not adv_id:
            errors.append("Объявление не найдено!")
            return render_template("delete.html", errors=errors, desk=desk)

        adv_to_delete = Advertisements.query.get(adv_id)

        if not adv_to_delete:
            errors.append("Объявление не найдено!")
            return render_template("delete.html", errors=errors, desk=desk)

        # Проверяем, является ли пользователь владельцем объявления или администратором
        if adv_to_delete.author_id != current_user.id and current_user.username != 'shekaterina':
            errors.append("У вас нет прав для удаления данного объявления!")
            return render_template("delete.html", errors=errors, desk=desk)

        # Удаляем связанные фотографии, если такие есть
        AdPhoto.query.filter_by(ad_id=adv_to_delete.id).delete()
        
        db.session.delete(adv_to_delete)
        db.session.commit()

        # Перенаправляем на ту же страницу для обновления списка
        return redirect(url_for('delete'))

    return render_template("delete.html", errors=errors, desk=desk)




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


@app.route('/api/ads/<cooperation_condition>', methods=['GET'])
def get_ads_by_cooperation(cooperation_condition):
    # Получаем все объявления с выбранным условием сотрудничества
    ads = Advertisements.query.filter_by(cooperation_condition=cooperation_condition).all()
    
    ads_data = []
    for ad in ads:
        ad_data = {
            'id': ad.id,
            'subject': ad.subject,
            'main_text': ad.main_text,
            'author_name': ad.author_name,
            'link': ad.link,
            'photos': [],
            'price': ad.price  # Добавляем цену в данные объявления
        }

        # Получение всех фотографий для данного объявления
        photos = AdPhoto.query.filter_by(ad_id=ad.id).all()
        for photo in photos:
            ad_data['photos'].append(base64.b64encode(photo.img).decode('utf-8'))

        ads_data.append(ad_data)

    return jsonify(ads_data)



from flask import request, jsonify
@app.route('/submit_journal_application', methods=['POST'])
@login_required
def submit_journal_application():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Нет данных для обработки!"}), 400

    team_details = data.get('team_details')
    cloud_link = data.get('cloud_link')
    social_link = data.get('social_link')

    try:
        new_application = JournalApplication(
            user_id=current_user.id, 
            team_details=team_details,
            cloud_link=cloud_link,
            social_link=social_link
        )
        db.session.add(new_application)
        db.session.commit()
        return jsonify({"message": "Заявка отправлена!"}), 200
    except Exception as e:
        return jsonify({"message": "Ошибка сохранения заявки: " + str(e)}), 500



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

@app.route('/upload_portfolio', methods=['POST'])
def upload_portfolio():
    files = request.files.getlist('portfolio_images')
    user_id = current_user.id  # Получаем текущий ID пользователя

    for file in files:
        if file:
            img_data = file.read()  # Считываем данные изображения
            new_portfolio_image = Portfolio(img=img_data, name=file.filename, user_id=user_id)
            db.session.add(new_portfolio_image)  # Добавляем в сессию
    db.session.commit()  # Сохраняем изменения в базе данных

    return redirect(url_for('account'))  # Возвращаемся в личный кабинет

@app.template_filter('b64encode')
def b64encode_filter(data):
    """Кодирует бинарные данные в строку base64."""
    return base64.b64encode(data).decode('utf-8') if data else ''

@app.route('/delete_portfolio/<int:image_id>', methods=['POST'])
def delete_portfolio(image_id):
    user_id = current_user.id
    image_to_delete = Portfolio.query.get(image_id)

    print(f'Attempting to delete image with ID: {image_id} by user_id: {user_id}')  # Отладочное сообщение

    if image_to_delete and image_to_delete.user_id == user_id:
        try:
            db.session.delete(image_to_delete)
            db.session.commit()
            print('Image deleted successfully')  # Отладочное сообщение
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при удалении изображения: ' + str(e), 'error')
            print(f'Error occurred: {e}')  # Отладочное сообщение
    else:
        flash('Изображение не найдено или у вас нет прав для его удаления.', 'error')
        print('Image not found or no permission')  # Отладочное сообщение

    return redirect(url_for('account'))

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = Users.query.get(current_user.id)  # Получаем текущего пользователя
    errors = []  # Список ошибок

    if request.method == 'POST':
        # Обновляем остальные данные
        user.name = request.form['name']
        user.contact = request.form['contact']
        user.about = request.form['about']
        user.social = request.form['social']

        # Обработка аватара
        if 'avatar' in request.files and request.files['avatar']:
            avatar_file = request.files['avatar']
            if allowed_file(avatar_file.filename):  # Проверка формата файла
                filename = secure_filename(avatar_file.filename)
                img_data = avatar_file.read()

                # Сохраняем новый аватар (можно сохранить как BLOB или путь к файлу)
                user.avatar = img_data  # Если используете BLOB
                # Либо используйте:
                # avatar_path = f'static/avatars/{user.id}_{filename}'
                # avatar_file.save(avatar_path)
                # user.avatar = avatar_path  # Сохраняйте путь к файлу

        db.session.commit()  # Сохраняем изменения в базе данных
        
        flash('Профиль успешно обновлён!', 'success')  # Добавляем сообщение об успехе
        return redirect(url_for('account'))  # Перенаправляем обратно в аккаунт после сохранения

    return render_template('edit_profile.html', user=user, errors=errors)

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))










