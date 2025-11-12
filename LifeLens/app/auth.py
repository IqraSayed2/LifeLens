from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/', methods=['GET', 'POST'])
def login_signup():
    """
    Single page handles both login and signup.
    We'll check which form was submitted using a hidden input 'form_type'.
    """
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # ---------- LOGIN ----------
        if form_type == 'login':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid username or password.', 'error')
                return redirect(url_for('auth.login_signup'))

        # ---------- SIGNUP ----------
        elif form_type == 'signup':
            name = request.form.get('name')
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm = request.form.get('confirm')

            if password != confirm:
                flash('Passwords do not match.', 'error')
                return redirect(url_for('auth.login_signup'))

            if not username:
                flash('Username is required.', 'error')
                return redirect(url_for('auth.login_signup'))

            if User.query.filter_by(username=username).first():
                flash('Username already taken.', 'error')
                return redirect(url_for('auth.login_signup'))

            if email and User.query.filter_by(email=email).first():
                flash('Email already registered.', 'error')
                return redirect(url_for('auth.login_signup'))

            new_user = User(
                name=name,
                username=username,
                email=email,
                password=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('auth.login_signup'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login_signup'))
