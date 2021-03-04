from flask import Blueprint,jsonify,request,abort,redirect,g

from .users_controller import (
    create_user_ctrl,
    get_user_list_ctrl,
    get_user_self_ctrl,
    get_user_list_ctr_country,
    get_user_list_ctr_gender,
    get_user_list_ctr_first_name,
    get_user_list_ctr_update_first_name,
    get_user_list_ctrl_sort,
    get_user_list_ctrl_sort_by_order,
    user_education_details_ctrl,
    get_user_education_details_ctrl, send_pending_reg_emails_link_ctrl,
)
from ..users.users_models import Users, EducationDetails
from .utils import fetch, exception, admin_api

user_api = Blueprint("user_api", __name__)


@user_api.route("/user", methods=["POST"])
def create_user():
    req_data = request.json
    user_email = req_data["email"]
    existing_user = fetch(Users, {"email": user_email})
    if existing_user is None:
        create_user_ctrl(req_data)
        return jsonify({"success": True})
    else:
        if not existing_user["is_active"]:
            return jsonify({"Success": False, "error": "inactive_user_exists"})
        return jsonify({"Success": False, "error": "user_already_exists"})


@user_api.route("/user", methods=["GET"])
def get_user_list():
    return jsonify(get_user_list_ctrl())


@user_api.route("/user/<country>", methods=["GET"])
def get_user_list_country(country):
    return jsonify(get_user_list_ctr_country(country))


@user_api.route("/user_gender/<gender>", methods=["GET"])
def get_user_list_gender(gender):
    return jsonify(get_user_list_ctr_gender(gender))


@user_api.route("/user_first-name/<first_name>", methods=["GET"])
def get_user_list_first_name(first_name):
    return jsonify(get_user_list_ctr_first_name(first_name))


@user_api.route("/update/<email>/<first_name>", methods=["GET"])
def get_user_list_update_first_name(email, first_name):
    return jsonify(get_user_list_ctr_update_first_name(email, first_name))


@user_api.route("/sort/<first_name>", methods=["GET"])
def get_user_list_sort(first_name):
    return jsonify(get_user_list_ctrl_sort(first_name))


@user_api.route("/params", methods=["GET"])
def param():
    sort_by = request.args.get("sort_by")
    sort_order = request.args.get("sort_order")
    return jsonify(get_user_list_ctrl_sort_by_order(sort_by, sort_order))


@user_api.route("/education_details", methods=["POST"])
def user_education_details():
    req_data = request.json
    return jsonify(user_education_details_ctrl(req_data))


@user_api.route("/education_details", methods=["GET"])
def get_user_education_details():
    return jsonify(get_user_education_details_ctrl())


@user_api.route("/user/self", methods=["GET"])
def get_user_self():
    return jsonify(get_user_self_ctrl())

@user_api.route("/user/send-pending-reg-emails",methods=["POST"])
@exception
@admin_api
def send_pending_reg_emails():
    return jsonify(send_pending_reg_emails_link_ctrl())

