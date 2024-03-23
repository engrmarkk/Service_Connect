from flask import Blueprint, redirect, render_template, url_for
from models import save_services, get_services
from flask_login import login_required
from decorator import user_required


user = Blueprint("user", __name__)


@user.route("/")
def home():
    # save_services()
    serv = get_services()
    return render_template("home.html", home=True, services=serv)
