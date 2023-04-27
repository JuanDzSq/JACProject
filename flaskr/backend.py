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

    def upload_user_vote(self, username: str, page_name: str, vote: int):
        blob = self.content_bucket.blob("user_votes_file.txt")

        users_separator = "-/-User-/-"
        user_and_votes_separator = "<-User / Page Votes->"
        dictionary_separator = "-/-Dict-/-"
        key_value_separator = "<-Key / Value->"
        prev_vote = -1  # -1 means that the user hasn't made a vote, which is the default case.

        if blob.exists():
            users_vote_str = blob.download_as_text()
            users_list = users_vote_str.split(
                users_separator)  # Makes list of users
            for i in range(len(users_list)):
                users_list[i] = users_list[i].split(
                    user_and_votes_separator
                )  # Makes lists of [username, all page votes]

            user_found = False  # A flag for whether a user is found or not
            for i in range(len(users_list)):
                if users_list[i][
                        0] == username:  # True if user is found within users_vote_str
                    user_found = True
                    users_list[i][1] = users_list[i][1].split(
                        dictionary_separator
                    )  # Make a list of [page vote 1, page vote 2, etc.]
                    page_found = False  # A flag for whether a page is found or not
                    for j in range(len(users_list[i][1])):
                        users_list[i][1][j] = users_list[i][1][j].split(
                            key_value_separator
                        )  # Makes lists of [page_name, vote]
                        if users_list[i][1][j][
                                0] == page_name:  # True if page_name is in the user's page votes string
                            page_found = True
                            prev_vote = int(
                                users_list[i][1][j]
                                [1])  # Gets the original vote of the user
                            if vote == prev_vote:  # If the user reclicks their previous vote, then their vote is canceled and set to 1
                                users_list[i][1][j][1] = str(-1)
                            else:
                                users_list[i][1][j][1] = str(vote)
                    if not page_found:
                        users_list[i][1].append([page_name, str(vote)])

                    for j in range(len(users_list[i][1])):
                        users_list[i][1][j] = key_value_separator.join(
                            users_list[i][1][j])
                    users_list[i][1] = dictionary_separator.join(
                        users_list[i][1])

            if not user_found:
                users_list.append(
                    [username, page_name + "<-Key / Value->" + str(vote)])
            for i in range(len(users_list)):
                users_list[i] = user_and_votes_separator.join(users_list[i])
            users_vote_str = users_separator.join(users_list)
        else:
            users_vote_str = username + "<-User / Page Votes->" + page_name + "<-Key / Value->" + str(
                vote)
        self.upload_page_votes(page_name, vote, prev_vote)
        blob.upload_from_string(users_vote_str)

    def get_user_vote(self, username, page_name) -> int:
        blob = self.content_bucket.blob("user_votes_file.txt")

        users_separator = "-/-User-/-"
        user_and_votes_separator = "<-User / Page Votes->"
        dictionary_separator = "-/-Dict-/-"
        key_value_separator = "<-Key / Value->"

        if blob.exists():
            users_vote_str = blob.download_as_text()
            users_list = users_vote_str.split(
                users_separator)  # Makes list of users
            for i in range(len(users_list)):
                users_list[i] = users_list[i].split(
                    user_and_votes_separator
                )  # Makes lists of [username, all page votes]

            for i in range(len(users_list)):
                if users_list[i][
                        0] == username:  # True if user is found within users_vote_str
                    users_list[i][1] = users_list[i][1].split(
                        dictionary_separator
                    )  # Make a list of [page vote 1, page vote 2, etc.]
                    for j in range(len(users_list[i][1])):
                        users_list[i][1][j] = users_list[i][1][j].split(
                            key_value_separator
                        )  # Makes lists of [page_name, vote]
                        if users_list[i][1][j][
                                0] == page_name:  # True if page_name is in the user's page votes string
                            return int(users_list[i][1][j][1])
        return -1  # Return -1 if the user is not found, or if the page is not found

    def vote_result(self, vote: int, prev_vote: int) -> tuple:
        if vote == prev_vote and vote == 0:
            return (0, -1)  # Cancel downvote
        elif vote == prev_vote and vote == 1:
            return (-1, 0)  # Cancel upvote
        elif vote == 1 and prev_vote == 0:
            return (1, -1)  # Switch vote from downvote to upvote
        elif vote == 0 and prev_vote == 1:
            return (-1, 1)  # Switch vote from upvote to downvote
        elif vote == 0:
            return (0, 1)
        else:
            return (1, 0)

    def upload_page_votes(self, page_name, vote: int, prev_vote: int):
        blob = self.content_bucket.blob("page_votes_file.txt")

        pages_separator = "-/-Page-/-"
        page_votes_separator = "<-Page / Page Votes->"
        votes_separator = "<-Up / Down->"
        if blob.exists():
            pages_votes_str = blob.download_as_text()
            pages_list = pages_votes_str.split(pages_separator)
            for i in range(len(pages_list)):
                pages_list[i] = pages_list[i].split(page_votes_separator)

            page_found = False
            for i in range(len(pages_list)):
                if pages_list[i][0] == page_name:
                    page_found = True
                    pages_list[i][1] = pages_list[i][1].split(votes_separator)
                    old_upvote = int(pages_list[i][1][0])
                    old_downvote = int(pages_list[i][1][1])
                    upvote, downvote = self.vote_result(vote, prev_vote)
                    new_upvote = old_upvote + upvote
                    new_downvote = old_downvote + downvote
                    pages_list[i][1][0] = str(new_upvote)
                    pages_list[i][1][1] = str(new_downvote)
                    pages_list[i][1] = votes_separator.join(pages_list[i][1])

            if not page_found:
                if vote == 0:
                    pages_list.append([page_name, "0<-Up / Down->1"])
                else:
                    pages_list.append([page_name, "1<-Up / Down->0"])
            for i in range(len(pages_list)):
                pages_list[i] = page_votes_separator.join(pages_list[i])
            pages_votes_str = pages_separator.join(pages_list)
        else:
            if vote == 0:
                pages_votes_str = page_name + "<-Page / Page Votes->0<-Up / Down->1"
            else:
                pages_votes_str = page_name + "<-Page / Page Votes->1<-Up / Down->0"
        blob.upload_from_string(pages_votes_str)

    def get_page_votes(self, page_name) -> tuple:
        """Gives the votes corresponding to the given wiki page.
        
        If the page's votes are already in the content bucket, it retrieves its
        votes. If the page is not in the bucket, then it returns zero votes.

        Args:
        - page_name (str): The name of the wiki page to retrieve comments for.

        Returns: 
        A tuple with format (up_vote, down_vote), representing the votes of the 
        given wiki page.
        """
        blob = self.content_bucket.blob("page_votes_file.txt")

        pages_separator = "-/-Page-/-"
        page_votes_separator = "<-Page / Page Votes->"
        votes_separator = "<-Up / Down->"

        if blob.exists():
            pages_votes_str = blob.download_as_text()
            pages_list = pages_votes_str.split(pages_separator)
            for i in range(len(pages_list)):
                pages_list[i] = pages_list[i].split(page_votes_separator)

            for i in range(len(pages_list)):
                if pages_list[i][0] == page_name:
                    pages_list[i][1] = pages_list[i][1].split(votes_separator)
                    cur_upvote = int(pages_list[i][1][0])
                    cur_downvote = int(pages_list[i][1][1])
                    return (cur_upvote, cur_downvote)
        return (0, 0)

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
    def send_email(self, name, email, user_comment):
        port = 465  # For SSL
        password = "zsxprlnwxsqgyolw"
        context = ssl.create_default_context()
        sender_email = "teamjactechx@gmail.com"
        receiver_emails = ["christin_m@techexchange.in", email]

        message = f"""\
        Subject: {name} submmitted a Contact Support Form!

        New concern from {name} : 

            {user_comment}

        Please respond back to {name} at {email}
        
        """
        with smtplib.SMTP_SSL("smtp.gmail.com", port,
                              context=context) as server:
            server.login(sender_email, password)
            return server.sendmail(sender_email, receiver_emails, message)

    # Contact-support-form feature backend

    def user_email(self, name, email):
        prefixed_email = self.PASSWORD_PREFIX + email
        hashed_email = hashlib.sha256(prefixed_email.encode()).hexdigest()
        user_info = f"{hashed_email}"
        anonymous_user_info = f"{name}:{hashed_email}"
        blob = self.user_bucket.blob(name)

        if blob.exists():
            blob.upload_from_string(user_info)
        blob.upload_from_string(anonymous_user_info)


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
