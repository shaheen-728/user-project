from __future__ import absolute_import
import redis
import logging
from flask import Flask, g
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm
from app.sqlalchemy_utils import GUID
from flask_marshmallow import Marshmallow
from flask_caching import Cache


Base = declarative_base()

app = Flask(__name__)

app.config.from_envvar("CONFIG")

# if not app.config["DEVELOPMENT"]:
#     from elasticapm.contrib.flask import ElasticAPM
#     app.config['ELASTIC_APM'] = {
#         "SERVER_URL": "http://apm-server:8200",
#         "SERVICE_NAME": "abekus"
#     }
#     apm = ElasticAPM(app)

CORS(app)
r = redis.StrictRedis(host=app.config["REDIS_HOST"], port=6379, db=0)
app.config.update(
    CELERY_BROKER_URL=f"{app.config['REDIS_URI']}/0",
    CELERY_RESULT_BACKEND=f"{app.config['REDIS_URI']}/0",
    CACHE_TYPE="redis",
    CACHE_DEFAULT_TIMEOUT=300,
    CACHE_REDIS_HOST=app.config["REDIS_HOST"]
)


cache = Cache(app)
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"],
                       pool_size=30, max_overflow=0)


def get_new_session():
    DBSession = orm.scoped_session(orm.sessionmaker(bind=engine))
    session = DBSession()
    return session


db = SQLAlchemy(app)
db.GUID = GUID
migrate = Migrate(app, db)

ma = Marshmallow(app)