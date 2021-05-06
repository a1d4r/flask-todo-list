import pytest

from todo_list import create_app, db
from todo_list.models import Task


@pytest.fixture()
def app():
    app_ = create_app('testing')
    with app_.app_context():
        db.create_all()
        yield app_


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture()
def db_with_some_tasks(app):
    task1 = Task(id=1, description='First Task')
    task2 = Task(id=2, description='Second Task')
    task3 = Task(id=3, description='Third Task')
    task4 = Task(id=4, description='Fourth Task', active=False)
    db.session.add_all([task1, task2, task3, task4])
    db.session.commit()


@pytest.fixture()
def large_db(app):
    tasks = [
        Task(id=i, description=f'Task {i:02d}', active=(i < 50)) for i in range(100)
    ]
    db.session.add_all(tasks)
    db.session.commit()
