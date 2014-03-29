#coding: utf-8
from pyramid.view import view_config


@view_config(route_name='home', renderer='templates/home.jinja2')
def my_view(request):
    return {'project': 'JKH'}

@view_config(route_name='about', renderer='templates/about.jinja2')
def about_view(request):
    return {'About': u"Work!"}

@view_config(route_name='user', renderer='templates/user.jinja2')
def user_view(request):
    return {'project': 'JKH'}

@view_config(route_name='news', renderer='templates/news.jinja2')
def news_view(request):
    return {'project': 'JKH'}

@view_config(route_name='registration', renderer='templates/registration.jinja2')
def registration_view(request):
    return {'project': 'JKH'}

@view_config(route_name='login', renderer='templates/login.jinja2')
def login_view(request):
    return {'project': 'JKH'}