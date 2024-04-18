from flask import Blueprint, redirect, render_template, url_for, session
from models import save_services, get_services
from flask_login import login_required, current_user
from decorator import user_required
from decorator import complete_profile


user = Blueprint("user", __name__)


@user.route("/")
@complete_profile
def home():
    # save_services()
    alert = session.pop("alert", None)
    bg_color = session.pop("bg_color", None)
    serv = get_services()
    return render_template("home.html", home=True, services=serv, alert=alert, bg_color=bg_color)
