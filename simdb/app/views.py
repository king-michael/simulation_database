import sys, os
sys.path.append("..")
from flask import render_template, request, redirect, flash,url_for
#from databaseModel import Main
from databaseViewer import app
from app import db
from app.databaseModelApp import DBPath
from databaseAPI import getEntryTable, getEntryDetails, getEntryKeywords, getEntryMeta
import pandas as pd

@app.route('/', methods=['POST', 'GET'])
def index():
    try:
        path = request.form['path']
        comment = request.form['comment']
        db.session.add(DBPath(path=path, comment=comment))
        db.session.commit()
    except:
        pass
    return render_template(
        'index.html',
        databases=db.session.query(DBPath).all()
    )



@app.route('/view/', methods=['POST', 'GET'])
def list_all():
    path = ""
    try:
        path = request.form['path']
    except:
        pass
    if path != "" and os.path.exists(path):
        table = getEntryTable(path, columns=["entry_id", "path", "created_on", "added_on", "updated_on", "description"], load_keys=False, load_tags=False)
        db_id = db.session.query(DBPath).filter(DBPath.path == path).one().id
        table["entry_id"] = table["entry_id"].apply(lambda x: '<a href="/{1}/{0}/">{0}</a>'.format(x, db_id))
    else:
        table = pd.DataFrame()
    return render_template(
        'list.html',
        path=path,
        databases = db.session.query(DBPath).all(),
        table      = table.to_html(classes="table sortable", escape=False)
    )


@app.route('/<db_id>/<entry_id>/', methods=['POST', 'GET'])
def detail(db_id, entry_id):
    path = db.session.query(DBPath).filter(DBPath.id == db_id).one().path
    return render_template(
        'details.html',
        sim = getEntryDetails(path, entry_id)
    )
