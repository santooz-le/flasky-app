from datetime import datetime
from flask import render_template, session, redirect, url_for
from . import main
from .forms import NameForm
from .. import db
from ..models import User, Role
from ..email import send_email


def get_or_create_role(name):
    role = Role.query.filter_by(name=name).first()
    if role is None:
        role = Role(name=name)
        db.session.add(role)
        db.session.commit()
    return role


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            default_role = get_or_create_role('User')
            user = User(username=form.name.data, role_id=default_role.id)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            # Envia e-mail com o endereço extra informado no formulário
            extra_email = form.email.data.strip() if form.email.data else None
            send_email(form.name.data, extra_email=extra_email)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        form.email.data = ''
        return redirect(url_for('.index'))

    # Usuários agrupados: Admin primeiro, depois User
    admin_role = Role.query.filter_by(name='Admin').first()
    user_role = Role.query.filter_by(name='User').first()
    admins = admin_role.users.order_by(User.username).all() if admin_role else []
    users = user_role.users.order_by(User.username).all() if user_role else []

    return render_template('index.html',
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False),
                           admins=admins,
                           users=users,
                           current_time=datetime.utcnow())
