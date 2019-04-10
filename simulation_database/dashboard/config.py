from os import environ


class Config(object):
    """
    Base config object for flask application.
    """
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
    """
    Config object extension for production environment.
    """
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
    """
    Config object extension for development environment.
    """
    DEBUG = True

    SELECTED_DATABASE = {"id": 1,
                         "name": "Andrej real example",
                         "path": "../../examples/setup_databases/andrej/andrej_raw.db",
                         "comment": "This database contains all simulations performed during PhD 2016-2019"}


config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
