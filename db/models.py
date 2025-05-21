from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model):
    __tablename__ = 'users'  # Укажите явное имя таблицы

    id = db.Column(db.Integer, primary_key=True)  # Основной ключ
    username = db.Column(db.String(50), unique=True, nullable=False)  # Поле username (уникальное)
    password = db.Column(db.String(256), nullable=False)  # Поле password (обязательно)
    name = db.Column(db.String(50))  # Поле name
    contact = db.Column(db.String(256))  # Поле contact
    about = db.Column(db.String(1800))  # Поле about увеличено до 1800 символов
    specialization = db.Column(db.String(50))  # Поле specialization
    social = db.Column(db.String(256))  # Поле для ссылки на соц.сети

    def __repr__(self):
        return f'<User id: {self.id}, username: {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)  # Хэширование пароля при установке

    def check_password(self, password):
        return check_password_hash(self.password, password)  # Проверка пароля

    def is_active(self):
        return True  # В этом случае пользователь всегда активен

    def get_id(self):
        return str(self.id)  # Возвращает строковое представление ID пользователя

    def is_authenticated(self):
        return True  # Пользователь всегда аутентифицирован


    def __repr__(self):
        return f'<User id: {self.id}, username: {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)  # Хэширование пароля при установке

    def check_password(self, password):
        return check_password_hash(self.password, password)  # Проверка пароля

    def is_active(self):
        return True  # В этом случае пользователь всегда активен

    def get_id(self):
        return str(self.id)  # Возвращает строковое представление ID пользователя

    def is_authenticated(self):
        return True  # Пользователь всегда аутентифицирован



from db import db

class Advertisements(db.Model):
    __tablename__ = 'advertisements'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(400), nullable=False)
    main_text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(255), nullable=False)  # Изменили email на social_link
    photo = db.Column(db.String(255), nullable=False)
    cooperation_condition = db.Column(db.String(50), nullable=False)  # Новое поле для условий сотрудничества
    price = db.Column(db.String(100), nullable=True)  # Поле для стоимости в час или предложения по бартеру

    def __repr__(self):
        return f'id:{self.id}, subject:{self.subject}, cooperation_condition:{self.cooperation_condition}, price:{self.price}, social_link:{self.social_link}'

    
class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.LargeBinary, nullable=False)  # Храним изображение в формате BLOB
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Привязываем к пользователю

    def __repr__(self):
        return f'<Img id: {self.id}, name: {self.name}>'
    
class Portfolio(db.Model):
    __tablename__ = 'portfolio'  # Имя таблицы

    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.LargeBinary, nullable=False)  # Храним изображение в формате BLOB
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Привязываем к пользователю

    user = db.relationship('Users', backref='portfolios')  # Связь с пользователем

    def __repr__(self):
        return f'<Portfolio id: {self.id}, name: {self.name}>'

class AdPhoto(db.Model):
    __tablename__ = 'ad_photos'

    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.LargeBinary, nullable=False)
    ad_id = db.Column(db.Integer, db.ForeignKey('advertisements.id'), nullable=False)

    ad = db.relationship('Advertisements', backref='photos')  # Связь с объявлениями

    def __repr__(self):
        return f'<AdPhoto id: {self.id}, ad_id: {self.ad_id}>'
    
from db import db

class JournalApplication(db.Model):
    __tablename__ = 'journal_applications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    team_details = db.Column(db.String(1800), nullable=False)  # Изменено на 1800 символов
    cloud_link = db.Column(db.String(255), nullable=False)
    social_link = db.Column(db.String(255), nullable=True)  # Новая колонка для ссылки на соц-сеть
    
    user = db.relationship('Users', backref='journal_applications')



