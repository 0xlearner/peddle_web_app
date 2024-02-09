import os

from flask import Flask

from .extensions import db

from .routes import main

from scraper.sel_peddle import get_access_token, run


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_CONN_URL")
    app.config["SECRET_KEY"] = "thisisasecret!"

    db.init_app(app)
    # with app.app_context():
    #     get_access_token()
    #     run()
    app.register_blueprint(main)

    return app
