from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from helpers import (validate_input, check_username_exist,
                     check_email_exist, create_user, return_user,
                     generate_otp)
from passlib.hash import pbkdf2_sha256 as sha256
from flask_login import login_user, logout_user, logout_user, login_required

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    alert = session.pop("alert", None)
    bg_color = session.pop("bg_color", None)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            alert = "Please enter your email"
            bg_color = "danger"
            return render_template("login.html", alert=alert, bg_color=bg_color, email=email, password=password, login=True)

        if not password:
            alert = "Please enter your password"
            bg_color = "danger"
            return render_template("login.html", alert=alert, bg_color=bg_color, email=email, password=password, login=True)

        user = return_user(email)
        if user:
            if sha256.verify(password, user.password):
                login_user(user)
                if not user.otp_verified:
                    session["alert"] = "Please verify your account"
                    session["bg_color"] = "warning"
                    return redirect(url_for("auth.verify_otp"))
                if user.is_admin:
                    session["alert"] = "Login successful"
                    session["bg_color"] = "success"
                    return redirect(url_for("admin.home"))
                elif user.is_worker:
                    if not user.worker_profile:
                        session["alert"] = "Please update your profile"
                        session["bg_color"] = "warning"
                        return redirect(url_for("worker.update_profile"))
                    else:
                        session["alert"] = "Login successful"
                        session["bg_color"] = "success"
                        return redirect(url_for("worker.home"))
                else:
                    session["alert"] = "Login successful"
                    session["bg_color"] = "success"
                    return redirect(url_for("user.home"))
            else:
                alert = "Incorrect password"
                bg_color = "danger"
                return render_template("login.html", alert=alert, bg_color=bg_color, email=email, password=password, login=True)
        else:
            alert = "User does not exist"
            bg_color = "danger"
            return render_template("login.html", alert=alert, bg_color=bg_color, email=email, password=password, login=True)
    return render_template("login.html", alert=alert, bg_color=bg_color, login=True)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        profile_picture = request.form.get("profile_picture")
        phone = request.form.get("phone")
        country = request.form.get("country")
        state = request.form.get("state")
        local_government = request.form.get("local_government")
        user_type = request.form.get("user_type")

        alert = validate_input(username, email, password,
                               profile_picture, phone, country,
                               state, local_government, user_type)
        if alert:
            return render_template("register.html", alert=alert,
                                   bg_color="danger", username=username,
                                   email=email, password=password, profile_picture=profile_picture,
                                   phone=phone, country=country, state=state, local_government=local_government,
                                   user_type=user_type)

        if user_type == "worker":
            is_worker = True
        else:
            is_worker = False

        if check_username_exist(username):
            return render_template("register.html", alert="Username already exist",
                                   bg_color="danger", username=username,
                                   email=email, password=password, profile_picture=profile_picture,
                                   phone=phone, country=country, state=state, local_government=local_government,
                                   user_type=user_type)

        if check_email_exist(email):
            return render_template("register.html", alert="Email already exist",
                                   bg_color="danger", username=username,
                                   email=email, password=password, profile_picture=profile_picture,
                                   phone=phone, country=country, state=state, local_government=local_government,
                                   user_type=user_type)

        hashed_password = sha256.hash(password)

        otp = generate_otp()

        user = create_user(username, email, hashed_password, profile_picture,
                           phone, country, state, local_government,
                           is_worker, otp)

        if user:
            session["alert"] = "Pls Verify your email."
            session["bg_color"] = "info"
            login_user(user)
            return redirect(url_for("auth.verify_otp"))
        else:
            return render_template("register.html", alert="Something went wrong",
                                   bg_color="danger", username=username,
                                   email=email, password=password, profile_picture=profile_picture,
                                   phone=phone, country=country, state=state, local_government=local_government,
                                   user_type=user_type)

    return render_template("register.html")


@auth.route("/verify-otp", methods=["GET", "POST"])
@login_required
def verify_otp():
    return render_template("verify_otp.html")
