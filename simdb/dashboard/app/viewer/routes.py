from app.viewer import blueprint
from flask import render_template, current_app, request
import simdb.databaseAPI as api
from simdb.databaseModel import *
import itertools, json, os
import pandas as pd

@blueprint.route('/')
def viewer_index():
    return render_template('viewer_index.html')


@blueprint.route('/build_filter')
def build_filter():

    out = {'groups': [],
           'group_counts': [],
           'keywords': [],
           'keyword_counts': [],
           'values': [],
           'value_counts': []}

    # get path to selected database
    db_path = current_app.config['SELECTED_DATABASE']['path']

    # this data is send as coma separated list
    selected_groups = request.args.get('selected_groups')
    selected_keywords = request.args.get('selected_keywords')

    # handle selected groups and keywords
    if selected_groups == "" or selected_groups == "none":
        selected_groups = None
    else:
        selected_groups = selected_groups.split(",")

    if selected_keywords == "" or selected_keywords == "none":
        selected_keywords = None
    else:
        selected_keywords = selected_keywords.split(",")


    session = api.connect_database(db_path=db_path)

    # get groups for display
    grp = api.get_all_groups(session, count=True)
    groups, counts = zip(*grp) if grp is not None else [[],[]]
    out['groups'], out['group_counts'] = [str(g) for g in groups], list(counts)

    # get keywords to display
    all_keywords = api.get_all_keywords(session, groups=selected_groups, count=True)
    out['keywords'], out['keyword_counts'] = zip(*all_keywords) if all_keywords else [[],[]]

    if selected_keywords:
        if len(selected_keywords) == 1 and selected_keywords != [""]:
            out['values'], out['value_counts'] = zip(*api.get_all_keyword_values(session, selected_keywords[0], groups=selected_groups, count=True))

    session.close()

    return json.dumps(out)

@blueprint.route('/filter/')
def filter_table():

    # options which one could change in GUI in the future
    show_columns = ["entry_id", "path", "created_on", "added_on", "updated_on", "description"]

    # load configuration
    db_id = current_app.config['SELECTED_DATABASE']['id']
    db_path = db_path = current_app.config['SELECTED_DATABASE']['path']

    # interaction with filterTable() js function
    selected_groups = request.args.get('selected_groups')
    selected_keywords = request.args.get('selected_keywords')
    selected_keyword_values = request.args.get('selected_keyword_values')

    # some checks on selected path
    if not db_path :
        return "<h4 style='align=center'><i class='fa fa-info'></i> No database selected. Select a database in Preferences first.</h4>"
    if not os.path.exists(db_path):
        return "<h4 style='align=center'><i class='fa fa-exclamation'></i> Path to database not found.</h4>"

    # handle selected groups and keywords
    if selected_groups == "" or selected_groups == "none":
        selected_groups = None
    else:
        selected_groups = selected_groups.split(",")

    if selected_keywords == "" or selected_keywords == "none":
        selected_keywords = None
    else:
        selected_keywords = selected_keywords.split(",")

    if selected_keyword_values == "" or selected_keyword_values == "none":
        selected_keyword_values = None
    else:
        selected_keyword_values = selected_keyword_values.split(",")

    if selected_keyword_values:
        apply_filter = or_(*[Main.keywords.any(name=selected_keywords[0], value=value) for value in selected_keyword_values])
        selected_keywords = None
    else:
        apply_filter = None

    # load table
    session = api.connect_database(db_path = db_path)
    table = api.get_entry_table(session,
                                group_names=selected_groups,
                                keyword_names=selected_keywords,
                                columns=show_columns,
                                apply_filter=apply_filter,
                                # order_by=order_by,
                                # order=order
                                )
    session.close()

    # stop if table is empty
    if table.shape[0] == 0:
        return "<h2 style='align=center'><i class='fa fa-info'></i> No entries found</h2>"

    # convert table to proper HTML
    pd.set_option('display.max_colwidth', -1) # let pandas print the full entry to HTML table

    # Order is important ! dont switch table["path"] and table["entry_id"]
    link_template = '<a href="details?entry_id={entry_id}">{link_name}</a>'
    table["path"] = table.apply(
       lambda row: link_template.format(entry_id=str(row.entry_id), link_name=row.path), axis=1)
    table["entry_id"] = table["entry_id"].apply(
       lambda entry_id: link_template.format(entry_id=entry_id, link_name=entry_id))
    #table["path"] = table["path"].apply(lambda x: '<a href="{0}" target="blank">{0}</a>'.format(x), )
    # convert dates
    table["updated_on"] = table["updated_on"].apply(lambda x: x.strftime('%Y/%m/%d'))
    table["added_on"] = table["added_on"].apply(lambda x: x.strftime('%Y/%m/%d'))
    table["created_on"] = table["created_on"].apply(lambda x: x.strftime('%Y/%m/%d') if x not in [None, pd.NaT] else "--")

    return table.to_html(classes=str("table"), escape=False, index=False, border=0) # convert to HTML

@blueprint.route('/details/')
def viewer_details():

    # get the path to selected DB
    db_path = current_app.config['SELECTED_DATABASE']['path']
    entry_id = request.args.get('entry_id')
    session = api.connect_database(db_path=db_path)

    sim = api.get_entry_details(session=session, entry_id=entry_id)
    meta = api.get_meta_groups(session, entry_id, as_list=True)
    keywords = api.get_keywords(session=session, entry_id=entry_id)

    session.close()

    # render template
    return render_template(
        'viewer_details.html',
        sim=sim,
        meta=meta,
        keywords=keywords,
    )