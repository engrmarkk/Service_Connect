from models import Users, db, WorkerProfile
from random import randint


def generate_otp():
    return randint(100000, 999999)


def validate_input(username, email, password, profile_picture, phone, country, state, local_government, user_type):
    if not username:
        return "Please enter your username"
    if not email:
        return "Please enter your email"
    if not password:
        return "Please enter your password"
    if not profile_picture:
        return "Please enter your profile picture"
    if not phone:
        return "Please enter your phone number"
    if not country:
        return "Please enter your country"
    if not state:
        return "Please enter your state"
    if not local_government:
        return "Please enter your local government"
    if not user_type:
        return "Please select your user type"
    return None


def create_user(username, email, password, profile_picture, phone, country, state, local_government, is_worker, otp):
    user = Users(
        username=username.lower(),
        email=email.lower(),
        password=password,
        profile_picture=profile_picture,
        phone=phone,
        country=country.lower(),
        state=state.lower(),
        local_government=local_government.lower(),
        is_worker=is_worker,
        otp=otp
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as e:
        print(e)
        db.session.rollback()
    return user


def check_username_exist(username):
    user = Users.query.filter_by(username=username.lower()).first()
    if user:
        return True
    return False


def check_email_exist(email):
    user = Users.query.filter_by(email=email.lower()).first()
    if user:
        return True
    return False


def return_user(email):
    return Users.query.filter_by(email=email.lower()).first()
