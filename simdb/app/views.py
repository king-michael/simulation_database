import sys, os
sys.path.append("..")
from flask import render_template, request, redirect, flash,url_for
#from databaseModel import Main
from databaseViewer import app
from app import db
from app.databaseModelApp import DBPath
from databaseAPI import getEntryTable
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
        table = getEntryTable(path)
        table["entry_id"] = table["entry_id"].apply(lambda x: '<a href="/{0}/">{0}</a>'.format(x))
    else:
        table = pd.DataFrame()
    return render_template(
        'list.html',
        path=path,
        databases = db.session.query(DBPath).all(),
        table      = table.to_html(classes="table sortable", escape=False)
    )

#
# @app.route('/<entry_id>/')
# def detail(entry_id):
#     return render_template(
#         'details.html',
#         sim = db.session.query(Main).filter(Main.entry_id == entry_id).one()
#     )
