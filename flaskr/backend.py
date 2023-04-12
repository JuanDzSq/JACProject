# TODO(Project 1): Implement Backend according to the requirements.

from google.cloud import storage
import hashlib
import io
from flask import send_file


class Backend:
    PASSWORD_PREFIX = "teamjacwillmakeit"

    def __init__(self):
        self.content_bucket_name = "teamjac-wiki_content"
        self.user_bucket_name = "teamjac-users-passwords"
        self.storage_client = storage.Client()
        self.content_bucket = self.storage_client.bucket(
            self.content_bucket_name)
        self.user_bucket = self.storage_client.bucket(self.user_bucket_name)

    def get_wiki_page(self, name):
        """
        Fetches the contents of the specified wiki page.

        Args:
        page_name: A string representing the name of the wiki page to retrieve.

        Returns:
        The text content of the wiki page, as a string.
        """
        page_name = name
        blob = self.content_bucket.blob(page_name)
        if not blob.exists():
            return f"Error: The file {page_name} does not exist."
        contents = blob.download_as_text()
        return contents

    def get_all_page_names(self):
        """
        Fetches the names of all wiki pages stored in the content bucket.

        Returns:
        A list of strings representing the names of all wiki pages in the content bucket.
        """
        page_names = []
        blobs = self.content_bucket.list_blobs(prefix="")
        for blob in blobs:
            if blob.name.endswith('.html'):
                page_names.append(blob.name.split('/')[-1])
        return page_names

    def upload_comments(self, page_name, comment_text, username):
        """
        Uploads a new comment to a comment file in the content bucket, or creates a new comment file for the particular page if it doesn't exist.

        Args:
        - page_name (str): The name of the page to upload the comment to.
        - comment_text (str): The text of the comment to upload.
        - username (str): The username of the user who posted the comment.
        """

        end_of_comment_message = "#2109abhishekfromnepal870+)_@)#_()*)(902#$%@"
        comment_text_file = f"{page_name}.txt"        
        blob = self.content_bucket.blob(comment_text_file)
        if blob.exists():
            comments_text = blob.download_as_text()
            comments = comments_text.split(end_of_comment_message)
        else:
            comments = []
        new_comment = f"{username}: {comment_text}"
        comments.append(new_comment)
        updated_comments_collection = end_of_comment_message.join(comments)
        blob.upload_from_string(updated_comments_collection)

    def get_comments(self, page_name):

        """
        Retrieves the comments from a text file in the content bucket for a given wiki page.

        Args:
        - page_name (str): The name of the wiki page to retrieve comments for.

        Returns:
        A list of strings representing the comments for the given wiki page.
        """
    
        end_of_comment_message = "#2109abhishekfromnepal870+)_@)#_()*)(902#$%@"
        comment_text_file = f"{page_name}.txt"
        blob = self.content_bucket.blob(comment_text_file)
        if blob.exists():
            comments_str = blob.download_as_text()
            comments = comments_str.split(end_of_comment_message)
            return comments        
        else:
            return []
            
    def upload(self, file_content, file_name):
        """
        Uploads the given file content to the content bucket with the given filename.
        
        Args:
        file_content: A file object containing the contents to be uploaded.
        file_name: The name to be given to the uploaded file.
        """
        blob = self.content_bucket.blob(file_name)
        blob.upload_from_file(file_content)

    def sign_up(self, username, password):
        """
        Creates a new user by uploading their hashed password to the user bucket.
        
        Args:
            username (str): The username of the user to be created.
            password (str): The plaintext password of the user to be created.
        
        Returns:
            bool: True if the user is created successfully, False if the user already exists.
        """
        prefixed_password = self.PASSWORD_PREFIX + password
        hashed_password = hashlib.sha256(prefixed_password.encode()).hexdigest()
        user_data = f"{username}:{hashed_password}"
        blob = self.user_bucket.blob(username)
        if blob.exists():
            return False
        blob.upload_from_string(user_data)
        return True

    def sign_in(self, username, password):
        """
        Signs in a user with the given username and password.

        Args:
        username: A string representing the username to sign in.
        password: A string representing the password to use for authentication.

        Returns:
        True if login is successful, False otherwise.
        """
        blob = self.user_bucket.blob(username)
        if not blob.exists():
            return False
        user_data = blob.download_as_text()

        stored_hashed_password = user_data.split(':')[1]
        prefixed_password = self.PASSWORD_PREFIX + password
        hashed_password = hashlib.sha256(prefixed_password.encode()).hexdigest()
        if hashed_password == stored_hashed_password:
            return True
        else:
            return False

    def get_image(self, image_name):
        """
        Retrieves the specified image from the user bucket and returns it as a Flask response.

        Args:
            image_name (str): The name of the image file to retrieve.

        Returns:
            A bytes object containing the requested image.
        """
        blob = self.content_bucket.blob(image_name)
        if not blob.exists():
            return f"The image {image_name} does not exist in the bucket."
        img_data = blob.download_as_bytes()
        return img_data


# example_backend = Backend()
# username = "Abhishek Khanal"
# page_name = "DreamLeagueSoccer"
# comment_text = "Hey All! I really liked the content you all have.\n I am so glad that you people are able to produce such a great contents.\n I enjoyed reading your contents.\n\nThankyou"
# example_backend.upload_comments(page_name, comment_text, username)

# example_backend = Backend()
# username = "Abhishek"
# page_name = "DreamLeagueSoccer"
# comment_text = "Hey All!"
# example_backend.upload_comments(page_name, comment_text, username)

# example_backend = Backend()
# page_name = "DreamLeagueSoccer"
# comments = example_backend.get_comments(page_name)
# print(comments)
# print(len(comments))