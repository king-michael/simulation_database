import sys, os
sys.path.append("..")
from flask import render_template, request, redirect, flash,url_for
#from databaseModel import Main
from databaseViewer import app
from app import db
from app.databaseModelApp import DBPath
from databaseAPI import getEntryTable, getEntryDetails, getEntryKeywords, getEntryTags, getEntryMeta
import pandas as pd

# page where we can add DBs
# this will be moved to /view/ in a later step
@app.route('/', methods=['POST', 'GET'])
def index():

    # if a path and comment are provided
    # add this DB to list of selectable DBs
    # this has to be changed!
    try:
        path = request.form['path']
        comment = request.form['comment']
        db.session.add(DBPath(path=path, comment=comment))
        db.session.commit()
    except:
        pass

    # render the template
    return render_template(
        'index.html',
        databases=db.session.query(DBPath).all()
    )


# overview page which displays all entries in DB as a table/list
@app.route('/view/', methods=['POST', 'GET'])
def list_all():
    path = ""

    # check if a DB is selected
    try:
        path = request.form['path']
    except:
        pass

    # load table if a valid DB is selected
    if path != "" and os.path.exists(path):
        table = getEntryTable(path, columns=["entry_id", "path", "created_on", "added_on", "updated_on", "description"], load_keys=False, load_tags=False)
        db_id = db.session.query(DBPath).filter(DBPath.path == path).one().id
        table["entry_id"] = table["entry_id"].apply(lambda x: '<a href="/{1}/{0}/">{0}</a>'.format(x, db_id))
    else:
        table = pd.DataFrame()

    # let pandas print the full entry to HTML table
    pd.set_option('display.max_colwidth', -1)

    # render the template
    return render_template(
        'list.html',
        path=path,
        databases = db.session.query(DBPath).all(),
        table      = table.to_html(classes="table sortable", escape=False)
    )


# details page for each entry in DB
@app.route('/<db_id>/<entry_id>/', methods=['POST', 'GET'])
def detail(db_id, entry_id):

    # get the path to selected DB
    path = db.session.query(DBPath).filter(DBPath.id == db_id).one().path

    # render template
    return render_template(
        'details.html',
        sim = getEntryDetails(path, entry_id),
        meta = getEntryMeta(path, entry_id),
        keywords = getEntryKeywords(path, entry_id),
        tags = getEntryTags(path, entry_id)
    )
