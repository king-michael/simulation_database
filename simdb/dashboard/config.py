from os import environ


class Config(object):
    SECRET_KEY = 'key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dashboard.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # THEME SUPPORT
    #  if set then url_for('static', filename='', theme='')
    #  will add the theme name to the static URL:
    #    /static/<DEFAULT_THEME>/filename
    # DEFAULT_THEME = "themes/dark"
    DEFAULT_THEME = None

    SELECTED_DATABASE = {"id": None,
                         "name": None,
                         "path": None,
                         "comment": None}


class ProductionConfig(Config):
    DEBUG = False

    # AB: We can use this if we want to use a real DB server
    # PostgreSQL database
    # SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
    #     environ.get('GENTELELLA_DATABASE_USER', 'gentelella'),
    #     environ.get('GENTELELLA_DATABASE_PASSWORD', 'gentelella'),
    #     environ.get('GENTELELLA_DATABASE_HOST', 'db'),
    #     environ.get('GENTELELLA_DATABASE_PORT', 5432),
    #     environ.get('GENTELELLA_DATABASE_NAME', 'gentelella')
    # )


class DebugConfig(Config):
    DEBUG = True


config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
