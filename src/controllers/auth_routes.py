from contextlib import contextmanager
from typing import Iterable

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.data_access.user_dal import UserDAL
from src.extensions import db
from src.forms.auth_forms import LoginForm, RegisterForm


auth_bp = Blueprint('auth', __name__)


ALLOWED_ROLES: Iterable[str] = ('student', 'staff')


@contextmanager
def get_db_session():
    """Context manager for database sessions compatible with Base models."""
    from src.models import Base
    # Create sessionmaker bound to the engine with Base's registry
    # The key is to ensure Base.metadata is bound to the engine
    Session = sessionmaker(bind=db.engine)
    session = Session()
    # Bind the session to Base's metadata
    Base.metadata.bind = db.engine
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _flash_form_errors(form):
    for field_name, errors in form.errors.items():
        field_label = form[field_name].label.text
        for error in errors:
            flash(f'{field_label}: {error}', 'error')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if form.role.data not in ALLOWED_ROLES:
            flash('Invalid role selected.', 'error')
            return render_template('auth/register.html', form=form)

        try:
            with get_db_session() as session:
                dal = UserDAL(session)
                user = dal.create_user(
                    name=form.name.data.strip(),
                    email=form.email.data.strip().lower(),
                    plaintext_password=form.password.data,
                    role=form.role.data,
                )
        except SQLAlchemyError:
            flash('An unexpected database error occurred. Please try again.', 'error')
            return render_template('auth/register.html', form=form)

        if user is None:
            flash('Registration failed. Email may already be in use.', 'error')
            return render_template('auth/register.html', form=form)

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    if form.errors:
        _flash_form_errors(form)

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('resources.list_resources'))

    form = LoginForm()

    if form.validate_on_submit():
        identifier = form.identifier.data.strip()
        password = form.password.data

        with get_db_session() as session:
            dal = UserDAL(session)
            user = dal.verify_user_credentials(identifier=identifier, plaintext_password=password)

        if user:
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('resources.list_resources'))

        flash('Invalid credentials. Please try again.', 'error')

    if form.errors:
        _flash_form_errors(form)

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

