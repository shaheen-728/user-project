from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from .users_models  import Users, EducationDetails


class UsersSchema(ModelSchema):
    class Meta:
        model = Users
    password = fields.Str(load_only=True)
    one_time_hash = fields.Str(load_only=True)


class EducationDetailsSchema(ModelSchema):
    class Meta:
        model = EducationDetails
