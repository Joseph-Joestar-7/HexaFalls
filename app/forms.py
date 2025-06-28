from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# For signup
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

# For login
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# For completing premium user profile
class ProfileForm(FlaskForm):
    class_level = SelectField("Class Level", validators=[DataRequired()], choices=[])
    target_exam = SelectField("Target Exam", validators=[DataRequired()], choices=[])
    subjects = SelectMultipleField("Subjects", validators=[DataRequired()], choices=[])
    submit = SubmitField("Save Profile")
