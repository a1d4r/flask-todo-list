import pytest
from flask import Flask, Response, current_app
from flask.testing import FlaskClient

from todo_list import db
from todo_list.models import Task


class TestApp:
    def test_app_exists(self, app: Flask):
        assert app is not None

    def test_app_is_testing(self, app: Flask):
        assert app.config['TESTING'] is True


@pytest.mark.usefixtures('client')
class TestClientApp:
    def test_client_app_exists(self):
        assert current_app is not None

    def test_client_app_is_testing(self):
        assert current_app.config['TESTING'] is True


class TestToDoList:
    def test_todo_list_response_ok(self, client: FlaskClient):
        assert client.get('tasks/').status_code == 200

    def test_other_methods_not_allowed(self, client: FlaskClient):
        assert client.post('tasks/').status_code == 405
        assert client.put('tasks/').status_code == 405
        assert client.patch('tasks/').status_code == 405
        assert client.delete('tasks/').status_code == 405


class TestAddTask:
    def test_get_response_ok(self, client: FlaskClient):
        assert (
            client.post(
                'tasks/add-task/', data={'task': 'Task'}, follow_redirects=True
            ).status_code
            == 200
        )

    def test_other_methods_not_allowed(self, client: FlaskClient):
        assert client.get('tasks/add-task/').status_code == 405
        assert client.put('tasks/add-task/').status_code == 405
        assert client.patch('tasks/add-task/').status_code == 405
        assert client.delete('tasks/add-task/').status_code == 405

    def test_task_added(self, client: FlaskClient):
        client.post('tasks/add-task/', data={'task': 'Task'}, follow_redirects=True)
        tasks = Task.query.all()
        assert len(tasks) == 1
        task = tasks[0]
        assert task.description == 'Task'
        assert task.active is True


@pytest.mark.usefixtures('db_with_some_tasks')
class TestCompleteTask:
    def test_get_response_ok(self, client: FlaskClient):
        assert (
            client.post('/tasks/complete-task/1/', follow_redirects=True).status_code
            == 200
        )

    def test_other_methods_not_allowed(self, client: FlaskClient):
        assert client.get('tasks/complete-task/1/').status_code == 405
        assert client.put('tasks/complete-task/1/').status_code == 405
        assert client.patch('tasks/complete-task/1/').status_code == 405
        assert client.delete('tasks/complete-task/1/').status_code == 405

    def test_task_completed(self, client: FlaskClient):
        client.post('/tasks/complete-task/1/', follow_redirects=True)
        task = Task.query.get(1)
        assert task.active is False


@pytest.mark.usefixtures('app')
class TestModels:
    def test_task_model(self):
        task = Task(description='Desc')
        db.session.add(task)
        db.session.commit()
        assert task.description == 'Desc'
        assert task.active is True
        assert repr(task) == '<Task Desc>'


@pytest.mark.usefixtures('db_with_some_tasks')
class TestStatusFilter:
    def test_status_all(self, client: FlaskClient):
        response: Response = client.get('tasks/?status=all')
        assert response.status_code == 200
        for task in Task.query.all():
            assert task.description.encode() in response.data

    def test_status_active(self, client: FlaskClient):
        response: Response = client.get('tasks/?status=active')
        assert response.status_code == 200
        for task in Task.query.all():
            if task.active:
                assert task.description.encode() in response.data
            else:
                assert task.description.encode() not in response.data

    def test_status_completed(self, client: FlaskClient):
        response: Response = client.get('tasks/?status=completed')
        assert response.status_code == 200
        for task in Task.query.all():
            if task.active:
                assert task.description.encode() not in response.data
            else:
                assert task.description.encode() in response.data


@pytest.mark.usefixtures('large_db')
class TestPagination:
    @pytest.mark.parametrize('status', ['all', 'active', 'completed'])
    @pytest.mark.parametrize('page', list(range(1, 6)))
    def test_number_of_tasks_per_page(
        self, client: FlaskClient, status: str, page: int
    ):
        response: Response = client.get(f'tasks/?status={status}')
        count = sum(
            1 for task in Task.query.all() if task.description.encode() in response.data
        )
        assert count == current_app.config['TASKS_PER_PAGE']

    @pytest.mark.parametrize('status', ['all', 'active', 'completed'])
    def test_page_out_of_range(self, client: FlaskClient, status: str):
        response: Response = client.get(f'tasks/?status={status}&page=999')
        assert response.status_code == 200
        assert not any(
            task.description.encode() in response.data for task in Task.query.all()
        )


@pytest.mark.usefixtures('large_db')
class TestSearch:
    @pytest.mark.parametrize('substring', ['Task', '1', '21', 'No such task'])
    def test_search_by_substring(self, client: FlaskClient, substring: str):
        response: Response = client.get(f'tasks/?filter={substring}')
        assert response.status_code == 200
        assert all(
            not task.description.encode() in response.data
            or substring in task.description
            for task in Task.query.all()
        )


def test_main_app():
    from todo_list.app import app

    assert app is not None
