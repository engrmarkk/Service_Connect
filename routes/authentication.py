from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from helpers import (
    validate_input,
    check_username_exist,
    check_email_exist,
    create_user,
    return_user,
    generate_otp,
)
from passlib.hash import pbkdf2_sha256 as sha256
from flask_login import (
    login_user,
    logout_user,
    logout_user,
    login_required,
    current_user,
)
from flask_mail import Message
from extensions import mail, db
import cloudinary
from decorator import check_logged_in, check_not_logged_in
import os
import cloudinary.uploader
import cloudinary_config
from datetime import datetime

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
@check_logged_in
def login():
    alert = session.pop("alert", None)
    bg_color = session.pop("bg_color", None)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            alert = "Please enter your email"
            bg_color = "danger"
            return render_template(
                "login.html",
                alert=alert,
                bg_color=bg_color,
                email=email,
                password=password,
                login=True,
            )

        if not password:
            alert = "Please enter your password"
            bg_color = "danger"
            return render_template(
                "login.html",
                alert=alert,
                bg_color=bg_color,
                email=email,
                password=password,
                login=True,
            )

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
                return render_template(
                    "login.html",
                    alert=alert,
                    bg_color=bg_color,
                    email=email,
                    password=password,
                    login=True,
                )
        else:
            alert = "User does not exist"
            bg_color = "danger"
            return render_template(
                "login.html",
                alert=alert,
                bg_color=bg_color,
                email=email,
                password=password,
                login=True,
            )
    return render_template("login.html", alert=alert, bg_color=bg_color, login=True)


@auth.route("/register", methods=["GET", "POST"])
@check_logged_in
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        profile_picture = request.files.get("profile_picture")
        phone = request.form.get("phone_number")
        country = request.form.get("country")
        state = request.form.get("state")
        local_government = request.form.get("local_government")
        user_type = request.form.get("user_type")

        print(
            "username: ",
            username,
            "email: ",
            email,
            "password: ",
            password,
            "profile_picture: ",
            profile_picture,
            "phone: ",
            phone,
            "country: ",
            country,
            "state: ",
            state,
            "local_government: ",
            local_government,
            "user_type: ",
            user_type,
        )

        alert = validate_input(
            username,
            email,
            password,
            profile_picture,
            phone,
            country,
            state,
            local_government,
            user_type,
        )
        if alert:
            return render_template(
                "register.html",
                alert=alert,
                bg_color="danger",
                username=username,
                email=email,
                password=password,
                pp=profile_picture,
                phone=phone,
                country=country,
                state=state,
                local_government=local_government,
                user_type=user_type,
            )

        if user_type == "worker":
            is_worker = True
        else:
            is_worker = False

        if check_username_exist(username):
            return render_template(
                "register.html",
                alert="Username already exist",
                bg_color="danger",
                username=username,
                email=email,
                password=password,
                profile_picture=profile_picture,
                phone=phone,
                country=country,
                state=state,
                local_government=local_government,
                user_type=user_type,
            )

        if check_email_exist(email):
            return render_template(
                "register.html",
                alert="Email already exist",
                bg_color="danger",
                username=username,
                email=email,
                password=password,
                profile_picture=profile_picture,
                phone=phone,
                country=country,
                state=state,
                local_government=local_government,
                user_type=user_type,
            )

        if password != confirm_password:
            return render_template(
                "register.html",
                alert="Passwords do not match",
                bg_color="danger",
                username=username,
                email=email,
                password=password,
                pp=profile_picture,
                phone=phone,
                country=country,
                state=state,
                local_government=local_government,
                user_type=user_type,
            )

        result = cloudinary.uploader.upload(
            profile_picture,
            folder="service_connect",
            transformation=[{"width": 176, "height": 176, "crop": "fill"}],
        )
        image_url = result["secure_url"]

        hashed_password = sha256.hash(password)

        otp = generate_otp()

        user = create_user(
            username,
            email,
            hashed_password,
            image_url,
            phone,
            country,
            state,
            local_government,
            is_worker,
            otp,
        )

        if user:
            session["alert"] = "Pls Verify your email."
            session["bg_color"] = "info"
            # login_user(user)
            try:
                msg = Message(
                    subject="Email Verification",
                    sender="Service Connect <easytransact.send@gmail.com>",
                    recipients=[email],
                )
                msg.html = render_template("email_verification.html", otp=str(otp))
                mail.send(msg)
            except Exception as e:
                print(e)
                flash("failed to verify email", "danger")
                return render_template("register.html", date=datetime.utcnow())
            print("Email sent")
            return redirect(url_for("auth.verify_otp", email=email))
        else:
            return render_template(
                "register.html",
                alert="Something went wrong",
                bg_color="danger",
                username=username,
                email=email,
                password=password,
                profile_picture=profile_picture,
                phone=phone,
                country=country,
                state=state,
                local_government=local_government,
                user_type=user_type,
            )

    return render_template("register.html")


