from app.statistics import blueprint
from flask import render_template, current_app, jsonify
import simdb.databaseAPI as api
from simdb.databaseModel import *
from sqlalchemy import func
import datetime

@blueprint.route('/')
def statistics_index():

    db_path = current_app.config['SELECTED_DATABASE']['path']

    session = api.connect_database(db_path=db_path)

    counts = {}

    counts["entries"] = session.query(Main).count()
    counts["keywords"] = session.query(Keywords.name).distinct().count()
    counts["groups"] = session.query(Groups).count()
    counts["archived"] = session.query(Main.archived).filter_by(archived=True).count()
    counts["deleted"] = session.query(Main.archived).filter_by(archived=True).count()

    session.close()

    return render_template(
        'index_statistics.html',
        counts = counts
    )


@blueprint.route('/entry_types/', methods=['POST'])
def statistics_entry_types():

    # open database
    db_path = current_app.config['SELECTED_DATABASE']['path']
    session = api.connect_database(db_path=db_path)

    # get data
    # [{'name': str, 'value': num}]
    data = [ {"name": name, "value": value} for name, value in session.query(Main.type, func.count(Main.type)).group_by(Main.type).all()]

    # close database
    session.close()

    # handle empty fields
    unknown = sum([e["value"] for e in data if e["name"] == '' or e["name"] == None])
    data = [e for e in data if e["name"] not in [None, '']]
    if unknown > 0:
        data.append({"name": "unknown", "value": unknown})

    # return data as json object
    return jsonify({"data" : data})


@blueprint.route('/entry_owner/', methods=['POST'])
def statistics_entry_owner():

    # open database
    db_path = current_app.config['SELECTED_DATABASE']['path']
    session = api.connect_database(db_path=db_path)

    # get data
    # [{'name': str, 'value': num}]
    data = [ {"name": name, "value": value} for name, value in session.query(Main.owner, func.count(Main.owner)).group_by(Main.owner).all()]

    # close database
    session.close()

    # handle empty fields
    unknown = sum([e["value"] for e in data if e["name"] == '' or e["name"] == None])
    data = [e for e in data if e["name"] not in [None, '']]
    if unknown > 0:
        data.append({"name": "unknown", "value": unknown})

    # return data as json object
    return jsonify({"data" : data})


@blueprint.route('/activity/', methods=['POST'])
def statistics_activity():

    # open database
    db_path = current_app.config['SELECTED_DATABASE']['path']
    session = api.connect_database(db_path=db_path)

    # count entries by day
    date = func.strftime("%Y-%m-%d", Main.created_on).label('date')
    created = dict(session.query(date, func.count(date)).group_by('date').all())

    date = func.strftime("%Y-%m-%d", Main.added_on).label('date')
    added = dict(session.query(date, func.count(date)).group_by('date').all())

    date = func.strftime("%Y-%m-%d", Main.updated_on).label('date')
    updated = dict(session.query(date, func.count(date)).group_by('date').all())

    # convert data
    dates = list(set(created.keys() + added.keys() + updated.keys()))
    dates.sort()
    # dates = ["/".join(d.split("-")[::-1]) for d in dates]
    print(dates)

    heatmap = [[i, 2, created[d]] if created.get(d) else [i, 2, 0] for i, d in enumerate(dates)] \
              + [[i, 1, added[d]] if added.get(d) else [i, 1, 0] for i, d in enumerate(dates)] \
              + [[i, 0, updated[d]] if updated.get(d) else [i, 0, 0] for i, d in enumerate(dates)]


    session.close()

    return jsonify({"dates" : dates, "heatmap" : heatmap})