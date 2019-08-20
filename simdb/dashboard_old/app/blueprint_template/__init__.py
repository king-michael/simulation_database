from flask import Blueprint

blueprint = Blueprint(
    'TEMPLATE_blueprint',
    __name__,
    url_prefix='/TEMPLATE',
    template_folder='templates',
    static_folder='static'
)
