from app.viewer import blueprint
from flask import render_template


@blueprint.route('/')
def viewer_index():
    return render_template('index_viewer.html')


# @blueprint.route('/<template>')
# def route_template(template):
#     return render_template(template + '.html')
