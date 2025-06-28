from functools import wraps
from flask_login import current_user
from app import app, db
from flask import flash, render_template, redirect, url_for, session, request, current_app
from app.forms import RegisterForm,LoginForm
from app.models import User
import os

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@app.context_processor
def inject_current_accounts():
    return {
        'current_user': get_current_user()
    }

def login_required_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            print("Please log in to access this page!!!")
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required_user
def dashboard():
    
    return render_template('dashboard.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:  # Check if already logged in
        return redirect(url_for('dashboard'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        user_data = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data 
        )
        db.session.add(user_data)
        db.session.commit()
        session['user_id'] = user_data.id
        return redirect(url_for('complete_profile'))

    return render_template('signup.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if 'user_id' in session:  # Check if already logged in
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(form.password.data):
            session['user_id'] = attempted_user.id
            return redirect(url_for('dashboard'))
        else:
            flash("Username and Password do not match! Please try again", "danger")

    return render_template('signin.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out')
    return redirect(url_for('signin'))