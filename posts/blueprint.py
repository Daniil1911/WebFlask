from flask import Blueprint
from app import db
from flask import render_template
from models import Post
from .forms import PostForm
from flask import request
from flask import redirect
from flask import url_for

posts = Blueprint('posts', __name__, template_folder='templates')

@posts.route('/create', methods=['POST',  'GET'])
def create_post():

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        try:
            post = Post(title=title, content=content)
            db.session.add(post)
            db.session.commit()
        except:
            print('Ошибка')

        return redirect( url_for('posts.index'))
    form = PostForm()
    return render_template('posts/create_post.html', form=form)

@posts.route('/')
def index():
    post_model = Post(db.get_connection())
    return render_template('posts/index.html', posts=post_model)
