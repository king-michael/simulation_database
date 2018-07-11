from flask import render_template, request, redirect, flash,url_for
from databaseModel import Main, Keywords
from databaseViewer import app
from app import db


@app.route('/')
def list_all():
    return render_template(
        'list.html',
        sims = db.session.query(Main).all()
    )


@app.route('/<entry_id>/')
def detail(entry_id):
    return render_template(
        'details.html',
        sim = db.session.query(Main).filter(Main.entry_id == entry_id).one()
    )