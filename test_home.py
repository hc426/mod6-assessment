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
    db = boto3.resource('dynamodb', region_name='ap-southeast-1')
    
    # Find table
    table = db.Table('todo-list-table')

    # Clear the table before testing
    for item in table.scan().get('Items', []):
        key = {'taskId': item['taskId']}
        table.delete_item(Key=key)

    #Add a new item to the table for testing purposes
    resp = client.post('/add', data={'title': 'Buy groceries'})

    # Read all items from the table
    response = table.scan()

    # Convert into a list
    todo_list = response.get('Items', [])

    assert len(todo_list) == 1

    assert todo_list[0]['title'] == 'Buy groceries'

    assert resp.status_code == 302 # Redirect to home

def test_update(client):
    resp = client.get('/update/1')

    db = boto3.resource('dynamodb', region_name='ap-southeast-1')
    
    # Find table
    table = db.Table('todo-list-table')

    # Read all items from the table
    response = table.scan()

    # Convert into a list
    todo_list = response.get('Items', [])

    print(todo_list)

    assert todo_list[0]['completed']

    assert resp.status_code == 302 # Redirect to home

def test_delete(client):
    resp = client.get('/delete/1')
    
    db = boto3.resource('dynamodb', region_name='ap-southeast-1')
    
    # Find table
    table = db.Table('todo-list-table')

    # Read all items from the table
    response = table.scan()

    # Convert into a list
    todo_list = response.get('Items', [])

    assert len(todo_list) == 0

    assert resp.status_code == 302 # Redirect to home


