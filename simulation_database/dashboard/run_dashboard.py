from __future__ import print_function
#from flask_migrate import Migrate
from os import environ
from sys import exit

from config import config_dict
from app import create_app, db

get_config_mode = environ.get('SIMDB_CONFIG_MODE', 'Debug')

try:
    config_mode = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid SIMDB_CONFIG_MODE environment variable entry.')

app = create_app(config_mode)


#Migrate(app, db)

if __name__ == '__main__':

    # empty log
    with open("error.log", "w") as log:
        log.write("")

    # Start app
    app.run(debug=True)