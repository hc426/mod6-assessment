from app import create_test_client
import pytest

@pytest.fixture
def client():
    return create_test_client()

def test_home(client):
    resp = client.get('/')
    assert resp.data.decode() == 'hello world'

def test_get(client):
    resp = client.get('/')
    assert resp.status_code == 200

'''
def test_post(client):
    test_data = {'key_a': 'value_a', "John": "Testy"}
    resp = client.post('/resource', json=test_data, content_type = 'application/json')
    assert resp.status_code == 200
    assert b'POST method invoked with data' in resp.data
    
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



