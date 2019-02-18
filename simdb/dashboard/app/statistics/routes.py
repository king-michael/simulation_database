from app.statistics import blueprint
from flask import render_template


@blueprint.route('/')
def statistics_index():
    return render_template('index_statistics.html')


# @blueprint.route('/<template>')
# def route_template(template):
#     return render_template(template + '.html')
