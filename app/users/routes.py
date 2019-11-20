from flask import render_template, url_for, request, redirect, flash, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, AchievementsForm
from app import bcrypt, db
from app.models import User, Achievementss
from app.users.utils import save_picture


users = Blueprint('users', __name__)


@users.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to login', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)


@users.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful, Please check username and password', 'danger')
    return render_template('login.html', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file=image_file, form=form)


@users.route('/account/achievements', methods=['GET', 'POST'])
@login_required
def achievements():
    form = AchievementsForm()
    achieves = Achievementss.query.filter_by(user_id=current_user.id)
    if form.validate_on_submit():
        achievement = Achievementss(title=form.title.data, type=form.type.data, user_id=current_user.id)
        db.session.add(achievement)
        db.session.commit()
        flash('Your achievement now is in portfolio', 'success')
        return redirect(url_for('users.achievements'))
    return render_template('achievements.html', form=form, achieves=achieves)


@users.route('/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_achieve(id):
    achieve_to_delete = Achievementss.query.get_or_404(id)
    if achieve_to_delete.user_id != current_user.id:
        return 'You can\'t delete this one'
    db.session.delete(achieve_to_delete)
    db.session.commit()
    return redirect(url_for('users.achievements'))
