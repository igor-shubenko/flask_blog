from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FileField
from wtforms.validators import Length

class AdminLoginForm(FlaskForm):
    admin_name = StringField(label="Ім'я")
    password = PasswordField(label='Пароль')


class AddPostForm(FlaskForm):
    title = StringField(label="Заголовок", validators=[Length(min=3, max=200)])
    slug = StringField(label='Slug', validators=[Length(min=3, max=100)])
    text = TextAreaField(label='Текст статті', validators=[Length(min=10)])


class AddFileForm(FlaskForm):
    fileinput = FileField(label='Додати файл')