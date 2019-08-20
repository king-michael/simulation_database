from app.base import blueprint
from flask import redirect, url_for


@blueprint.route('/')
def route_default():
    return redirect(url_for('viewer_blueprint.viewer_index'))


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
