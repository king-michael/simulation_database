from flask import render_template, request, redirect, flash,url_for
from databaseModel import Main, Keywords
from databaseViewer import app
from app import db
#from databaseAPI import getEntryTable
from datatables import DataTable
import json


@app.route('/')
def list_all():
    return render_template(
        'list.html',
        keywords = db.session.query(Keywords.name).filter(Keywords.value != None).distinct().all(),
        sims     = db.session.query(Main).all(),#join(Priority).order_by(Priority.value.desc())
    )

@app.route('/<entry_id>/')
def detail(entry_id):
    return render_template(
        'details.html',
        sim=db.session.query(Main).filter(Main.entry_id == entry_id).one()
    )
@app.route("/data")
def datatables():
    table = DataTable(request.args, Main, db.session.query(Main), ["id"])
    table.add_data(link=lambda obj: url_for('view_user', id=obj.id))
    # table.searchable(lambda queryset, user_input: perform_search(queryset, user_input))

    return json.dumps(table.json())

# def perform_search(queryset, user_input):
#     return queryset.filter(
#         db.or_(
#             User.full_name.like('%' + user_input + '%'),
#             Address.description.like('%' + user_input + '%')
#             )
#         )

# @app.route('/<name>')
# def list_todos(name):
#     category = Category.query.filter_by(name=name).first()
#     return render_template(
#         'list.html',
#         todos=Todo.query.filter_by(category=category).all(),# .join(Priority).order_by(Priority.value.desc()),
#         categories=Category.query.all(),
#
#     )
#
#
# @app.route('/new-task', methods=['GET', 'POST'])
# def new():
#     if request.method == 'POST':
#         category = Category.query.filter_by(id=request.form['category']).first()
#         #priority = Priority.query.filter_by(id=request.form['priority']).first()
#         #todo = Todo(category=category, priority=priority, description=request.form['description'])
#         todo = Todo(category=category, description=request.form['description'])
#         db.session.add(todo)
#         db.session.commit()
#         return redirect(url_for('list_all'))
#     else:
#         return render_template(
#             'new-task.html',
#             page='new-task',
#             categories=Category.query.all(),
#             #priorities=Priority.query.all()
#         )
#
#
# @app.route('/<int:todo_id>', methods=['GET', 'POST'])
# def update_todo(todo_id):
#     todo = Todo.query.get(todo_id)
#     if request.method == 'GET':
#         return render_template(
#             'new-task.html',
#             todo=todo,
#             categories=Category.query.all(),
#             #priorities=Priority.query.all()
#         )
#     else:
#         category = Category.query.filter_by(id=request.form['category']).first()
#         #priority = Priority.query.filter_by(id=request.form['priority']).first()
#         description = request.form['description']
#         todo.category = category
#         #todo.priority = priority
#         todo.description = description
#         db.session.commit()
#         return redirect('/')
#
#
# @app.route('/new-category', methods=['GET', 'POST'])
# def new_category():
#     if request.method == 'POST':
#         category = Category(name=request.form['category'])
#         db.session.add(category)
#         db.session.commit()
#         return redirect('/')
#     else:
#         return render_template(
#             'new-category.html',
#             page='new-category.html')
#
#
# @app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
# def edit_category(category_id):
#     category = Category.query.get(category_id)
#     if request.method == 'GET':
#         return render_template(
#             'new-category.html',
#             category=category
#         )
#     else:
#         category_name = request.form['category']
#         category.name = category_name
#         db.session.commit()
#         return redirect('/')
#
#
# @app.route('/delete-category/<int:category_id>', methods=['POST'])
# def delete_category(category_id):
#     if request.method == 'POST':
#         category = Category.query.get(category_id)
#         if not category.todos:
#             db.session.delete(category)
#             db.session.commit()
#         else:
#             flash('You have TODOs in that category. Remove them first.')
#         return redirect('/')
#
#
# @app.route('/delete-todo/<int:todo_id>', methods=['POST'])
# def delete_todo(todo_id):
#     if request.method == 'POST':
#         todo = Todo.query.get(todo_id)
#         db.session.delete(todo)
#         db.session.commit()
#         return redirect('/')
#
#
# @app.route('/mark-done/<int:todo_id>', methods=['POST'])
# def mark_done(todo_id):
#     if request.method == 'POST':
#         todo = Todo.query.get(todo_id)
#         todo.is_done = True
#         db.session.commit()
#         return redirect('/')
