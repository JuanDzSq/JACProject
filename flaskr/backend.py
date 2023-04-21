# TODO(Project 1): Implement Backend according to the requirements.

from google.cloud import storage
import hashlib
import io
import smtplib, ssl
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
    
    # TODO(christin): Update Contact support message to include the user's name. 
    def send_email(self, name, email):
        port = 465  # For SSL
        password = "zsxprlnwxsqgyolw"
        context = ssl.create_default_context()
        sender_email = "teamjactechx@gmail.com"
        receiver_emails = ["christin_m@techexchange.in", email]
        message = f"""\
        Subject: {name} submmitted a Contact Support Form!

        New concern from {name}.
        
        """
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            return server.sendmail(sender_email, receiver_emails, message)

    #Contact-support-form feature backend
    # def user_email(self, username, full_name, email):
    #     prefixed_email = self.PASSWORD_PREFIX + email
    #     hashed_email = hashlib.sha256(prefixed_email.encode()).hexdigest()
    #     user_data = f"{username}:{hashed_email}"
    #     blob = self.user_bucket.blob(username)
    #     if blob.exists():
    #         blob.upload_from_string(user_data)
            
    #     return True

    #     if not blob.exists():
    #         return False
    #     user_data = blob.download_as_text()

    #     stored_hashed_password = user_data.split(':')[1]
    #     prefixed_password = self.PASSWORD_PREFIX + password
    #     hashed_password = hashlib.sha256(prefixed_password.encode()).hexdigest()
    #     if hashed_password == stored_hashed_password:
    #         return True
    #     else:
    #         return False
