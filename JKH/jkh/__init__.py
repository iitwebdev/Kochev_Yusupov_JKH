from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from .models import (
    DBSession,
    Base,
    User, Country, Region, Service, Tarif, History)


def not_found(request):
    return HTTPNotFound('Not found, bro.')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.', poolclass=NullPool)
    DBSession.configure(bind=engine)
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    Base.metadata.bind = engine
    config = Configurator(
        settings=settings,
        session_factory=my_session_factory,
        authentication_policy=SessionAuthenticationPolicy())
    Base.metadata.create_all(engine)
    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("jkh:templates")
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('user', '/user')
    config.add_route('news', '/news')
    config.add_route('about', '/about')
    config.add_route('registration', '/registration')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('passremind', '/passremind')
    config.add_route('settings', '/settings')
    config.add_route('calculate', '/calculate')
    config.add_notfound_view(not_found, append_slash=True)

    config.include('sacrud.pyramid_ext', route_prefix='/admin')
    settings = config.registry.settings
    settings['sacrud.models'] = {"": [User, Country, Tarif, Service, Region, History]}

    config.scan()
    return config.make_wsgi_app()
