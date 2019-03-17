from wtforms import Form, StringField, TextAreaField


class PostForm(Form):
    title = StringField('Title')
    content = TextAreaField('Content')