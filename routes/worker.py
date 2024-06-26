from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import (
    login_user,
    logout_user,
    logout_user,
    login_required,
    current_user,
)
from models import WorkerProfile, get_services
from decorator import worker_required
import cloudinary.uploader
import cloudinary_config
from extensions import mail, db

worker = Blueprint("worker", __name__)


@worker.route("/home")
@login_required
@worker_required
def home():
    alert = session.pop("alert", None)
    bg_color = session.pop("bg_color", None)
    return render_template(
        "worker/home.html", home=True, alert=alert, bg_color=bg_color
    )


@worker.route("/update_profile", methods=["GET", "POST"])
@login_required
@worker_required
def update_profile():
    alert = session.pop("alert", None)
    bg_color = session.pop("bg_color", None)
    servs = get_services()
    if request.method == "POST":
        company = request.form.get("company")
        description = request.form.get("description")
        rate = request.form.get("rate")
        work_pic1 = request.files.get("work_pic1")
        work_pic2 = request.files.get("work_pic2")
        work_pic3 = request.files.get("work_pic3")
        service_offered = request.form.get("service_offered")
        user = current_user.id
        print(rate, "rate")
        if not company:
            alert = "Please enter your company name"
            bg_color = "danger"
            return render_template(
                "worker/update_profile.html",
                alert=alert,
                bg_color=bg_color,
                company=company,
                description=description,
                rate=rate,
                work_pic1=work_pic1,
                work_pic2=work_pic2,
                work_pic3=work_pic3,
                service_offered=service_offered,
            )
        if not description:
            alert = "Please enter your description"
            bg_color = "danger"
            return render_template(
                "worker/update_profile.html",
                alert=alert,
                bg_color=bg_color,
                company=company,
                description=description,
                rate=rate,
                work_pic1=work_pic1,
                work_pic2=work_pic2,
                work_pic3=work_pic3,
                service_offered=service_offered,
            )
        if not service_offered:
            alert = "Please enter your service offered"
            bg_color = "danger"
            return render_template(
                "worker/update_profile.html",
                alert=alert,
                bg_color=bg_color,
                company=company,
                description=description,
                rate=rate,
                work_pic1=work_pic1,
                work_pic2=work_pic2,
                work_pic3=work_pic3,
                service_offered=service_offered,
            )
        if not work_pic1 and not work_pic2 and not work_pic3:
            alert = "Please enter your work pictures"
            bg_color = "danger"
            return render_template(
                "worker/update_profile.html",
                alert=alert,
                bg_color=bg_color,
                company=company,
                description=description,
                rate=rate,
                work_pic1=work_pic1,
                work_pic2=work_pic2,
                work_pic3=work_pic3,
                service_offered=service_offered,
            )

        print(
            "company",
            company,
            "desc",
            description,
            "rate",
            rate,
            "work_pic1",
            work_pic1,
            "work_pic2",
            work_pic2,
            "work_pic3",
            work_pic3,
            "service_offered",
            service_offered,
            "user",
            user,
        )

        work_pics = [work_pic1, work_pic2, work_pic3]
        cloudinary_img_urls = []

        for res in work_pics:
            result = cloudinary.uploader.upload(
                res,
                folder="service_connect",
                transformation=[{"width": 176, "height": 176, "crop": "fill"}],
            )
            image_url = result["secure_url"]
            cloudinary_img_urls.append(image_url)

        worker_profile = WorkerProfile(
            company=company,
            description=description,
            rate=rate,
            work_pic1=cloudinary_img_urls[0],
            work_pic2=cloudinary_img_urls[1],
            work_pic3=cloudinary_img_urls[2],
            service_offered=service_offered,
            user=user,
        )
        db.session.add(worker_profile)
        try:
            db.session.commit()
            session["alert"] = "Profile updated successfully"
            session["bg_color"] = "success"
        except IntegrityError as e:
            print(e, "Worker Profile Not Added")
            db.session.rollback()
            session["alert"] = "Error updating profile"
            session["bg_color"] = "danger"
        except Exception as e:
            print(e, "Worker Profile Not Added")
            db.session.rollback()
            session["alert"] = "Error updating profile"
            session["bg_color"] = "danger"
        return redirect(url_for("worker.home"))

    return render_template(
        "worker/update_profile.html", alert=alert, bg_color=bg_color, servs=servs
    )
