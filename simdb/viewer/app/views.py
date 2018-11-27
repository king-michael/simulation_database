import sys, os
sys.path.append("..")
from flask import render_template, request, redirect, flash, url_for, abort
#from databaseModel import Main
from databaseViewer import app
from app import db
from app.databaseModelApp import DBPath
from sqlalchemy.orm.exc import NoResultFound
from databaseAPI import *
import pandas as pd
import json

# page where we can add DBs
# this will be moved to /view/ in a later step
@app.route('/', methods=['POST', 'GET'])
def index():

    # if a path and comment are provided
    # add this DB to list of selectable DBs
    # I have no idea if this is a good way to do this
    try:
        path = request.form['path']
    except:
        path = False
    try:
        comment = request.form['comment']
    except:
        comment = False

    if path and comment:
        db.session.add(DBPath(path=path, comment=comment))
        db.session.commit()
        flash('Entry added successfully!')

    # render the template
    return render_template(
        'index.html',
        databases=db.session.query(DBPath).all()
    )


# overview page which displays all entries in DB as a table/list
@app.route('/view/', methods=['POST', 'GET'])
def list_all():

    # render the template
    return render_template(
        'view.html',
        databases = db.session.query(DBPath).all()
    )

# this page is only there to perform the search
@app.route('/view/filter/')
def filter_table():

    # options which one could change in GUI in the future
    search_case_sensitive = False

    # interaction with filterTable() js function
    db_path = request.args['db_path'] # get the path to selected data base
    search_query = request.args['search_query'] # get the search query from search field
    group = request.args['group']
    tag = request.args['tag']
    columns = request.args['columns'] # string of selected columns

    columns = ["entry_id"] + columns.split()

    # hotfix until tags get multiselectable
    if group == "" or group == "none":
        group = None
    else:
        group = [group]
    if tag == "" or tag == "none":
        tag = None
    else:
        tag = [tag]

    # load table if a valid DB is selected
    if db_path != "" and os.path.exists(db_path):
        db_id = db.session.query(DBPath).filter(DBPath.path == db_path).one().id  # need this only while working with paths
        table = get_entry_table(db_path, group_names=group, tags=tag, columns=["entry_id", "path", "created_on", "added_on", "updated_on", "description"])
    else:
        db_id = 0
        table = pd.DataFrame([], columns=["entry_id", "path", "created_on", "added_on", "updated_on", "description"])

    # filter by search query
    if search_query != "":

        # convert search query string to list of statements
        search_for = []
        statement = ''
        split = True  # split words if separated by whitespace

        for l in search_query.strip():

            if l == '"':
                # quote starts or ends
                split = not split

            elif l == ' ' and split:
                # statement ends, append to output
                search_for.append(statement)
                statement = ""

            else:
                # append letter to statement or whitespace if quote
                statement += l

        search_for.append(statement)

        for statement in search_for:
            if search_case_sensitive:
                mask = table['entry_id'].str.contains(statement) | table['description'].str.contains(statement)
            else:
                # (?!) in regex tells re to do a search without case sensitivity
                mask = table['entry_id'].str.contains('(?i)' + statement) | table['description'].str.contains('(?i)' + statement)
            table = table[mask]

    # convert table to proper HTML
    pd.set_option('display.max_colwidth', -1) # let pandas print the full entry to HTML table
    table["entry_id"] = table["entry_id"].apply(lambda x: '<a href="details/{1}/{0}/">{0}</a>'.format(x, db_id)) # convert entry ids to links for details view
    table["path"] = table["path"].apply(lambda x: '<a href="{0}" target="blank">{0}</a>'.format(x))

    # convert dates
    table["updated_on"] = table["updated_on"].apply(lambda x: x.strftime('%Y/%m/%d'))
    table["added_on"] = table["added_on"].apply(lambda x: x.strftime('%Y/%m/%d'))
    table["created_on"] = table["created_on"].apply(lambda x: x.strftime('%Y/%m/%d') if x is not None else "--")

    table = table[columns]
    results = table.to_html(classes="table sortable", escape=False) # convert to HTML

    return results

# this page is only there to gather information for the filter
@app.route('/view/build_filter/')
def build_filter():

    # interaction with buildFilter() js function
    db_path = request.args['db_path']

    out = {'groups' : get_groups(db_path),
           'tags'   : get_tags(db_path)}

    return json.dumps(out)

# details page for each entry in DB
@app.route('/view/details/<db_id>/<entry_id>/', methods=['POST', 'GET'])
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


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    """
    Delete the path to database that matches the specified
    id in the URL
    """
    try:
        e = db.session.query(DBPath).filter_by(id=id).one()
    except NoResultFound:
        abort(404)


    # delete the item from the database
    db.session.delete(e)
    db.session.commit()

    flash('Entry deleted successfully!')

    return redirect('/')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """
    Edit the path etc. to database that matches the specified
    id in the URL
    """

    # get the entry first
    try:
        e = db.session.query(DBPath).filter_by(id=id).one()
    except NoResultFound:
        abort(404)

    # try to get request
    try:
        path = request.form['path']
    except:
        path = False
    try:
        comment = request.form['comment']
    except:
        comment = False


    if path and comment:
        # request was submitted, edit entry
        e.path = path
        e.comment = comment
        db.session.commit()

        flash('Entry edited successfully!')

        return redirect('/')

    else:
        # no request, show form
        return render_template("edit_app_entry.html", db_entry=e)