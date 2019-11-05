class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '1234567890'
    SQLALCHEMY_ECHO = False
    FLASK_ADMIN_SWATCH = 'united'



if __name__ == '__main__':
    for key in Config.__dict__:
        print(key, Config.__dict__[key])