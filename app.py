from extensions import db, login_manager, mail, migrate
from flask import redirect, flash, url_for, session, render_template, Flask
from routes import AuthenticationBlueprint, UserBlueprint, WorkerBlueprint
from models import Services, Users, WorkerProfile
from datetime import timedelta
import os
import flask
from flask_login import current_user


def create_app():
    base_dir = os.path.dirname(os.path.realpath(__file__))

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        base_dir, "service_hub.db"
    )

    # app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql db link here'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "4f557e8e5eb51bfb7c42"
    app.config["DEBUG"] = False
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USERNAME"] = os.getenv("EMAIL_USER")
    app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_PASS")
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True

    # print(os.getenv("EMAIL_USER"), "eemail user", type(os.getenv("EMAIL_USER")))
    # print(os.getenv("EMAIL_PASS"), "eemail pass", type(os.getenv("EMAIL_PASS")))

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # The decorator that loads the user using the user's id
    @login_manager.user_loader
    def user_loader(id):
        return Users.query.get(id)

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    # handler for unauthorized
    @app.errorhandler(401)
    def unauthorized(e):
        session["alert"] = "Login to access this page"
        session["bg_color"] = "danger"
        return redirect(url_for("auth.login"))

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=20)
        session.modified = True
        flask.g.user = current_user

    app.register_blueprint(AuthenticationBlueprint)
    app.register_blueprint(UserBlueprint)
    app.register_blueprint(WorkerBlueprint)

    return app
