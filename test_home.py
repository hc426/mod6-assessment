from app import create_test_client
import pytest
import boto3

@pytest.fixture
def client():
    return create_test_client()

def test_index(client):
    resp = client.get('/index')
    assert resp.data.decode() == 'hello world'

def test_home(client):
    resp = client.get('/')
    assert resp.status_code == 200

def test_add(client):
    resp = client.post('/add', data={'title': 'Buy groceries'})

    db = boto3.resource('dynamodb', region_name='ap-southeast-1')
    
    # Find table
    table = db.Table('todo-list-table')

    # Read all items from the table
    response = table.scan()

    # Convert into a list
    todo_list = response.get('Items', [])

    assert len(todo_list) > 0

    assert todo_list[0]['title'] == 'Buy groceries'

    assert resp.status_code == 200

'''
def test_put(client):
    test_data = {'update': 'data', "id": 123}
    resp = client.put('/resource', json=test_data, content_type = 'application/json')
    assert resp.status_code == 200
    assert b'PUT method invoked with data' in resp.data

def test_delete(client):
    resp = client.delete('/resource')
    assert resp.status_code == 200
    assert resp.data.decode() == 'DELETE method invoked!'

def test_post_without_data(client):
    resp = client.post('/resource')
    assert resp.status_code == 415
'''



