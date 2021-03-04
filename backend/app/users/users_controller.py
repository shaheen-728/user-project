import hashlib
import logging

import os
from datetime import datetime, timedelta
from flask import render_template
from .users_models import Users, EducationDetails, EmailSettings
from ..extensions import app, g
from .utils import create, fetch, fetch_list, hash_password, serialize_to_json

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

dir_path = os.path.dirname(os.path.realpath(__file__))


def create_user_ctrl(obj):
    referred_by_hash = obj.pop("referred_by_hash", None)
    password_unhash = obj["password"]
    obj["password"] = hash_password(password_unhash)

    now = datetime.now()
    obj["one_time_hash"] = hashlib.sha256(str(now).encode("utf-8")).hexdigest()
    obj["is_active"] = True
    obj["credits"] = 50
    obj["user_type"] = "Creator"  # To be changed to general user later
    user = Users(**obj)
    create(user)
    return serialize_to_json(user)


def user_education_details_ctrl(obj):
    obj["user_id"] = str(g.user.id)
    user_update = EducationDetails(**obj)
    if EducationDetails.percentage_of_10th is None:
        create(user_update)
    else:
        g.session.query(EducationDetails).filter(
            g.user.id == EducationDetails.user_id
        ).delete()
        g.session.commit()
        create(user_update)
    return serialize_to_json(user_update)


def get_user_education_details_ctrl():
    user = g.session.query(Users).get(g.user.id)
    education_details = (
        g.session.query(EducationDetails)
        .filter(g.user.id == EducationDetails.user_id)
        .first()
    )
    user_education = serialize_to_json(user)
    user_education["education_details"] = serialize_to_json(education_details)
    return user_education


def get_user_list_ctrl():
    all_users = g.session.query(Users).all()
    response_list = []
    for user in all_users:
        response_list.append(
            {"first_name": user.first_name, "email": user.email, "id": str(user.id)}
        )
    return response_list


def get_user_list_ctr_country(country):
    all_users = g.session.query(Users).filter(Users.country == country).all()
    response_list = []
    for user in all_users:
        response_list.append(
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "id": str(user.id),
                "gender": user.gender,
                "country": user.country,
            }
        )
    return response_list


def get_user_list_ctr_gender(gender):
    all_users = g.session.query(Users).filter(Users.gender == gender).all()
    response_list = []
    for user in all_users:
        response_list.append(
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "id": str(user.id),
                "gender": user.gender,
                "country": user.country,
            }
        )
    return response_list


def get_user_list_ctr_first_name(first_name):
    all_users = g.session.query(Users).filter(Users.first_name == first_name).all()
    response_list = []
    for user in all_users:
        response_list.append(
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "id": str(user.id),
                "gender": user.gender,
                "country": user.country,
            }
        )
    return response_list


def get_user_list_ctr_update_first_name(email, first_name):
    response_list = []
    if first_name == "":
        return response_list
    all_users = g.session.query(Users).filter(Users.email == email).first()
    all_users.first_name = first_name
    g.session.commit()

    response_list.append(
        {
            "first_name": all_users.first_name,
            "last_name": all_users.last_name,
            "email": all_users.email,
            "id": str(all_users.id),
            "gender": all_users.gender,
            "country": all_users.country,
        }
    )
    return response_list


def get_user_list_ctrl_sort(first_name):
    all_users = g.session.query(Users).order_by(Users.first_name.desc()).all()

    response_list = []
    for user in all_users:
        response_list.append(
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "id": str(user.id),
                "gender": user.gender,
                "country": user.country,
            }
        )
    return response_list


def get_user_list_ctrl_sort_by_order(sort_by, sort_order):
    all_users = g.session.query(Users).order_by(
        getattr(getattr(Users, sort_by), sort_order)()
    )

    response_list = []
    for user in all_users:
        response_list.append(
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "id": str(user.id),
                "gender": user.gender,
                "country": user.country,
            }
        )
    return response_list


def get_user_self_ctrl(user_id=None):
    if not user_id:
        user_id = g.user.id
    user_serialized = fetch(Users, {"id": user_id})
    return user_serialized


def send_pending_reg_emails_link_ctrl():
    all_pending_reg_users = g.session.query(Users).filter(Users.is_active == False).all()
    for user in all_pending_reg_users:
        if user.created_at > (datetime.today() - timedelta(days=3)):
            email_setting_email = g.session.query(EmailSettings.email).filter(user.id == EmailSettings.user_id).first()
            email_setting_email = [x for x in email_setting_email]
            send_activate_email_to_user(user.email, user.first_name, user.one_time_hash, email_setting_email[0])
    return {"Success": True}


def send_activate_email_to_user(email, first_name, one_time_hash,email_setting_email):
    subject = "Account Activation email - Abekus.com!"
    send_email_new(email, subject, 'ref_pending_reg.html',
                   {"first_name": first_name, "activation_link": activation_link_ctrl(one_time_hash)})


def activation_link_ctrl(one_time_hash):
    activation_link = app.config["BACKEND_URL"] + "/user/verify-registration?hash=" + one_time_hash
    return activation_link

def send_email_new(to_email, subject, template_name, template_args, rollbar=None):
    # Todo: make this async again
    # mailing_queue_ses.delay(to_email, subject, content)
    try:
        template_args["unsubscribe_link"] = f'{app.config["BACKEND_URL"]}/user/unsubscribe_emails?email={to_email}'
        content = render_template(template_name, **template_args)
        logging.warning(to_email)
        return
    except Exception as ex:
        rollbar.report_exc_info()

