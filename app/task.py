from flask import Blueprint, render_template, url_for, flash, redirect
from app import db
from app.models import Task
from app.forms import TaskForm, TaskUpdateForm

task_bp = Blueprint('task', __name__)

@task_bp.route('/')
def index():
    tasks = Task.query.order_by(Task.due_date.asc()).all()
    return render_template('task/index.html', tasks=tasks)

@task_bp.route('/add', methods=['GET', 'POST'])
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added!', 'success')
        return redirect(url_for('task.index'))
    return render_template('task/add_task.html', form=form)

@task_bp.route('/<int:task_id>', methods=['GET', 'POST'])
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskUpdateForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.completed = form.completed.data
        db.session.commit()
        flash('Task updated!', 'success')
        return redirect(url_for('task.index'))
    return render_template('task/task_detail.html', task=task, form=form)
