# TODO(Project 1): Implement Backend according to the requirements.

from google.cloud import storage
import hashlib
import io
from flask import send_file

class Backend:

    def __init__(self):
        self.content_bucket_name = "teamjac-wiki_content"
        self.user_bucket_name = "teamjac-users-passwords"
        self.storage_client = storage.Client()
        self.content_bucket = self.storage_client.bucket(self.content_bucket_name)
        self.user_bucket = self.storage_client.bucket(self.user_bucket_name)
        
    def get_wiki_page(self, name):
        page_name = name
        blob = self.content_bucket.blob(page_name)
        if not blob.exists():
            return f"Error: The file {page_name} does not exist in the bucket."
        contents = blob.download_as_text()
        return contents

    def get_all_page_names(self):
        page_names = []
        blobs = self.content_bucket.list_blobs(prefix='Pages/')
        for blob in blobs:
            if blob.name.endswith('.html'):
                page_names.append(blob.name.split('/')[-1])
        return page_names

    def upload(self,file_path, data):
        blob = self.content_bucket.blob(data)
        blob.upload_from_filename(file_path)

    def sign_up(self, username, password):
        prefixed_password = "teamjacwillmakeit" + password
        blob = self.user_bucket.blob(username) # here this is blob name
        if blob.exists():
            return "User already exists"
        hashed_password = hashlib.sha256(prefixed_password.encode()).hexdigest()
        data = {"username": username, "password": hashed_password}
        blob.upload_from_string(str(data))
        return "User created successfully"

    def sign_in(self, username, password):
        blob = self.user_bucket.blob(username)
        if not blob.exists():
            return "User does not exist"
        user_data = blob.download_as_text()

        stored_credentials = user_data.split(':')
        stored_hashed_password = stored_credentials[-1]
        prefixed_password = "teamjacwillmakeit" + password
        hashed_password = hashlib.sha256(prefixed_password.encode()).hexdigest()

        if hashed_password == stored_hashed_password:
            return "Login Successful"
        else:
            return "Login Unsuccessful"

    def get_image(self, image_name):
        blob = self.user_bucket.blob(image_name)
        if not blob.exists():
            return f"Error: The image {image_name} does not exist in the bucket."
        img_stream = blob.download_as_bytes()
        return send_file(io.BytesIO(img_stream), mimetype='image/jpeg')
