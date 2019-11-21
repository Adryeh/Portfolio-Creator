from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager
from flask_login import UserMixin


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
    background_color = db.Column(db.String, default='#add8e6')
    font_color = db.Column(db.String, default='black')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return '<Portfolio %r>' % self.title


class Achievementss(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)