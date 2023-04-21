from flaskr import create_app
import pytest
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


# def test_request_sign_up(client):
#     response = client.get("/sign_up")
#     assert b"<title>User Sign Up</title>" in response.data


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
    # print(response)
    assert b"<title> TeamJAC Project </title>" in response.data


# def test_sign_up_failed(client):
#     data_dict = {'username': 'Juan Diaz', 'password': 'testing'}
#     response = client.post("/sign_up", data=data_dict)
"""
Testing if the page will be accessed
"""


def test_working_get_pages(client, backend):
    backend().get_all_page_names = MagicMock(return_value=['action'])
    # print(backend.get_all_page_names())
    response = client.get("/pages")
    # print(response.data)
    assert b"<title> Pages contained in the Team JAC Wiki! </title>" in response.data
    assert b"<a href= /pages/action>action</a>" in response.data


def test_non_empty_user_comment_when_logged_in(client, backend):
    """
    Test that user can make comment when logged in. Tests that the backend method is called which uploads the comments in the buckets and the page is redirected again. 
    """
    page_name = "page1"
    comment = "Hey! This is just a test comment"
    username = "Abhishek"

    with client.session_transaction() as session:
        session['loggedin'] = True
        session['username'] = username

    backend_instance = backend.return_value
    backend_instance.upload_comments = MagicMock()

    response = client.post(f"/pages/{page_name}", data={"comment": comment})
    backend_instance.upload_comments.assert_called_once_with(
        page_name.split(".")[0], comment, username)
    assert response.status_code == 302
    assert response.headers['Location'] == f"/pages/{page_name}"
    assert b"Redirecting" in response.data

    resp = client.get(f'/pages/{page_name}')
    assert resp.status_code == 200
    assert b"submit" in resp.data


def test_empty_user_comment_when_logged_in(client, backend):
    """
    Test that user cannot post empty comment. An empty comment is just spaces with no alphabets. Tests that the backend method is not called and the user is redirected to the same page.
    """
    page_name = "page1"
    empty_comment = "       "
    username = "Abhishek"

    with client.session_transaction() as session:
        session['loggedin'] = True
        session['username'] = username

    backend_instance = backend.return_value
    backend_instance.upload_comments = MagicMock()

    response = client.post(f"/pages/{page_name}",
                           data={"comment": empty_comment})
    assert not backend_instance.upload_comments.called
    assert response.status_code == 302
    assert response.headers['Location'] == f"/pages/{page_name}"
    assert b"Redirecting" in response.data

    resp = client.get(f'/pages/{page_name}')
    assert resp.status_code == 200
    assert b"submit" in resp.data


def test_user_comment_when_not_logged_in(client, backend):
    """
    Test that user is redirected to the logged in page when he makes a comment post when not logged in
    """

    page_name = "page1"
    comment = "Hey! This is just a test comment"

    response = client.post(f"/pages/{page_name}", data={"comment": comment})

    backend_instance = backend.return_value
    backend_instance.upload_comments.assert_not_called()
    assert response.status_code == 302
    assert response.headers['Location'] == "/login"
    assert b"Redirecting" in response.data
    assert b'target URL: <a href="/login">/login</a>' in response.data


def test_user_comment_is_displayed_in_pages(client, backend):
    """
    Test that the user's comment is displayed on the page along with the existing comments
    """
    page_name = "page1"
    page_content = "<html><head></head><body><h1>Hello, World!</h1></body></html>"
    comments = ["Abhishek Khanal", "Khanal Abhishek"]

    backend_instance = backend.return_value
    backend_instance.get_wiki_page.return_value = page_content
    backend_instance.get_comments.return_value = comments

    response = client.get(f"/pages/{page_name}")

    assert response.status_code == 200
    assert page_content.encode() in response.data
    print(response.data)
    for comment in comments:
        assert comment.encode() in response.data


def test_login_redirects_to_last_page(client, backend):
    """
    Tests that after successful login, the user is redirected to the previously opened page where the user was about to post comment and also confirms that the response contains "Redirecting" and the name of the page that the user was on before logging in.
    """
    page_name = "page1"
    data_dict = {'username': 'testusername', 'password': 'test'}
    backend().sign_in.return_value = True

    with client.session_transaction() as session:
        session['page_to_redirect'] = page_name

    response = client.post("/login", data=data_dict)

    assert response.status_code == 302
    assert b"Redirecting" in response.data
    assert b"page1" in response.data


def test_page_in_session_after_comment_post(client, backend):
    """
    Test that the session is set to store the name of the previously opened page, which allows the user to back to the previously opened page where the user was about the post comment after he logs in.
    """

    page_name = "page1"
    comment = "This is test comment"

    response = client.post(f"/pages/{page_name}", data={'comment': comment})
    with client.session_transaction() as session:
        assert response.status_code == 302
        assert session['page_to_redirect'] == f"/pages/{page_name}"


def test_comment_stays_in_form_after_redirecting_from_login(client, backend):
    """
    Test that the comment text is retained in the session after redirecting from login and the comment stays in the form.
    """

    page_name = "mock_page1"
    comment = "Really liked the content of page1"

    response = client.post(f"/pages/{page_name}", data={'comment': comment})
    with client.session_transaction() as session:
        assert response.status_code == 302
        assert session["comment_text"] == comment

    response = client.get(response.location, follow_redirects=True)
    assert response.status_code == 200


"""
Testing if authors images show
"""
# def test_working_about(self):
#     author = {'Christin': 'Christin.jpeg'}
#     response = self.post("/about", data = author)
#     self.assertEqual(response.status_code)