@auth.route("/verify-otp/<string:email>", methods=["GET", "POST"])
@check_logged_in
def verify_otp(email):
    if current_user.is_authenticated:
        return redirect(url_for("user.home"))
    alert = session.get("alert")
    bg_color = session.get("bg_color")
    user = return_user(email)
    if not user:
        session["alert"] = "User does not exist"
        session["bg_color"] = "danger"
        return redirect(url_for("user.home"))
    if user.otp_verified:
        session["alert"] = "Already verified, login now"
        session["bg_color"] = "success"
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        otp = request.form.get("otp")
        print(otp)
        if not otp:
            alert = "Please enter OTP"
            bg_color = "danger"
            return render_template(
                "verify_otp.html", alert=alert, bg_color=bg_color, email=email
            )
        if len(otp) != 6 or not otp.isdigit():
            alert = "Please enter a valid OTP"
            bg_color = "danger"
            return render_template(
                "verify_otp.html", otp=otp, alert=alert, bg_color=bg_color, email=email
            )
        if otp == user.otp:
            session["alert"] = "Verification successful, login now"
            session["bg_color"] = "success"
            user.otp_verified = True
            db.session.commit()
            return redirect(url_for("auth.login"))
        else:
            alert = "Incorrect OTP"
            bg_color = "danger"
            return render_template(
                "verify_otp.html", otp=otp, alert=alert, bg_color=bg_color, email=email
            )
    return render_template(
        "verify_otp.html", alert=alert, bg_color=bg_color, email=email
    )


# resend otp
@auth.route("/resend-otp/<string:email>", methods=["GET"])
@check_logged_in
def resend_otp(email):
    if current_user.is_authenticated:
        return redirect(url_for("user.home"))
    user = return_user(email)
    if not user:
        session["alert"] = "User does not exist"
        session["bg_color"] = "danger"
        return redirect(url_for("user.home"))
    if user.otp_verified:
        session["alert"] = "Already verified, login now"
        session["bg_color"] = "success"
        return redirect(url_for("auth.login"))
    otp = generate_otp()
    user.otp = otp
    db.session.commit()
    try:
        msg = Message(
            subject="Email Verification",
            sender="Service Connect <easytransact.send@gmail.com>",
            recipients=[email],
        )
        msg.html = render_template("email_verification.html", otp=str(otp))
        mail.send(msg)
        session["alert"] = "OTP re-sent"
        session["bg_color"] = "success"
    except Exception as e:
        print(e)
        session["alert"] = "failed to verify email"
        session["bg_color"] = "danger"
    return redirect(url_for("auth.verify_otp", email=email))


@auth.route("/logout")
@check_not_logged_in
@login_required
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    logout_user()
    session["alert"] = "Logout successful"
    session["bg_color"] = "success"
    return redirect(url_for("user.home"))
