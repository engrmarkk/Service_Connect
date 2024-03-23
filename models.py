from extensions import db
import uuid
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin


def generate_hex():
    return uuid.uuid4().hex


class Services(db.Model):
    __tablename__ = "services"
    id = db.Column(db.String(120), primary_key=True, default=generate_hex, nullable=False)
    name = db.Column(db.String(180), unique=True, nullable=False)
    description = db.Column(db.String(120), nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # relationship
    worker_profile = db.relationship("WorkerProfile", backref="services")


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.String(120), primary_key=True, default=generate_hex, nullable=False)
    username = db.Column(db.String(180), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    profile_picture = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)
    is_worker = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # relationship
    worker_profile = db.relationship("WorkerProfile", backref="users")


class WorkerProfile(db.Model, UserMixin):
    __tablename__ = "worker_profile"
    id = db.Column(db.String(120), primary_key=True, default=generate_hex, nullable=False)
    service_offered = db.Column(db.ForeignKey("services.id"))
    user = db.Column(db.ForeignKey("users.id"))


services = [
    "Plumber", "Automotive services", "Drivers", "Cleaning Services", "Electrician",
    "Carpenter", "Painter", "Housekeeping",
    "Mechanic", "Nanny", "Developer",
    "Gardener", "Security Services", "Interior Designer", "Tutoring Services",
    "Event Planning", "Fitness Trainer", "Photographer", "Catering Services",
    "Legal Services", "Financial Advisor", "Graphic Designer", "Web Designer",
    "Content Writer", "Social Media Management", "Marketing Consultant"
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
