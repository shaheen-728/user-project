import os
import random
from datetime import datetime
from random import randrange

import boto3
from config.constants import aws_access_key_id, aws_secret_access_key
from sqlalchemy import and_
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename

from ..competition.models import Competition, CompetitionRegistrations
from ..exc import ControllerError
from ..extensions import g
from ..mail.controller import send_email_new
from ..tag.models import Tag
from ..users.users_models import Users,BotMetaDetails
from ..utils import create, fetch, serialize_to_json, update

dir_path = os.path.dirname(os.path.realpath(__file__))


def create_competition_ctrl(obj, image_url):
    competition_name = obj['name']
    for attribute in ["category_list", "start_date", "end_date", "name"]:
        assert attribute in obj, f"{attribute}_required"
    obj["category_list"] = obj["category_list"].split(",")
    assert len(obj["category_list"]) == g.session.query(Tag).filter(
        Tag.id.in_(obj["category_list"])).count(), "category_mismatch"
    if image_url:
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        s3 = session.resource('s3')
        filename = secure_filename(image_url.filename)
        filepath = os.path.join(dir_path, filename)
        image_url.save(filepath)
        bucket_key = competition_name + "_" + filename
        s3.meta.client.upload_file(Filename=filepath, Bucket='wikasta.projectq',
                                   Key=bucket_key)
        os.remove(filepath)
        obj["image_url"] = "https://s3-us-west-2.amazonaws.com/wikasta.projectq/" + bucket_key
    competition = Competition(**obj)
    create(competition)


def update_competition_ctrl(obj, image_url, competition_id):
    obj["id"] = competition_id
    if "category_list" in obj:
        obj["category_list"] = obj["category_list"].split(",")
    assert len(obj["category_list"]) == g.session.query(Tag).filter(
        Tag.id.in_(obj["category_list"])).count(), "category_mismatch"
    existing_competition = g.session.query(Competition).filter(Competition.id == competition_id).first()
    if not existing_competition:
        raise ControllerError("no_such_competition")
    if image_url:
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        s3 = session.resource('s3')
        filename = secure_filename(image_url.filename)
        filepath = os.path.join(dir_path, filename)
        image_url.save(filepath)
        bucket_key = existing_competition.name + "_" + filename
        s3.meta.client.upload_file(Filename=filepath, Bucket='wikasta.projectq',
                                   Key=bucket_key)
        os.remove(filepath)
        obj["image_url"] = "https://s3-us-west-2.amazonaws.com/wikasta.projectq/" + bucket_key
    competition = Competition(**obj)
    update(competition)
    return serialize_to_json(existing_competition)


def get_all_competitions_ctrl(competition_id=None):
    user_id = None
    if hasattr(g, "user"):
        user_id = g.user.id
    all_competitions = g.session.query(Competition).order_by(Competition.start_date.desc())
    if competition_id:
        all_competitions = all_competitions.filter(Competition.id == competition_id)
    all_competitions = all_competitions.all()
    all_competition_ids = []
    all_category_ids = set()
    for competition in all_competitions:
        all_competition_ids.append(str(competition.id))
        if competition.category_list:
            all_category_ids.update(competition.category_list)
    all_categories = g.session.query(Tag.id, Tag.name).filter(Tag.id.in_(all_category_ids)).all()
    all_category_by_id = {str(tag_id): name for tag_id, name in all_categories}
    competition_registration_counts = g.session.query(CompetitionRegistrations.competition_id,
                                                      func.count(CompetitionRegistrations.id)).filter(
        CompetitionRegistrations.competition_id.in_(all_competition_ids)).group_by(
        CompetitionRegistrations.competition_id).all()
    competition_wise_reg_counts = {str(c_id): reg_count for c_id, reg_count in competition_registration_counts}
    serialized_competitions = []
    if user_id:
        user_registered_competitions = g.session.query(CompetitionRegistrations.competition_id).filter(
            CompetitionRegistrations.user_id == user_id).filter(
            CompetitionRegistrations.competition_id.in_(all_competition_ids)).all()
        registered_competition_list = [str(ele[0]) for ele in user_registered_competitions]
    for competition in all_competitions:
        competition_dict = serialize_to_json(competition)
        competition_dict["total_registrations"] = 0
        if competition_dict["id"] in competition_wise_reg_counts:
            competition_dict["total_registrations"] = competition_wise_reg_counts[competition_dict["id"]]
        competition_dict["category_names"] = []
        if competition_dict["category_list"]:
            for category_id in competition_dict["category_list"]:
                if category_id in all_category_by_id:
                    competition_dict["category_names"].append(all_category_by_id[category_id])
        competition_dict.pop("category_list")
        competition_dict["is_registered"] = False
        if user_id:
            if competition_dict["id"] in registered_competition_list:
                competition_dict["is_registered"] = True
        serialized_competitions.append(competition_dict)
    return {"success": True, "data": serialized_competitions}


