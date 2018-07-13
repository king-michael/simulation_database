"""
# Details:
#   This script starts a Flask server to view
#   Simulation Data Bases
#   for more information see:
#       http://flask.pocoo.org/
#   Start by running:
#       python dataBaseViewer.py
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

__author__ = ["Andrej Berg"]
__date__ = "12.07.2018"

from app import app, db
from app.views import *

if __name__ == '__main__':
    # Create DB
    db.create_all()

    # Start app
    app.run(debug=True)
