from marshmallow_sqlalchemy import ModelSchema
from .models import Competition, CompetitionRegistrations


class CompetitionSchema(ModelSchema):
    class Meta:
        model = Competition


class CompetitionRegistrationsSchema(ModelSchema):
    class Meta:
        model = CompetitionRegistrations
