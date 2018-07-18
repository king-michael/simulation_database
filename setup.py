from setuptools import setup

setup(
    name='simulation_database',
    version='v0.1.0beta',
    packages=['simdb',
              'simdb.app',
              'simdb.utils',
              ],
    url='https://github.com/king-michael/simulation_database',
    license='', # ToDo: Choose a licence
    author=[
        'Michael King',
        'Andrej Berg'
    ],
    author_email=[
        'michael.king@uni-konstanz.de',
        'andrej.berg@uni-konstanz.de'
    ],
    description='', # ToDo: Description
    install_requires=[
        'SQLAlchemy',
        'flask',
        'Flask-SQLAlchemy',
        'pandas>=0.21',
        'numpy'
    ]
)
