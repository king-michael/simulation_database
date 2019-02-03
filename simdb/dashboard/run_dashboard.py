from flask_migrate import Migrate
from os import environ
from sys import exit

from config import config_dict
from app import create_app, db

get_config_mode = environ.get('GENTELELLA_CONFIG_MODE', 'Debug')

try:
    config_mode = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid GENTELELLA_CONFIG_MODE environment variable entry.')

app = create_app(config_mode)

app.config["selected_database"] = { "id"   : None,
                                    "name" : None,
                                    "path" : None,
                                    "comment" : None}

Migrate(app, db)

if __name__ == '__main__':

    # empty log

    # Start app
    app.run(debug=True)