def competition_registrations_ctrl(competition_id, user_id):
    competition = g.session.query(Competition).filter(Competition.id == competition_id).first()
    if not competition_id:
        raise ControllerError("competition_not_found")
    if competition.reg_end_date and competition.reg_end_date < datetime.now():
        raise ControllerError("registration_closed")
    existing_registration = g.session.query(CompetitionRegistrations).filter(
        CompetitionRegistrations.competition_id == competition_id).filter(
        CompetitionRegistrations.user_id == user_id).first()
    if existing_registration:
        raise ControllerError("already_registered")
    obj = {"user_id": user_id, "competition_id": competition_id}
    competitionregistrations = CompetitionRegistrations(**obj)
    create(competitionregistrations)


def get_all_users_by_competition_id_ctrl(competition_id):
    competition_data = fetch(CompetitionRegistrations, {"competition_id": competition_id})
    all_users_ids = g.session.query(CompetitionRegistrations.user_id).filter(
        CompetitionRegistrations.competition_id == competition_id).all()
    all_users_ids = [str(x[0]) for x in all_users_ids]
    all_users = g.session.query(Users).filter(Users.id.in_(all_users_ids)).all()
    user_list = []
    for user in all_users:
        user_list.append(user.first_name + " " + user.last_name)
    return {"user_list": user_list, "competition_data": competition_data}


def send_email_to_registered_users_ctrl():
    all_competition = g.session.query(Competition).filter(and_(
        Competition.start_date < datetime.now(), Competition.end_date >= datetime.now(),
        Competition.competition_starts_email_sent == False)).all()
    for competition in all_competition:
        subject = f'Abekus Competition | {competition.name} | is now Live!'
        all_users = g.session.query(Users).join(CompetitionRegistrations).filter(
            CompetitionRegistrations.competition_id == competition.id).all()
        for user in all_users:
            send_email_new(user.email, subject,
                           'join_competition.html', {"first_name": user.first_name,
                                                     "competition_name": competition.name, "heading": subject,
                                                     "start_datetime": competition.start_date.strftime(
                                                         "%d-%b-%Y %H:%M"),
                                                     "end_datetime": competition.end_date.strftime("%d-%b-%Y %H:%M"),
                                                     "description": competition.description
                                                     })
        competition.competition_starts_email_sent = True
    g.session.commit()


def competition_bots_registrations_ctrl():
    new_competitions = g.session.query(Competition).filter(
        Competition.created_at >= (datetime.today())).all()
    for new_competition in new_competitions:
        all_bots = g.session.query(BotMetaDetails).filter(
            BotMetaDetails.selected_categories.overlap(new_competition.category_list)).all()
        no_of_bots = len(all_bots)
        random_bot_count = no_of_bots
        if random_bot_count > 15:
            random_bot_count = randrange(min(15, no_of_bots), min(25, no_of_bots + 1))
        randomly_selected_bots = random.sample(all_bots, random_bot_count)
        for bot in randomly_selected_bots:
            competition_registrations_ctrl(new_competition.id, bot.user_id)


def competition_completion_email_to_registered_users_ctrl():
   subject="Competition_Completion_Email"
   all_competitions=g.session.query(Competition).filter(Competition.end_date<datetime.today()).all()
   for competition in all_competitions:
      all_users = g.session.query(Users).join(CompetitionRegistrations).filter(
          CompetitionRegistrations.competition_id == competition.id).all()
      for user in all_users:
           print(user.first_name)
           send_email_new(user.email,subject,'competition_completion_email.html',
                          {"first_name":user.first_name,"competition_name":competition.name})
