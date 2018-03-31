from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class InputForm(FlaskForm):
    inputText = StringField('inputText', validators=[DataRequired()])
    submit = SubmitField('Process')