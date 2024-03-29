from app import db
from flask import render_template, url_for, redirect, Blueprint, flash, abort, request
from flask_login import current_user, login_required
from app.models import Portfolio, Achievementss
from app.portfolio.forms import PortfolioForm


port = Blueprint('port', __name__)


@port.route('/create_portfolio', methods=['POST', 'GET'])
@login_required
def create_portfolio():
    if current_user.port:
        flash('You already have portfolio, delete it first', 'danger')
        return redirect(url_for('main.home'))
    form = PortfolioForm()
    if form.validate_on_submit():
        port = Portfolio(title=form.title.data, author=current_user.username, content=form.content.data,
                         about=form.about.data, avg=form.avg.data,
                         school=form.school.data, background_color=form.background_color.data,
                         font_color=form.font_color.data, creator=current_user)
        db.session.add(port)
        db.session.commit()
        flash('Success', 'success')
        return redirect(url_for('port.portfolio'))
    return render_template('create_portfolio.html', form=form)


@port.route('/portfolio')
@login_required
def portfolio():
    user = current_user.username
    achieves = Achievementss.query.filter_by(user_id=current_user.id)
    port = Portfolio.query.filter_by(user_id=current_user.id).first()
    if port is None:
        flash('You don\'t have any portfolio. Create your first!', 'info')
        return redirect(url_for('port.create_portfolio'))
    return render_template('portfolio.html', port=port, user=user, achieves=achieves)


@port.route('/portfolio/update', methods=['POST', 'GET'])
@login_required
def port_title_update():
    port = Portfolio.query.filter_by(user_id=current_user.id).first()
    if port.creator != current_user:
        abort(403)
    form = PortfolioForm()
    if form.validate_on_submit():
        port.title = form.title.data
        port.content = form.content.data
        port.about = form.about.data
        port.link = form.link.data
        port.avg = form.avg.data
        port.school = form.school.data
        port.background_color = form.background_color.data
        port.font_color = form.font_color.data
        db.session.commit()
        flash('Your portfolio has been updated', 'success')
        return redirect(url_for('port.portfolio'))
    elif request.method == 'GET':
        form.title.data = port.title
        form.content.data = port.content
        form.about.data = port.about
        form.link.data = port.link
        form.avg.data = port.avg
        form.school.data = port.school
        form.background_color.data = port.background_color
        form.font_color.data = port.font_color
    return render_template('create_portfolio.html', form=form)


@port.route("/port/delete", methods=['POST'])
@login_required
def delete_port():
    port = Portfolio.query.filter_by(user_id=current_user.id).first()
    if port.creator != current_user:
        abort(403)
    db.session.delete(port)
    db.session.commit()
    flash('Your portfolio has been deleted', 'success')
    return redirect(url_for('main.home'))


# TODO: Возможность менять цвета портфолио с помощью БД




