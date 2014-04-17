#coding: utf-8
from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.response import FileResponse
from pyramid.security import remember, authenticated_userid, forget
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from .models import (
    DBSession,
    User,
    login,
    register,
    pas_gen)

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
    id_ = authenticated_userid(request)
    # import pdb; pdb.set_trace()
    session = DBSession()
    return session.query(User).get(id_)

@view_config(route_name='home', renderer='templates/home.jinja2')
def my_view(request):
    return {'project': 'JKH'}

@view_config(route_name='about', renderer='templates/about.jinja2')
def about_view(request):
    return {'About': u"Work!"}

@view_config(route_name='user', renderer='templates/user.jinja2')
@auth_required
def user_view(request):
    return {'project': 'JKH'}

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
        print(user)
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