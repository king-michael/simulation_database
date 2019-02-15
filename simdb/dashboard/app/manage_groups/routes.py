from app.manage_groups import blueprint
from app import db
from app.base.models import Database
from flask import render_template, request, flash, current_app
import simdb.databaseAPI as api

@blueprint.route('/')
def manage_groups_index():

    db_path = current_app.config['SELECTED_DATABASE']['path']
    session = api.connect_database(db_path=db_path)

    # get groups for display
    groups = api.get_all_groups(session, count=True)

    return render_template(
        'manage_groups_index.html',
        groups = groups
    )