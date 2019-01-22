from __future__ import print_function, nested_scopes, generators, absolute_import, unicode_literals

import sys, os
sys.path.append("..")
from flask import render_template, request, redirect, flash, url_for, abort
from simdb.databaseModel import *
from simdb.viewer.databaseViewer import app
from simdb.viewer.app import db
from simdb.viewer.app.databaseModelApp import DBPath
from sqlalchemy.orm.exc import NoResultFound
import simdb.databaseAPI as api
import pandas as pd
import json
import itertools

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
    used_columns = ["entry_id", "path", "created_on", "added_on", "updated_on", "description"]

    # interaction with filterTable() js function
    db_path = request.args['db_path'] # get the path to selected data base
    search_query = request.args['search_query'] # get the search query from search field

    selected_group = request.args['selected_group']
    selected_keyword = request.args['selected_keyword']
    selected_keyword_value = request.args['selected_keyword_value']

    sort_ascending = request.args['sort_ascending']
    sort_descending = request.args['sort_descending']

    selected_columns = ["entry_id"] + request.args['selected_columns'].split()

    # some checks on selected path
    if db_path == "":
        return "<p style='align=center'>No database selected</p>"
    if not os.path.exists(db_path):
        return "<p style='align=center'>Path to database not found</p>"

    # handle selected groups and keywords
    # hotfix until tags get multiselectable
    if selected_group == "" or selected_group == "none":
        selected_group = None
    else:
        selected_group = [selected_group]

    if selected_keyword == "" or selected_keyword == "none":
        selected_keyword = None
    else:
        selected_keyword = [selected_keyword]

    if selected_keyword_value == "" or selected_keyword_value == "none":
        apply_filter = None
    else:
        apply_filter = Main.keywords.any(name=selected_keyword[0], value=selected_keyword_value) # value=selected_keyword_value[0]
        selected_keyword = None

    # handle sort by
    if not sort_ascending and not sort_descending:
        # default values
        order_by = "id"
        order = "ascending"
    elif not sort_ascending:
        order_by = sort_descending[8:]
        order = "descending"
    elif not sort_descending:
        order_by = sort_ascending[8:]
        order = "ascending"
    else:
        # something went wrong, go to default
        order_by = "id"
        order = "ascending"

    # load table
    db_id = db.session.query(DBPath).filter(DBPath.path == db_path).one().id  # need this only while working with paths
    session = api.connect_database(db_path=db_path)
    table = api.get_entry_table(session, group_names=selected_group, keyword_names=selected_keyword, columns=used_columns, apply_filter=apply_filter, order_by=order_by, order=order)

    # stop if table is empty
    if table.shape[0] == 0:
        return "<p style='align=center'>No entries found</p>"


    # filter by search query
    # export this to utils
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
            if len(table) == 0:
                return table.to_html(classes=str("table sortable"), escape=False, index=False) # convert to HTML

    # stop if table is empty
    if table.shape[0] == 0:
        return "<p style='align=center'>No entries found</p>"

    # convert table to proper HTML
    pd.set_option('display.max_colwidth', -1) # let pandas print the full entry to HTML table

    # Order is important ! dont switch table["path"] and table["entry_id"]
    link_template = '<a href="details/{db_id}/{entry_id}/">{link_name}</a>'
    table["path"] = table.apply(
       lambda row: link_template.format(entry_id=str(row.entry_id), db_id=db_id, link_name=row.path), axis=1)
    table["entry_id"] = table["entry_id"].apply(
        lambda entry_id: link_template.format(entry_id=entry_id, db_id=db_id, link_name=entry_id))
    #table["path"] = table["path"].apply(lambda x: '<a href="{0}" target="blank">{0}</a>'.format(x), )
    # convert dates
    table["updated_on"] = table["updated_on"].apply(lambda x: x.strftime('%Y/%m/%d'))
    table["added_on"] = table["added_on"].apply(lambda x: x.strftime('%Y/%m/%d'))
    table["created_on"] = table["created_on"].apply(lambda x: x.strftime('%Y/%m/%d') if x is not None else "--")

    table = table[selected_columns]

    # add buttons for sorting to columns
    button_template = '{column_name} <input id="sort_by_{column_name}" type="button" class="sort_button {sort_class}" onClick="sortTable(\'{column_name}\');filterTable()" />'

    html_columns = []
    for c in table.columns:
        sort_class = "sort_" + order if c == order_by else ""
        html_columns.append(button_template.format(column_name=c, sort_class=sort_class))
    table.columns = html_columns

    results = table.to_html(classes=str("table sortable"), escape=False, index=False) # convert to HTML

    return results

# this page is only there to gather information for the filter
@app.route('/view/build_filter/')
def build_filter():

    # interaction with buildFilter() js function
    db_path = request.args['db_path']  # get the path to selected data base
    search_query = request.args['search_query']  # get the search query from search field

    # this data is send as coma separated list
    selected_groups = request.args['selected_group'].split(",")
    selected_keywords = request.args['selected_keyword'].split(",")
    selected_keyword_value = request.args['selected_keyword_value'].split(",")

    session = api.connect_database(db_path=db_path)

    # get all groups in database
    groups = api.get_all_groups(session=session)
    groups = [g[0] for g in groups]
    print("---",groups)

    # count number of entries for each group
    groups_count = []
    query = session.query(Main.entry_id).join(association_main_groups).join(Groups)
    for g in groups:
        c = query.filter(Groups.name == g).count()
        groups_count.append(str(c))

    # get keywords to display
    # only show keywords which are present in selected group
    if selected_groups == [""]:
        keywords = api.get_all_keywords(session=session)
    else:
        query = session.query(Keywords.name, Keywords.value)\
                       .join(Main).join(association_main_groups).join(Groups)\
                       .filter(Groups.name.in_(selected_groups)).distinct()
        keywords = dict((k, list(zip(*v))[1]) for k, v in itertools.groupby(query.all(), lambda x: x[0]))

    # count number of entries for each keyword
    keywords_count = []
    query = session.query(Main.entry_id).join(association_main_groups).join(Groups).join(Keywords)
    if selected_groups == [""]:
        for k in keywords.keys():
            c = query.filter(Keywords.name == k).count()
            keywords_count.append(str(c))
    else:
        for k in keywords.keys():
            c = query.filter(Groups.name.in_(selected_groups), Keywords.name == k).count()
            keywords_count.append(str(c))

    if len(selected_keywords) > 1:
        # more than one keyword selected
        values = []
    else:
        if selected_keywords == [""]:
            # no keyword selected
            values = []
        else:
            # one keyword selected
            values = keywords[selected_keywords[0]]

    print(keywords.keys())
    print(keywords_count)
    out = {'groups'   : groups,
           'groupscount' : groups_count,
           'keywords' : keywords.keys(),
           'keywordscount' : keywords_count,
           'values'   : values}

    return json.dumps(out)

# details page for each entry in DB
@app.route('/view/details/<db_id>/<entry_id>/', methods=['POST', 'GET'])
def detail(db_id, entry_id):

    # get the path to selected DB
    path = db.session.query(DBPath).filter(DBPath.id == db_id).one().path
    session = api.connect_database(db_path=path)
    # render template
    return render_template(
        'details.html',
        sim = api.get_entry_details(session=session, entry_id=entry_id),
        meta = api.get_meta_groups(session, entry_id, as_list=True),
        keywords = api.get_keywords(session=session, entry_id=entry_id),
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