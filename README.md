# simulation_database

## Install
Clone the repository

```
git clone ...
```

Install
```
pip install -e . --user
```

## Run SimDB Viewer

```
cd simulation_database/simdb/viewer

python databaseViewer.py
```

open `127.0.0.0:5000` in browser

## Development
Important files:

File | Note 
--- | --- 
databaseViewer.py | Main file to start the flask application.
databaseModel.py | Classes for DB model.
databaseAPI.py | Functions and classes for interactions with DB.
app/\_\_init\_\_.py | Flask application is initialised here.
app/config.py | Configuration file for flask application.
app/views.py | All pages are added here. Each page renders a template from app/templates.
app/databaseModelApp.py | Classes for an additional DB which is used to run the application.
