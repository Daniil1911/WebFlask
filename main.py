from flask import Flask, redirect, render_template, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField, FileField
from wtforms.validators import DataRequired, EqualTo

from flask import Flask
from config import Configuration
import sqlite3


from models import UserModel,PostModel,Feed, UserImage

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
user_image = UserImage(db.get_connection())
post_model = PostModel(db.get_connection())
feed = Feed(db.get_connection())
user_model.init_table() #таблицы нужно проиницилизировать, т.е. создать при необходимости
post_model.init_table()
user_image.init_table()
feed.init_table()
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
    information = StringField('information', validators=[DataRequired()])
    submit = SubmitField('Войти')

class EditProfileForm(FlaskForm):
    fname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    image = FileField("Image")
    information = StringField('Information')
    submit = SubmitField('Update')
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
    information = form.information.data
    password_hash = form.password.data
    user_model.insert(login, password_hash, fname, name, information)
    if form.validate_on_submit():
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)

#страница главная
@app.route('/index')
def news():
    if user_status:
        post_list = post_model.get_all()
        user_list = [i[3] for i in post_list]
        name_list = [user_model.get_info(i)[:2] for i in user_list]
        image_list = [user_image.get(i) for i in user_list]
        data = [[post_list[i],name_list[i][0]+" "+ name_list[i][1], user_list[i], image_list[i]] for i in range(len(post_list))]
        print(list(data))
        return render_template('index.html', posts=data)
    else:
        return redirect('/login')

@app.route('/feed')
def feed_page():
    if user_status:
        post_list = feed.get_all(user_id)
        user_list = [i[3] for i in post_list]
        name_list = [user_model.get_info(i)[:2] for i in user_list]
        image_list = [user_image.get(i) for i in user_list]
        data = [[post_list[i], name_list[i][0] + " " + name_list[i][1], user_list[i], image_list[i]] for i in
                range(len(post_list))]
        print(list(data))
        return render_template('index.html', posts=data)
    else:
        return redirect('/login')

@app.route('/feeds')
def feeds_page():
    if user_status:
        users= feed.get_users(user_id)
        image_list = [user_image.get(i[0]) for i in users]
        print(list(zip(users,image_list)))
        data = [[users[i], image_list[i]] for i in   range(len(users))]
        return render_template('users.html', users=data)
    else:
        return redirect('/login')

@app.route('/profile')
def profile():
    if user_status:
        name,fname,information = user_model.get_info(user_id)
        image = user_image.get(user_id)
        user = user_image.get(user_id)
        return render_template('profile.html', user= user, name=name,fname=fname,information=information, image=image)
    else:
        return redirect('/login')
@app.route('/rd_profile', methods=['GET', 'POST'])
def edit_profile():
    if user_status:
        form = EditProfileForm()
        if form.validate_on_submit():
            name = form.name.data
            fname = form.fname.data
            information = form.information.data
            image = (form.image.data, form.image.data.read())
            user_image.insert(user_id,image)
            user_model.update(user_id, name,fname, information)
            return redirect("/profile")
        return render_template('add_profile.html', form=form)

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
        image=(form.image.data, form.image.data.read())
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


#follow
@app.route('/follow/<int:follow_id>', methods=['GET'])
def follow(follow_id):
    if not user_status:
        return redirect('/login')
    feed.insert(user_id,follow_id)
    return redirect("/index")
#unfollow
@app.route('/unfollow/<int:follow_id>', methods=['GET'])
def unfollow(follow_id):
    if not user_status:
        return redirect('/login')
    feed.delete(user_id,follow_id)
    return redirect("/index")


#запуск приложения
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)