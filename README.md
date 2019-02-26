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
cd simulation_database/simdb/dashboard

python run_dashboard.py
```

open `127.0.0.0:5000` in browser

## Development
### simDB (simdb/):

File | Note 
--- | --- 
databaseModel.py | Classes for DB model.
databaseAPI.py | Functions and classes for interactions with DB.

### simDB Dashboard (simdb/dashboard/):

File | Note
--- | ---
run_dashboard.py | Main file to run dashboard.
app/base/  | Main blueprint
app/base/models.py | Classes for an additional DB which is used to run the application.
