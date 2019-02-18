from flask import jsonify, render_template, redirect, request, url_for

from app import db
from app.base import blueprint
# from app.base.forms import LoginForm, CreateAccountForm
# from app.base.models import User


@blueprint.route('/')
def route_default():
    return redirect(url_for('viewer_blueprint.viewer_index'))



# @blueprint.route('/<template>')
# def route_template(template):
#     return render_template(template + '.html')
#
#
# @blueprint.route('/fixed_<template>')
# def route_fixed_template(template):
#     return render_template('fixed/fixed_{}.html'.format(template))
#
#
# @blueprint.route('/page_<error>')
# def route_errors(error):
#     return render_template('errors/page_{}.html'.format(error))
#
#
# @blueprint.route('/shutdown')
# def shutdown():
#     func = request.environ.get('werkzeug.server.shutdown')
#     if func is None:
#         raise RuntimeError('Not running with the Werkzeug Server')
#     func()
#     return 'Server shutting down...'

## Errors
## AB: it is not possible to define this on blueprint level in python2
## SOLUTION: static + routes.py on top app level
# @blueprint.errorhandler(403)
# def access_forbidden(error):
#     return render_template('errors/page_403.html'), 403
#
#
# @blueprint.errorhandler(404)
# def not_found_error(error):
#     return render_template('errors/page_404.html'), 404
#
#
# @blueprint.errorhandler(500)
# def internal_error(error):
#     return render_template('errors/page_500.html'), 500
