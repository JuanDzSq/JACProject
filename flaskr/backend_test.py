from flaskr.backend import Backend

# TODO(Project 1): Write tests for Backend methods.

import pytest
import hashlib
# from unittest.mock import Mock
from unittest.mock import MagicMock
import io

@pytest.fixture
def backend():
    """
    Fixture for creating a Backend instance with mocked content and user buckets for unit testing
    """
    backend = Backend()
    backend.content_bucket = MagicMock()
    backend.user_bucket = MagicMock()
    return backend

def test_get_wiki_page(backend):
    """
    Test that the `get_wiki_page` method retrieves the correct content for an existing page.
    """
    mock_page_name = "TeamJacHomePage.html"
    mock_page_content = "<html><body><h1>This is TeamJAC</h1></body></html>"
    
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True

    backend.content_bucket.blob.return_value = mock_blob

    page_blob = backend.content_bucket.blob(mock_page_name)
    page_blob.upload_from_string(mock_page_content)
    retrieved_content = backend.get_wiki_page(mock_page_name)
    assert retrieved_content == page_blob.download_as_text()


def test_get_wiki_page_when_page_doesnot_exists(backend):
    """
    This test checks that the appropriate error message is returned when a non-existent wiki page is requested using the get_wiki_page method of the backend.
    """
    non_existing_page_name = "TeamJacNoneExistingPage.html"
    mock_blob = MagicMock()
    backend.content_bucket.blob.return_value = mock_blob
    mock_blob.exists.return_value = False

    expected_output = f"Error: The file {non_existing_page_name} does not exist."
    result = backend.get_wiki_page(non_existing_page_name)
    assert result == expected_output


def test_get_all_page_names(backend):
    print("Accessed")
    """
    Tests that the get_all_page_names method returns the correct list of page names by mocking the content bucket.
    """
    mock_blob_1 = MagicMock()
    mock_blob_1.name = "Pages/page1.html"
    mock_blob_2 = MagicMock()
    mock_blob_2.name = "Pages/page2.html"
    mock_blob_3 = MagicMock()
    mock_blob_3.name = "Pages/page3.txt"
  
    backend.content_bucket.list_blobs.return_value = [mock_blob_1, mock_blob_2, mock_blob_3]
    assert backend.get_all_page_names() == ['page1.html', 'page2.html']


def test_upload_html_file(backend):
    """
    Tests the functionality of the upload method in the Backend class by uploading a mock file content and verifying its existence in the content bucket.
    """
    mock_file_content = "<html><head></head><body><h1>Hello, World!</h1></body></html>"
    mock_file_name = "abhishek.html"

    mock_blob = MagicMock()
    backend.content_bucket.blob.return_value = mock_blob
    backend.upload(mock_file_content, mock_file_name)
    mock_blob = backend.content_bucket.blob(mock_file_name)
    assert mock_blob.exists()
    mock_blob.download_as_string.return_value = mock_file_content
    assert mock_blob.download_as_string() == mock_file_content
    mock_blob.upload_from_file.assert_called_with(mock_file_content)


def test_upload_image_file(backend):
    """
    Tests the functionality of the upload method in the Backend class by uploading a mock image file and verifying its existence in the content bucket.
    """
    mock_file_name = "test_image.png"
    mock_file_content = io.BytesIO(b"Replica of some bytes in image")
    mock_file_content.seek(0)

    mock_blob = MagicMock()
    backend.content_bucket.blob.return_value = mock_blob
    backend.upload(mock_file_content, mock_file_name)
    mock_blob = backend.content_bucket.blob(mock_file_name)
    assert mock_blob.exists()
    mock_blob.download_as_bytes.return_value = b"Replica of some bytes in image"
    assert mock_blob.download_as_bytes() == b"Replica of some bytes in image"
    mock_blob.upload_from_file.assert_called_with(mock_file_content)


def test_sign_up_new_user(backend):
    """
    Tests that a new user can be successfully created and True is returned.
    """
    username = "AbhishekKhanal123"
    mock_blob_1 = MagicMock()
    mock_blob_1.exists.return_value = False

    backend.user_bucket.blob.return_value = mock_blob_1

    result = backend.sign_up(username, "somepasswordnewpassword123")
    assert result == True


def test_sign_up_existing_user(backend):
    """
    Tests that attempting to sign up with an existing username returns False.
    """
    username = "Abhishek"
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    backend.user_bucket.blob.return_value = mock_blob

    result = backend.sign_up(username, "somepassword")
    assert result == False

def test_sign_in_user_exists(backend):
    """
    Test that the `sign_in` method returns True when a user with the given username and correct password exists.
    """
    username = "Abhishek"
    password = "mypassword"
    hashed_password = hashlib.sha256(("teamjacwillmakeit" + password).encode()).hexdigest()
    user_data = f"{username}:{hashed_password}"
    
    mock_blob = MagicMock()
    mock_blob.download_as_text.return_value = user_data

    backend.user_bucket.blob.return_value = mock_blob

    result = backend.sign_in(username, password)
    assert result == True


def test_sign_in_user_does_not_exist(backend):
    """
    Test that the `sign_in` method returns False when a user with the given username does not exist.
    """
    username = "NonExistentUser"
    password = "Somepassword"

    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    backend.user_bucket.blob.return_value = mock_blob

    result = backend.sign_in(username, password)
    assert result == False

def test_sign_in_incorrect_password(backend):
    """
    Test that the `sign_in` method returns False when a user with the given username exists,
    but the provided password is incorrect.
    """    
    username = "Abhishek"
    password = "mypassword"
    hashed_password = hashlib.sha256("wrongpassword".encode()).hexdigest()
    user_data = f"{username}:{hashed_password}"

    mock_blob = MagicMock()
    mock_blob.download_as_text.return_value = user_data
    backend.user_bucket.blob.return_value = mock_blob
    result = backend.sign_in(username, password)
    assert result == False

def test_get_image(backend):
    """
    This unit test checks if the get_image method in the backend module correctly retrieves and returns the expected image bytes from the content bucket.
    """
    image_name = "test_image.jpg"
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True

    mock_image_data = b"Mock image bytes data"
    mock_blob.download_as_bytes.return_value = mock_image_data
    backend.content_bucket.blob.return_value = mock_blob
    result = backend.get_image(image_name)
    assert isinstance(result, bytes)
    assert result == mock_image_data


def test_get_image_non_existent(backend):
    """
    Test that an appropriate error message is returned when a non-existent image is requested from the content bucket
    using the get_image method.
    """
    image_name = "non_existent_image.jpg"
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False

    backend.content_bucket.blob.return_value = mock_blob
    result = backend.get_image(image_name)
    assert isinstance(result, str)
    assert result == f"The image {image_name} does not exist in the bucket."
