from app.extensions import db
from sqlalchemy.dialects import postgresql


class Users(db.Model):
    # Create migration with following query - alter table users alter column user_type TYPE  varchar(60);
    __tablename__ = "users"
    id = db.Column(db.GUID(), primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    country = db.Column(db.String(255))
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(120), unique=True)
    picture = db.Column(db.String(255))
    password = db.Column(db.String(256))
    dob = db.Column(db.DateTime)
    about = db.Column(db.String(255))
    modified_on = db.Column(db.DateTime)
    user_type = db.Column(db.String(60))
    created_at = db.Column(db.DateTime)
    one_time_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean)
    credits = db.Column(db.Integer)
    referral_hash = db.Column(db.String(256))
    level = db.Column(db.Integer())


class UserFollowing(db.Model):
    __tablename__ = "user_following"
    id = db.Column(db.GUID(), db.ForeignKey("users.id"), primary_key=True)
    followed_users = db.Column(postgresql.ARRAY(db.String()))
    following_users = db.Column(postgresql.ARRAY(db.String()))


class UserForgotPasswordHash(db.Model):
    __tablename__ = "user_forgot_password_hash"
    id = db.Column(db.GUID(), primary_key=True)
    user = db.Column(db.GUID(), db.ForeignKey("users.id"))
    one_time_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime)


class UserReferrals(db.Model):
    __tablename__ = "user_referrals"
    id = db.Column(db.GUID(), primary_key=True)
    referred_by = db.Column(db.GUID())
    referred_to = db.Column(db.GUID())
    is_active_on_platform = db.Column(db.Boolean, default=False)
    credits = db.Column(db.Integer, server_default="25")
    created_at = db.Column(db.DateTime)
    modified_on = db.Column(db.DateTime)


class EmailReferrals(db.Model):
    __tablename__ = "email_referrals"
    id = db.Column(db.GUID(), primary_key=True)
    referred_by = db.Column(db.GUID())
    referred_user_email = db.Column(db.String())
    referred_user_firstname = db.Column(db.String())
    referred_user_lastname = db.Column(db.String())
    email_sent_timestamp = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
    modified_on = db.Column(db.DateTime)


class EducationDetails(db.Model):
    __tablename__ = "education_details"
    id = db.Column(db.GUID(), primary_key=True)
    user_id = db.Column(db.GUID(), db.ForeignKey("users.id"))
    percentage_of_10th = db.Column(db.Float())
    year_of_passing_10th = db.Column(db.Date)
    school_name_of_10th = db.Column(db.String())
    percentage_of_12th = db.Column(db.Float())
    year_of_passing_12th = db.Column(db.Date)
    school_name_of_12th = db.Column(db.String())
    percentage_of_graduation = db.Column(db.Float())
    completion_of_graduation = db.Column(db.Date)
    college_name = db.Column(db.String())


class EmailSettings(db.Model):
        __tablename__ = 'email_settings'
        id = db.Column(db.GUID(), primary_key=True)
        first_name = db.Column(db.String(255))
        last_name = db.Column(db.String(255))
        user_id = db.Column(db.GUID(), db.ForeignKey('users.id'))
        email = db.Column(db.String(120), unique=True)
        unsubscribe = db.Column(db.Boolean, default=False)
        sent_email_templates = db.Column(postgresql.ARRAY(db.String(255)))
        created_at = db.Column(db.DateTime)
        modified_on = db.Column(db.DateTime)


class BotMetaDetails(db.Model):
        __tablename__ = 'bot_meta_details'
        id = db.Column(db.GUID(), primary_key=True)
        user_id = db.Column(db.GUID(), db.ForeignKey('users.id'))
        selected_categories = db.Column(postgresql.ARRAY(db.GUID()))
        accuracy = db.Column(db.Float())


