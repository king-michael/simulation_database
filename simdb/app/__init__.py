from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

from app.config import Config

print Config.SQLALCHEMY_DATABASE_URI


# init Flask object and load configuration
app = Flask(__name__)
app.config.from_object(Config)

# init database and migration tool
db = SQLAlchemy(app)
# migrate = Migrate(app, db)


# these import have to be here
# from app import routes
from databaseModel import Main
# DEV used to fill up the db after deletetion
# def add_defaults(db):
#     for w in ["spce", "tip3p"]:
#         q = db.session.query(WaterModels).filter(WaterModels.name == w)
#         if not db.session.query(q.exists()).scalar():
#             db.session.add(WaterModels(w))
#             db.session.commit()
#
#     for w in ["pdb2gmx", "martinize"]:
#         q = db.session.query(BuildTools).filter(BuildTools.name == w)
#         if not db.session.query(q.exists()).scalar():
#             db.session.add(BuildTools(w))
#             db.session.commit()
#
#     for m, ff, b, w in [("gromos54a7-isop", "gromos54a7-isop", "pdb2gmx", "spce")]:
#         q = db.session.query(Models).filter(Models.name == m)
#         if not db.session.query(q.exists()).scalar():
#             m = Models(m)
#             m.force_field = db.session.query(ForceFields).filter(ForceFields.name == ff).one()
#             m.build_with = db.session.query(BuildTools).filter(BuildTools.name == b).one()
#             m.water = db.session.query(WaterModels).filter(WaterModels.name == w).one()
#             db.session.add(m)
#             db.session.commit()

# add_defaults(db)