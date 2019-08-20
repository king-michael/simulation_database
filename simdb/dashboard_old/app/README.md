# Dashboard Flask Application Module


## Structure

### Blueprints
Each blueprint extends the app. To create a new blueprint make a copy of 
`blueprint_template`. Modify `__init__.py`, `routes.py` and `templates/TEMPLATE_index.html`
accordingly. Search for `TEMPLATE` to find all relevant definitions. Finally, add the 
new blueprint to flask app by adding the directory name to `register_blueprints()` 
in `app/__init__.py`.

Directory     | Blueprint Name          | url_prefix     | prefix for templates and defs
------------- | ----------------------- | -------------- | -----------------
base          | base_blueprint          | /              | 
preferences   | preferences_blueprint   | /preferences   | `preferences_`
viewer        | viewer_blueprint        | /viewer        | `viewer_`
statistics    | statistics_blueprint    | /statistics    | `statistics_`
manage_groups | manage_groups_blueprint | /manage_groups | `manage_groups_`

Some important rules to keep in mind:
 - Each filename of HTML templates in `blueprint/templates/` has to be unique
 - Each definition in routes has to be unique

#### Base
This blueprint is to manage application wide functionality. JS/CSS extension are stored 
in `static`.

#### Preferences
Display and manage application preferences.
 - manage simulation databases
 - ... 

#### Viewer
View entries of selected database.

#### Statistics
View statistics for selected database

#### Manage Groups
View and manage entry groups and group keywords.