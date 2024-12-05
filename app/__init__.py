import os
from flask import Flask, request, redirect
from flask_cors import CORS
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_login import LoginManager
from .models import db, User
from .api.user_routes import user_routes
from .api.auth_routes import auth_routes
from .api.card_routes import card_routes
from .api.wallet_routes import wallet_routes
from .api.category_routes import category_routes
from .api.spending_routes import spending_routes
from .seeds import seed_commands
from .config import Config

# Setup login manager
login = LoginManager()
login.login_view = 'auth.unauthorized'


def create_app():
    app = Flask(__name__, static_folder='../react-vite/dist', static_url_path='/')

    # App configuration
    app.config.from_object(Config)

    # Initialize plugins
    login.init_app(app)
    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    # Register blueprints
    app.register_blueprint(user_routes, url_prefix='/api/users')
    app.register_blueprint(auth_routes, url_prefix='/api/auth')
    app.register_blueprint(card_routes, url_prefix='/api/cards')
    app.register_blueprint(wallet_routes, url_prefix='/api/wallet')
    app.register_blueprint(category_routes, url_prefix='/api/categories')
    app.register_blueprint(spending_routes, url_prefix='/api/spending')

    # Register CLI commands
    app.cli.add_command(seed_commands)

    # Redirect HTTP to HTTPS in production
    @app.before_request
    def https_redirect():
        if os.environ.get('FLASK_ENV') == 'production':
            if request.headers.get('X-Forwarded-Proto') == 'http':
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)

    # Add CSRF token to cookies
    @app.after_request
    def inject_csrf_token(response):
        response.set_cookie(
            'csrf_token',
            generate_csrf(),
            secure=True if os.environ.get('FLASK_ENV') == 'production' else False,
            samesite='Strict' if os.environ.get('FLASK_ENV') == 'production' else None,
            httponly=True
        )
        return response

    # API Documentation Route
    @app.route("/api/docs")
    def api_help():
        """
        Returns all API routes and their doc strings
        """
        acceptable_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        route_list = {
            rule.rule: [
                [method for method in rule.methods if method in acceptable_methods],
                app.view_functions[rule.endpoint].__doc__,
            ]
            for rule in app.url_map.iter_rules() if rule.endpoint != 'static'
        }
        return route_list

    # Serve React Frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def react_root(path):
        """
        This route will direct to the public directory in our
        react builds in the production environment for favicon
        or index.html requests
        """
        if path == 'favicon.ico':
            return app.send_from_directory('public', 'favicon.ico')
        return app.send_static_file('index.html')

    # Handle 404 errors by serving the React app
    @app.errorhandler(404)
    def not_found(e):
        return app.send_static_file('index.html')

    return app
