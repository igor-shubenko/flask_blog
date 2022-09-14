from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import Length

class CommentForm(FlaskForm):
    name = StringField('Имя', validators=[Length(min=1, max=40)])
    text = TextAreaField('Комент', validators=[Length(min=3, max=5000)])
