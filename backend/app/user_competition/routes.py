from flask import Blueprint, jsonify, request


from .controller import (competition_registrations_ctrl, create_competition_ctrl, get_all_competitions_ctrl,
                         update_competition_ctrl, competition_bots_registrations_ctrl,
                         send_email_to_registered_users_ctrl, competition_completion_email_to_registered_users_ctrl)
from ..utils import admin_api, exception
from ..extensions import g


competition_api = Blueprint("competition_api", __name__)


@competition_api.route('/competition', methods=['POST'])
@exception
@admin_api
def create_competition():
    image_url = request.files['competition_image']
    name = request.form["name"] if "name" in request.form else None
    description = request.form["description"] if "description" in request.form else None
    short_description = request.form["short_description"] if "short_description" in request.form else None
    start_date = request.form["start_date"] if "start_date" in request.form else None
    end_date = request.form["end_date"] if "end_date" in request.form else None
    reg_start_date = request.form["reg_start_date"] if "reg_start_date" in request.form else None
    reg_end_date = request.form["reg_end_date"] if "reg_end_date" in request.form else None
    category_list = request.form["category_list"] if "category_list" in request.form else None
    rules = request.form["rules"] if "rules" in request.form else None
    rewards = request.form["rewards"] if "rewards" in request.form else None
    additional_notes = request.form["additional_notes"] if "additional_notes" in request.form else None
    create_competition_ctrl({
        "name": name,
        "description": description,
        "short_description": short_description,
        "start_date": start_date,
        "end_date": end_date,
        "reg_start_date": reg_start_date,
        "reg_end_date": reg_end_date,
        "category_list": category_list,
        "rules": rules,
        "rewards": rewards,
        "additional_notes": additional_notes,
    }, image_url)
    return jsonify({"success": True})


@competition_api.route('/competition/<competition_id>', methods=['PUT'])
@exception
@admin_api
def update_competition(competition_id):
    image_url = request.files['competition_image']
    name = request.form["name"] if "name" in request.form else None
    description = request.form["description"] if "description" in request.form else None
    short_description = request.form["short_description"] if "short_description" in request.form else None
    start_date = request.form["start_date"] if "start_date" in request.form else None
    end_date = request.form["end_date"] if "end_date" in request.form else None
    reg_start_date = request.form["reg_start_date"] if "reg_start_date" in request.form else None
    reg_end_date = request.form["reg_end_date"] if "reg_end_date" in request.form else None
    category_list = request.form["category_list"] if "category_list" in request.form else None
    rules = request.form["rules"] if "rules" in request.form else None
    rewards = request.form["rewards"] if "rewards" in request.form else None
    additional_notes = request.form["additional_notes"] if "additional_notes" in request.form else None
    obj = {
        "name": name,
        "description": description,
        "short_description": short_description,
        "start_date": start_date,
        "end_date": end_date,
        "reg_start_date": reg_start_date,
        "reg_end_date": reg_end_date,
        "category_list": category_list,
        "rules": rules,
        "rewards": rewards,
        "additional_notes": additional_notes,
    }
    return jsonify(update_competition_ctrl(obj, image_url, competition_id))


@competition_api.route('/competition', methods=['GET'])
@exception
def get_all_competitions():
    return jsonify(get_all_competitions_ctrl())


@competition_api.route('/competition/<competition_id>', methods=['GET'])
@exception
def get_competition_by_id(competition_id):
    return jsonify(get_all_competitions_ctrl(competition_id=competition_id))


@competition_api.route('/competition/<competition_id>/register', methods=['POST'])
@exception
def competition_registrations(competition_id):
    user_id = g.user.id
    competition_registrations_ctrl(competition_id, user_id)
    return jsonify({"success": True})


@competition_api.route('/competition/bots_register', methods=['GET'])
@exception
def competition_bots_registrations():
    competition_bots_registrations_ctrl()
    return jsonify({"success": True})


@competition_api.route('/competition/send_email', methods=['GET'])
@exception
@admin_api
def send_email_to_registered_users():
    send_email_to_registered_users_ctrl()
    return jsonify({"success": True})

@competition_api.route('/competition/completion_email', methods=['GET'])
@exception
@admin_api
def competition_completion_email_to_registered_users():
    competition_completion_email_to_registered_users_ctrl()
    return jsonify({"success": True})


