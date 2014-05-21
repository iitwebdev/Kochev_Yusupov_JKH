#coding: utf-8
from datetime import datetime

from pyramid.view import view_config, forbidden_view_config

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.security import remember, authenticated_userid, forget
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from .models import (
    DBSession,
    User,
    login,
    register,
    pas_gen, send_email,
    History, Service, Country, Region, Tarif)


@forbidden_view_config()
def forbidden_view(request):
    # do not allow a user to login if they are already logged in
    if authenticated_userid(request):
        return HTTPForbidden()
    loc = request.route_url('login', _query=(('next', request.path),))
    return HTTPFound(location=loc)


def auth_required(func):
    def wrapper(request):
        owner = authenticated_userid(request)
        if owner is None:
            raise HTTPForbidden()
        return func(request)

    return wrapper


def get_current_user(request):
    try:
        id_ = authenticated_userid(request)
        # import pdb; pdb.set_trace()
        session = DBSession()
        return session.query(User).get(id_)
    except:
        return None


@view_config(route_name='home', renderer='templates/home.jinja2')
def my_view(request):
    if get_current_user(request):
        return {'login': True}
    else:
        return {'login': False}


@view_config(route_name='about', renderer='templates/about.jinja2')
def about_view(request):
    return {
        'About': u'Создать удобный для вас удобный и простой сервис.'
                 u'С помощью данного сервиса у вас появиться возможность хранить все данные в одном месте, '
                 u'а так же очень просто рассчитывать свои расходы. ',

    }


@view_config(route_name='calculate', renderer='templates/calculate.jinja2')
@auth_required
def calculate_view(request):
    nxt = request.params.get('next') or request.route_url('user')
    session = DBSession()
    countries = session.query(Country).all()
    regions = session.query(Region).all()
    tarifs = session.query(Tarif)
    services = session.query(Service).all()
    if 'contry' and 'region' and 'tarif' and 'value' and 'date' in request.POST:
        # country = session.query(Country).filter(Country.id == int(request.POST['country'])).one()
        # region = session.query(Region).filter(Region.id == int(request.POST['region'])).one()
        tarif = tarifs.filter(Tarif.id == int(request.POST['tarif'])).one()
        value = int(request.POST['value'])
        dateISO = (request.POST['date'])
        date = datetime.strptime(dateISO, "%Y-%m-%d").date()
        cost = calculate(tarif, value)
        history = History(user_id=get_current_user(request).id, service_id=tarif.service_id,
                          date=date, cost=cost)
        session.add(history)
        session.commit()
        return HTTPFound(location=nxt)
    return {'project': 'JKH',
            'countries': countries,
            'regions': regions,
            'tarifs': tarifs.all(),
            'services': services,
            'login': True}


def calculate(tarif, value):
    return tarif.price * value


@view_config(route_name='user', renderer='templates/user.jinja2')
@auth_required
def user_view(request):
    session = DBSession()
    history = session.query(History).filter(History.user_id == get_current_user(request).id)
    services = session.query(Service).all()
    return {
        'history': history,
        'services': services,
        'login': True
    }
    # countries = session.query(Country).all()
    # regions = session.query(Region).all()
    # tarifs = session.query(Tarif).all()
    # services = session.query(Service).all()
    # # return {'project': 'JKH',
    # #         'countries': countries,
    # #         'regions': regions,
    # #         'tarifs': tarifs,
    # #         'services': services,
    # #         'login': True}


@view_config(route_name='news', renderer='templates/news.jinja2')
def news_view(request):
    return {'project': 'JKH'}


@view_config(route_name='registration', renderer='templates/registration.jinja2')
def registration_view(request):
    nxt = request.params.get('next') or request.route_url('home')
    did_fail = False
    if 'email' in request.POST:
        user = register(
            request.POST["name"], request.POST["email"],
            request.POST["password"]
        )
        # print(user)
        if user:
            headers = remember(request, user.id)
            return HTTPFound(location=nxt, headers=headers)
        else:
            did_fail = True
    return {
        'login': "",
        'next': nxt,
        'failed_attempt': did_fail,
    }


@view_config(route_name='login', renderer='templates/login.jinja2')
def login_view(request):
    nxt = request.params.get('next') or request.route_url('home')
    did_fail = False
    if 'email' in request.POST:
        #LOGIN PROCESSING
        user = login(request.POST["email"], request.POST["password"])
        if user:
            headers = remember(request, user.id)
            return HTTPFound(location=nxt, headers=headers)
        else:
            did_fail = True
    return {
        'login': "",
        'next': nxt,
        'failed_attempt': did_fail,
    }


@view_config(route_name='passremind', renderer='templates/passremind.jinja2')
def pass_remind_view(request):
    nxt = request.params.get('next') or request.route_url('home')
    did_fail = False
    if 'email' in request.POST:
        password = remind_pass(request.POST["email"])
        if password:
            send_email(request.POST["email"], str(password), 2)
            return HTTPFound(location=nxt)
        else:
            did_fail = True
    return {
        'login': "",
        'next': nxt,
        'failed_attempt': did_fail,
    }


def remind_pass(email):
    session = DBSession()
    try:
        user = session.query(User).filter(User.email == email).one()
        user.password = pas_gen()
        session.add(user)
        session.commit()
        return user.password
    except MultipleResultsFound:
        return False
    except NoResultFound:
        return False


@view_config(route_name='logout')
def logout_view(request):
    headers = forget(request)
    loc = request.route_url('home')
    return HTTPFound(location=loc, headers=headers)


@view_config(route_name='settings', renderer='templates/settings.jinja2')
@auth_required
def settings_view(request):
    did_fail = False
    user = get_current_user(request)
    if 'password' in request.POST:
        new_password = change_pass(user.email, request.POST["password"])
        if new_password:
            send_email(user.email, str(request.POST["password"]), 3)
            return {"Messege": u"Ваш пароль успешно изменен"}
        else:
            did_fail = True
    return {
        'login': True,
        'failed_attempt': did_fail,
    }


def change_pass(email, password):
    session = DBSession()
    try:
        user = session.query(User).filter(User.email == email).one()
        user.password = password
        session.add(user)
        session.commit()
        return True
    except MultipleResultsFound:
        return False
    except NoResultFound:
        return False
    except:
        return False