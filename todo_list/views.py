from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_pydantic import validate

from . import db
from .models import Task, TodoListQuery

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@bp.before_app_first_request
def create_tables():
    db.create_all()


@bp.route('/', methods=['GET'])
@validate()
def todo_list(query: TodoListQuery):
    status = query.status
    page = query.page
    filter_ = query.filter

    # Filter by status
    tasks = Task.query.order_by(Task.created_at.desc())
    if status == 'active':
        tasks = tasks.filter_by(active=True)
    elif status == 'completed':
        tasks = tasks.filter_by(active=False)

    # Filter by substring
    if filter_:
        tasks = tasks.filter(Task.description.contains(filter_))

    # Paginate tasks
    pagination = tasks.paginate(
        page, per_page=current_app.config['TASKS_PER_PAGE'], error_out=False
    )
    tasks = pagination.items

    return render_template(
        'todo.html', tasks=tasks, status=status, pagination=pagination
    )


@bp.route('add-task/', methods=['POST'])
def add_task():
    task_description = request.form.get('task', None)
    if task_description:
        task = Task(description=task_description)
        db.session.add(task)
        db.session.commit()
    return redirect(url_for('tasks.todo_list', **request.args))


@bp.route('complete-task/<int:task_id>/', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.active = False
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('tasks.todo_list', **request.args))
