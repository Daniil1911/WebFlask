from flask import Flask, redirect, render_template, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField, FileField
from wtforms.validators import DataRequired, EqualTo

from flask import Flask
from config import Configuration
import sqlite3


from models import UserModel,PostModel

app = Flask(__name__)
app.config.from_object(Configuration)

#database

class DB:
    def __init__(self):
        conn = sqlite3.connect('123.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()

#models, app and db init

db = DB()
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
user_model = UserModel(db.get_connection())
post_model = PostModel(db.get_connection())
user_model.init_table() #таблицы нужно проиницилизировать, т.е. создать при необходимости
post_model.init_table()
user_status, user_id = False, False #проверка, что юзер залогинился, его ид


#forms

#форма входа
class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

#форма регистрации
class RegForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторить пароль', validators=[DataRequired()])
    fname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    submit = SubmitField('Войти')
#форма добавление сообщения
class AddPost(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField('Описание ', validators=[DataRequired()])
    image = FileField("Image")
    submit = SubmitField('Добавить')


#pages

#страница входа
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_id, user_status
    form = LoginForm()
    user_status, user_id = user_model.exists(form.login.data, form.password.data)
    if form.validate_on_submit() and user_status:
        session["username"] = form.login.data
        return redirect('/index')
    return render_template('login.html', title='Авторизация', form=form)

#страница выхода
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global user_status
    user_status = False
    return redirect('/index')


#страница регистрации
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    global user_id, user_status
    form = RegForm()
    login = form.login.data
    fname = form.fname.data
    name = form.name.data
    password_hash = form.password.data
    user_model.insert(login, password_hash, fname, name)
    if form.validate_on_submit():
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)

#страница главная
@app.route('/index')
@app.route('/news')
def news():
    if user_status:
        post_list = post_model.get_all()
        return render_template('index.html', posts=post_list)
    else:
        return redirect('/login')

#страница просмотра отдельной новости
@app.route('/post/<int:post_id>', methods=['GET'])
def view_post(post_id):
    if user_status:
        post= post_model.get(post_id)
        post_model.add_view(post_id)
        return render_template('post.html', post=post)
    else:
        return redirect('/login')

#страница добавления новости
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if not user_status:
        return redirect('/login')
    form = AddPost()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        image=  (form.image.data, form.image.data.read())
        views = 0
        post_model.insert(title, content, str(user_id),image, views)
        return redirect("/index")
    return render_template('add_post.html', title='Добавление новости', form=form, username=user_id)


#страница удаления новости
@app.route('/delete/<int:post_id>', methods=['GET'])
def delete_post(post_id):
    if not user_status:
        return redirect('/login')
    post_model.delete(post_id)
    return redirect("/index")


#запуск приложения
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)