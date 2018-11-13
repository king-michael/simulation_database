"""
# Details:
#   simdb/app is the main directory for the flask app
# Structure:
#   views.py  ::  definition of views/sites to display
#                 calls HTMLs from templates
#   config.py ::  main configuration file for flask
#   templates ::  HTML templates for output for browser
#                 layout.html  --  main template
#                 list.html    --  template for display the Main table
#                 details.html --  template for details view of an entry
#   static    ::  place where everything is stored to display the site properly
# Authors:
#   Andrej Berg
# History:
#   -
# Last modified: 12.07.2018
# ToDo:
#   -
# Bugs:
#   -
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.config import Config


# init Flask object and load configuration
app = Flask(__name__)
app.config.from_object(Config)

# init database
db = SQLAlchemy(app)
