from app.viewer import blueprint
from flask import render_template, current_app, request
# import simdb.databaseAPI as api


@blueprint.route('/')
def TEMPLATE_index():
    return render_template('TEMPLATE_index.html')

