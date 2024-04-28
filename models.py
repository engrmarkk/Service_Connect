from extensions import db
import uuid
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin


def generate_hex():
    return uuid.uuid4().hex


class Services(db.Model):
    __tablename__ = "services"
    id = db.Column(
        db.String(120), primary_key=True, default=generate_hex, nullable=False
    )
    name = db.Column(db.String(180), unique=True, nullable=False)
    description = db.Column(db.String(120), nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # relationship
    worker_profile = db.relationship("WorkerProfile", backref="services")


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(
        db.String(120), primary_key=True, default=generate_hex, nullable=False
    )
    username = db.Column(db.String(180), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    profile_picture = db.Column(db.Text)
    phone = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    local_government = db.Column(db.String(120), nullable=True)
    otp = db.Column(db.String(6), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_worker = db.Column(db.Boolean, default=False)
    otp_verified = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # relationship
    worker_profile = db.relationship("WorkerProfile", backref="users", lazy="joined")


class WorkerProfile(db.Model, UserMixin):
    __tablename__ = "worker_profile"
    id = db.Column(
        db.String(120), primary_key=True, default=generate_hex, nullable=False
    )
    company = db.Column(db.String(180), nullable=True)
    description = db.Column(db.String(120), nullable=True)
    rate = db.Column(db.Float, nullable=True)
    work_pic1 = db.Column(db.Text)
    work_pic2 = db.Column(db.Text)
    work_pic3 = db.Column(db.Text)
    service_offered = db.Column(db.ForeignKey("services.id"))
    user = db.Column(db.ForeignKey("users.id"))


services = [
    "Plumber",
    "Automotive services",
    "Drivers",
    "Cleaning Services",
    "Electrician",
    "Carpenter",
    "Painter",
    "Housekeeping",
    "Mechanic",
    "Nanny",
    "Developer",
    "Gardener",
    "Security Services",
    "Interior Designer",
    "Tutoring Services",
    "Event Planning",
    "Fitness Trainer",
    "Photographer",
    "Catering Services",
    "Legal Services",
    "Financial Advisor",
    "Graphic Designer",
    "Web Designer",
    "Content Writer",
    "Social Media Management",
    "Marketing Consultant",
]


def save_services():
    for service in services:
        print(service)
        service = Services(name=service)
        db.session.add(service)
        try:
            db.session.commit()
        except IntegrityError as e:
            print(e)
            db.session.rollback()
    return True


def get_services():
    services = Services.query.all()
    return services
