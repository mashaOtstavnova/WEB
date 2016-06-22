from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
from .models.mymodel import (
    DBSession,Base)
from .routes import includeme

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.', poolclass=NullPool)
    DBSession.configure(bind=engine)
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    Base.metadata.bind = engine
    config = Configurator(settings=settings,
        session_factory=my_session_factory,
        authentication_policy=SessionAuthenticationPolicy())
    Base.metadata.create_all(engine)
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.add_jinja2_search_path("templates")
    includeme(config)
    config.scan()
    return config.make_wsgi_app()
