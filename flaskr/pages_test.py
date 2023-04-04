from flaskr import create_app
import pytest
from flaskr.backend import Backend
from unittest.mock import MagicMock
from unittest.mock import patch

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def backend():
    with patch('flaskr.pages.Backend') as mock:
        yield mock

def test_request_sign_up(client):
    response = client.get("/sign_up")
    assert b"<title>User Sign Up</title>" in response.data

def test_request_login(client):
    response = client.get("/login")
    assert b"<title>User Login</title>" in response.data

def test_request_logout(client):
    """Checks if logout redirects to the home page"""
    response = client.get("/logout", follow_redirects=True)
    expected = client.get("/")
    assert len(response.history) == 1
    assert response.data == expected.data

def test_sign_up_successful(client, backend):
    backend().sign_up.return_value = True
    data_dict = {'username': 'JuanDiaz', 'password': 'test'}
    response = client.post("/sign_up", data=data_dict, follow_redirects=True)
    print(response)
    assert b"<title> TeamJAC Project </title>" in response.data

"""
Testing if the page will be accessed
"""
def test_working_get_pages(client, backend):
    backend().get_all_page_names = MagicMock(return_value=['action'])
    print(backend.get_all_page_names())
    response = client.get("/pages")
    print(response.data)
    assert b"<title> Pages contained in the Team JAC Wiki! </title>" in response.data
    assert b"<a href= /pages/action>action</a>" in response.data

# """
# Testing if authors images show
# """
# def test_working_about(client):
#     author = {'Christin': 'Christin.jpeg'}
#     response = client.get("/about", data = author)
#     assert b"<h3>About this Wiki</h3>" in response.data


    
