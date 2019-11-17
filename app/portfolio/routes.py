from app import db
from flask import render_template, url_for, redirect, Blueprint, flash
from flask_login import current_user
from app.models import Portfolio
from app.portfolio.forms import PortfolioForm


port = Blueprint('port', __name__)


@port.route('/create_portfolio', methods=['POST', 'GET'])
def create_portfolio():
    form = PortfolioForm()
    if form.validate_on_submit():
        port = Portfolio(title=form.title.data, author=form.author.data, content=form.content.data,
                         about=form.about.data, link=form.link.data, avg=form.avg.data,
                         school=form.school.data, background_color=form.background_color.data,
                         font_color=form.font_color.data, creator=current_user)
        db.session.add(port)
        db.session.commit()
        flash('Success', 'success')
        return redirect(url_for('port.portfolio'))
    return render_template('create_portfolio.html', form=form)


@port.route('/portfolio')
def portfolio():

    port = Portfolio.query.filter_by(user_id=current_user.id).first()
    if port is None:
        flash('You don\'t have any portfolio. Create your first!', 'info')
        return redirect(url_for('port.create_portfolio'))
    return render_template('portfolio.html', port=port)