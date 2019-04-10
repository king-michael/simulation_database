from flask import Blueprint

blueprint = Blueprint(
    'preferences_blueprint',
    __name__,
    url_prefix='/preferences',
    template_folder='templates',
    static_folder='static'
)
