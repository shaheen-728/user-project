from app.extensions import db
from sqlalchemy.orm import relationship, backref


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.GUID(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))
    parent_tag_id = db.Column(db.GUID())
    s3_url = db.Column(db.String(255))
    accepted_question_credits = db.Column(db.Integer, server_default='10')
    category_unlock_credits = db.Column(db.Integer, server_default='-50')
    modified_on = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)


class TagDomain(db.Model):
    __tablename__ = 'tag_domain'
    id = db.Column(db.GUID(), primary_key=True)
    domain_id = db.Column(db.GUID(), db.ForeignKey('domain.id'))
    tag_id = db.Column(db.GUID(), db.ForeignKey('tag.id'))


class Domain(db.Model):
    __tablename__ = 'domain'
    id = db.Column(db.GUID(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))
    modified_on = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
