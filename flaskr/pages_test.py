from flaskr import create_app
import pytest

# Install with: pip install 'moto[ec2,s3,all]'
import boto3
import moto
from botocore.exceptions import ClientError

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

# From: https://stackoverflow.com/questions/71765091/unit-testing-by-mocking-s3-bucket
@pytest.fixture
def empty_bucket():
    """Fixture that creates a fake bucket for testing."""
    moto_fake = moto.mock_s3()
    try:
        moto_fake.start()
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket="teamjac-users-passwords")
        yield conn
    finally:
        moto_fake.stop()

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

def test_sign_up_failed(client):
    data_dict = {'username': 'Juan Diaz', 'password': 'testing'}
    response = client.post("/sign_up", data=data_dict)

"""
Testing if the page will be accessed
"""
def test_working_get_pages(client):
    response = client.get("/pages")
    assert b"<title> Pages contained in the Team JAC Wiki! </title>" in response.data

"""
Testing if authors images show
"""
def test_working_about(client):
    author = {'Christin': 'Christin.jpeg'}
    response = client.get("/about", data = author)
    assert b"<h3>About this Wiki</h3>" in response.data


    
