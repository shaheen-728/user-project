from app.extensions import db
from sqlalchemy.dialects import postgresql


class Competition(db.Model):
    __tablename__ = 'competition'
    id = db.Column(db.GUID(), primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(1200))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    reg_start_date = db.Column(db.DateTime)
    category_list = db.Column(postgresql.ARRAY(db.GUID()))
    reg_end_date = db.Column(db.DateTime)
    image_url = db.Column(db.String(255))
    short_description = db.Column(db.String(300))
    rules = db.Column(db.String())
    rewards = db.Column(db.String())
    additional_notes = db.Column(db.String())
    created_at = db.Column(db.DateTime)
    modified_on = db.Column(db.DateTime)
    competition_starts_email_sent = db.Column(db.Boolean, default=False)


class CompetitionRegistrations(db.Model):
    __tablename__ = 'competition_registrations'
    id = db.Column(db.GUID(), primary_key=True)
    user_id = db.Column(db.GUID(), db.ForeignKey('users.id'))
    competition_id = db.Column(db.GUID(), db.ForeignKey('competition.id'))
    created_at = db.Column(db.DateTime)

