import os

from app import app, db
# from app.obj import FileHandler
# from app.admin import admin

# Flask views
# @app.route('/')
# def index():
#     return '<a href="/admin/">Click me to get to Admin!</a>'
from views import *

if __name__ == '__main__':

    # Create DB
    db.create_all()

    # Files
    #fh = FileHandler(os.path.dirname(__file__))
    #fh.connect(db)

    # Start app
    app.run(debug=True)
