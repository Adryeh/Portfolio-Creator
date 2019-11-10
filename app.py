import os
import secrets
from PIL import Image
from flask import Flask, render_template, url_for, request, redirect, flash, current_app
from flask_login import login_user, current_user, logout_user, login_required, UserMixin, LoginManager
from flask_wtf.file import FileField, FileAllowed
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, FileField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    port = db.relationship('Portfolio', backref='creator', lazy=True)


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String)
    content = db.Column(db.Text)
    about = db.Column(db.Text)
    link = db.Column(db.String)
    avg = db.Column(db.Float)
    school = db.Column(db.String)
    background_color = db.Column(db.String)
    font_color = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return '<Portfolio %r>' % self.title



class RegistrationForm(FlaskForm):
    username: StringField = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email: StringField = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username exists. Please choose another!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email exists. Please choose another!')


class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username: StringField = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email: StringField = StringField('E-mail', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username exists. Please choose another!')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email exists. Please choose another!')



class PortfolioForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author')
    content = TextAreaField('Content')
    about = TextAreaField('About me')
    link = StringField('Achvmnts')
    avg = StringField('Avg')
    school = StringField('School')
    background_color = StringField('Choose background color (eg: green)')
    font_color = StringField('Choose font color (eg: white)')
    submit = SubmitField('Send')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/create_portfolio', methods=['POST', 'GET'])
def create_portfolio():
    form = PortfolioForm()
    if form.validate_on_submit():
        port = Portfolio(title=form.title.data, author=form.author.data, content=form.content.data,
                         about=form.about.data, link=form.link.data, avg=form.avg.data,
                         school=form.school.data, background_color=form.background_color.data,
                         font_color=form.font_color.data, creator=current_user)
        db.session.add(port)
        db.session.commit()
        return redirect(url_for('portfolio'))
    return render_template('create_portfolio.html', form=form)

@app.route('/portfolio')
def portfolio():
    port = Portfolio.query.first()
    return render_template('portfolio.html', port=port)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful, Please check username and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/account', methods=['POST', 'GET'])
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
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file=image_file, form=form)


if __name__ == '__main__':
    app.run(debug=True)
