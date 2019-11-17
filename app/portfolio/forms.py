from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, FileField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


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


class PortfolioTitleUpdate(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Update')


class PortfolioContentUpdate(FlaskForm):
    content = StringField('Content', validators=[DataRequired()])
    submit = SubmitField('Update')


class PortfolioAboutUpdate(FlaskForm):
    about = StringField('About', validators=[DataRequired()])
    submit = SubmitField('Update')