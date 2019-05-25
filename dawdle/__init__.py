"""
Exports a function to create an instance of the Dawdle app.
"""

import os

from flask import Flask, render_template
from flask_assets import Environment
from flask_login import LoginManager
from flask_mail import Mail
from flask_mongoengine import MongoEngine
from flask_wtf.csrf import CSRFProtect

from dawdle.assets import bundles
from dawdle.version import __version__

assets = Environment()

csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

mail = Mail()

mongoengine = MongoEngine()

def create_app(testing=False):
    """
    Creates an instance of the Dawdle app.
    """

    app = Flask(__name__, instance_relative_config=True)
    config = app.config

    # load default config
    config.from_object('config.Default')

    # load instance config (if present)
    config.from_pyfile('config.py', silent=True)

    # load test config (if testing)
    if testing:
        config.from_object('config.Test')

    # load environment variables (if present)
    environ = os.environ
    config.update({
        'DEBUG': environ.get('DEBUG', str(config.get('DEBUG'))).lower() == 'true',
        'ENV': environ.get('ENV', config.get('ENV')),
        'MAIL_DEFAULT_SENDER': environ.get('MAIL_DEFAULT_SENDER', config.get('MAIL_DEFAULT_SENDER')),
        'MAIL_PASSWORD': environ.get('MAIL_PASSWORD', config.get('MAIL_PASSWORD')),
        'MAIL_PORT': int(environ.get('MAIL_PORT', config.get('MAIL_PORT'))),
        'MAIL_SERVER': environ.get('MAIL_SERVER', config.get('MAIL_SERVER')),
        'MAIL_SUPPRESS_SEND':
            environ.get('MAIL_SUPPRESS_SEND', str(config.get('MAIL_SUPPRESS_SEND'))).lower() == 'true',
        'MAIL_USE_SSL': environ.get('MAIL_USE_SSL', str(config.get('MAIL_USE_SSL'))).lower() == 'true',
        'MAIL_USE_TLS': environ.get('MAIL_USE_TLS', str(config.get('MAIL_USE_TLS'))).lower() == 'true',
        'MAIL_USERNAME': environ.get('MAIL_USERNAME', config.get('MAIL_USERNAME')),
        'MONGODB_DB': environ.get('MONGODB_DB', config.get('MONGODB_DB')),
        'MONGODB_HOST': environ.get('MONGODB_HOST', config.get('MONGODB_HOST')),
        'MONGODB_PASSWORD': environ.get('MONGODB_PASSWORD', config.get('MONGODB_PASSWORD')),
        'MONGODB_PORT': int(environ.get('MONGODB_PORT', config.get('MONGODB_PORT'))),
        'MONGODB_USERNAME': environ.get('MONGODB_USERNAME', config.get('MONGODB_USERNAME')),
        'SECRET_KEY': environ.get('SECRET_KEY', config.get('SECRET_KEY')),
        'SERVER_NAME': environ.get('SERVER_NAME', config.get('SERVER_NAME')),
        'SESSION_COOKIE_DOMAIN': environ.get('SESSION_COOKIE_DOMAIN', config.get('SESSION_COOKIE_DOMAIN')),
        'WTF_CSRF_ENABLED': environ.get('WTF_CSRF_ENABLED', str(config.get('WTF_CSRF_ENABLED'))).lower() == 'true',
    })

    config.update({
        'TESTING': testing,
        'VERSION': __version__,
    })

    # init extensions
    assets.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    mongoengine.init_app(app)

    # disable strict trailing slashes e.g. so /auth/login and /auth/login/ both resolve to same endpoint
    app.url_map.strict_slashes = False

    # register blueprints
    from dawdle.blueprints.auth import auth
    from dawdle.blueprints.home import home
    app.register_blueprint(auth)
    app.register_blueprint(home)

    # register asset bundles
    assets.register(bundles)

    # attach 404 error handler
    @app.errorhandler(404)
    def handle_404(error):
        return render_template('error/404.html', error=error), 404

    # attach 500 error handler
    @app.errorhandler(500)
    def handle_500(error):
        return render_template('error/500.html', error=error), 500

    # disable caching when debugging
    if app.debug:
        @app.after_request
        def after_request(response):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Expires'] = 0
            response.headers['Pragma'] = 'no-cache'
            return response

    return app