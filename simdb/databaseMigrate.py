"""
# Details:
#   Migration Tool
#   Usage:
#       python databaseMigrate.py db init
# Authors:
#   Andrej Berg
#   Michael King
# History:
#   -
# Last modified: 12.07.2018
# ToDo:
#   -
# Bugs:
#   -
"""

__author__ = ["Andrej Berg", "Michael King"]
__date__ = "17.04.2018"

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app.config import Config

# init Flask object and load configuration
app = Flask(__name__)
app.config.from_object(Config)



# init database and migration tool
db = SQLAlchemy(app)

# Import database models with app context
with app.app_context():
  from databaseModel import *

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()