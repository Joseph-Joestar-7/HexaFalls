from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ProfileForm(FlaskForm):
    class_level = SelectField("Class Level", validators=[DataRequired()], choices=[])
    target_exam = SelectField("Target Exam", validators=[DataRequired()], choices=[])
    subjects = SelectMultipleField("Subjects", validators=[DataRequired()], choices=[])
    submit = SubmitField("Save Profile")
