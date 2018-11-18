from setuptools import setup

setup(
    name='simulation_database',
    version='v0.1.0beta',
    packages=['simdb',
              'simdb.app',
              'simdb.utils',
              ],
    url='https://github.com/king-michael/simulation_database',
    license='Apache License, Version 2.0, January 2004, http://www.apache.org/licenses/',
    author=[
        'Michael King',
        'Andrej Berg'
    ],
    author_email=[
        'michael.king@uni-konstanz.de',
        'andrej.berg@uni-konstanz.de'
    ],
    description='Python application based on SQL, Flask and PyQt to manage meta information about MD simulations.',
    install_requires=[
        'SQLAlchemy',
        'flask',
        'Flask-SQLAlchemy',
        'pandas>=0.21',
        'numpy'
    ]
)
