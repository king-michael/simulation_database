from flask import Blueprint

blueprint = Blueprint(
    'statistics_blueprint',
    __name__,
    url_prefix='/statistics',
    template_folder='templates',
    static_folder='static'
)
