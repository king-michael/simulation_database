from flask import Blueprint

blueprint = Blueprint(
    'viewer_blueprint',
    __name__,
    url_prefix='/viewer',
    template_folder='templates',
    static_folder='static'
)
