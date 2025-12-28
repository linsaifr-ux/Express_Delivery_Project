import pytest
import sys
import os

# Add root directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_key'
    with app.test_client() as client:
        yield client

def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Express Delivery' in rv.data

def test_track_page(client):
    rv = client.get('/track')
    assert rv.status_code == 200
    assert b'Track Your Package' in rv.data

def test_login_page(client):
    rv = client.get('/login')
    assert rv.status_code == 200
    assert b'Login' in rv.data

def test_register_page(client):
    rv = client.get('/register')
    assert rv.status_code == 200
    assert b'Register' in rv.data

def test_register_post(client):
    data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'phone': '0912345678',
        'address': 'Taipei City',
        'password': 'password',
        'billing_pref': 'on_delivery'
    }
    rv = client.post('/register', data=data, follow_redirects=True)
    assert rv.status_code == 200
    # Check for success message or redirect to login (which shows Login header)
    assert b'Login' in rv.data or b'Registration successful' in rv.data
