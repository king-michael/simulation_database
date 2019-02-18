from flask import Blueprint

blueprint = Blueprint(
    'manage_groups_blueprint',
    __name__,
    url_prefix='/manage_groups',
    template_folder='templates',
    static_folder='static'
)