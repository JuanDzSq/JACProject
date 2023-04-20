from flask import Flask, flash, render_template, request, redirect, url_for, session
from markupsafe import Markup
from flaskr.backend import Backend
from fileinput import filename
import base64
import pathlib
import io
"""Contains all of the routes for the pages of our wiki, along with their implementation."""


def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.

        #greeting = "Welcome to Team JAC's Wiki!!"
        return render_template("main.html")

    # TODO(Project 1): Implement additional routes according to the project requirements.
    """
    The navigation route will determine if the session is true meaning that the user is logged in and will
    return the username to the html if in use, else it would just return the html

    session: The user is logged in or not logged in, depending the username will be returned

    """

    @app.route("/nav_bar")
    def nav_bar():
        #backend = Backend()
        if username in session:
            #return f'{session["username"]}'
            #username = f'{session["username"]}'
            username = session['username']
            return render_template("navigation_bar.html", username=username)

        return render_template("navigation_bar.html")

    """
    The page list will be created with the page names retrieved from the backend. Then the list will be returned 
    to the pages.html and the links will be accessible there

    backend: get_all_page_names will be accessed and all exisiting pages will be in a list
    """

    @app.route("/pages")
    def pages():
        backend = Backend()
        page_list = backend.get_all_page_names()
        return render_template("pages.html", page_list=page_list)

    @app.route("/pages/<name>", methods=["GET", "POST"])
    def get_pages(name):
        """
        In the route get_pages, the user will be searching for a given page name, 
        depending on the page, the string retrieved from the backend will be implemented into 
        the template.html created, meaning that the page the user also creates will have its 
        own html page.

        Also, If a user makes a comment, the function checks if the user is logged in or not and if the user is logged in then allows the comment to be stored in the backend and pulls from the backend to display it in the page when the GET method is called. If the user is not logged in, it stores the comment as well as the page name in the session and calls the login route where the user can login themselves.

<<<<<<< HEAD
    @app.route("/pages/<name>")
    def get_pages(name): #upvotes and downvotes in parameters
        backend = Backend()
        content_str = Markup(backend.get_wiki_page(name))
        return render_template("template_page.html", content_str=content_str)
=======
        backend: get_wiki_page will access each page and return the string of the contents of the pages 
        """
        if request.method == "POST":
            if "loggedin" not in session:
                if request.form.get("comment") and not request.form.get(
                        "comment").isspace():
                    session["page_to_redirect"] = url_for('get_pages',
                                                          name=name)
                    session["comment_text"] = request.form.get("comment")
                return redirect("/login")
            else:
                backend = Backend()
                comment_text = request.form.get("comment")
                username = session.get("username")
                if comment_text and not comment_text.isspace():
                    page_name = name.split(".")[0]
                    backend.upload_comments(page_name, comment_text, username)
                else:
                    flash(
                        "Comment cannot be empty or contain only whitespace characters",
                        "error")
                    return redirect(url_for('get_pages', name=name))
                return redirect(url_for('get_pages', name=name))
        else:
            backend = Backend()
            content_str = Markup(backend.get_wiki_page(name))
            comment_file = name.split(".")[0]
            comments = backend.get_comments(comment_file)

            if "comment_text" in session:
                comment_text = session.pop("comment_text")
            else:
                comment_text = ""
            return render_template("template_page.html",
                                   content_str=content_str,
                                   comments=comments,
                                   comment_text=comment_text)
>>>>>>> 5d1652ede651d7c3a68a0ad004167b864100e66f

    """
    The about route will retrieve the images from the given authors and retrieve it through the backend. 
    Since the images are returned as bytes, they will be converted into jpegs so they can me shown in the 
    about.html page. 

    backend: get_image will get the images of the authors and return the bytes of the images
    """

    @app.route("/about", methods=["GET"])
    def about():
        authors = {
            "Abhishek Khanal": "Abhishek.jpg",
            "Juan": "Juan.jpeg",
            "Christin": "Christin.jpeg"
        }
        for author in authors:
            backend = Backend()
            image_bytes = backend.get_image(authors[author])
            authors[
                author] = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"

        return render_template("about.html", authors=authors)


    @app.route("/sign_up", methods=['GET', 'POST'])
    def sign_up():
        """Routes wiki to sign up page, where users can submit their username and password. 

        By filling the sign up form in sign_up.html, the username and password submitted
        will be uploaded to the username/password bucket only if the username is not 
        already in the bucket. Meaning that the user has to use a unique username. Additionally, 
        if the user is already logged in and tries to access this route, they will be redirected
        to the home page.

        Attributes:
            request.form: a dictionary that contains all information submitted in the form within
                the html.
            message: a message displayed for the benefit of the user if the sign up was unsuccessful.
            backend.sign_up(username, password): calls the sign_up function that will upload the 
                user sign up credentials to the bucket, if the username is unique. This will return
                True if the credentials were uploaded to the bucket.
            session: a flask specific dictionary that works over many different routes.
        Returns:
            a rendered template of sign_up.html, or if the sign up is successful, it
            redirects the wiki to the home page.
        """
        if session.get('loggedin', False) == True:
            return redirect(url_for('home'))

        backend = Backend()
        message = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            account_check = backend.sign_up(username, password)
            if account_check:  # True if sign up is successful
                session['loggedin'] = True
                session['username'] = username
                return redirect(url_for('home'))
            else:
                message = 'This username is already in use.'

        return render_template('sign_up.html', message=message)

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        """Routes wiki to the login page, where the user can submit their login credentials.

        By submitting login credentials to the form in login.html, the username and password
        will be checked against what is in the username/password bucket. If both the pair 
        have a match, then the login is succesful and the user gains logged in status and be 
        rerouted to the home page. If the user is already loggedin and attempts to enter this
        route, they will be rerouted to the home page. Also, if the session has page_to_redirect 
        then redirects the client to that page instead of redirecting to the home page.

        Attributes:
            request.form: a dictionary that contains all information submitted in the form within
                the html.
            message: a message displayed for the benefit of the user if the sign up was unsuccessful.
            backend.sign_in(username, password): calls the sign in function that will return True
                if the user login credentials have a match in the bucket.
            session: a flask specific dictionary that works over many different routes.
        Return:
            a rendered template of login.html, or if the login was successful, it will redirect the
            wiki to the home page.
        """
        if session.get('loggedin', False) == True:
            return redirect(url_for('home'))

        backend = Backend()
        message = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            account_check = backend.sign_in(username, password)
            if account_check:  # True if login is successful
                session['loggedin'] = True
                session['username'] = username
                if "page_to_redirect" in session:
                    redirect_url = session.pop("page_to_redirect")
                    return redirect(redirect_url)
                return render_template('main.html')
            else:
                message = 'Incorrect username or password.'

        return render_template('login.html', message=message)

    @app.route("/logout", methods=['GET', 'POST'])
    def logout():
        """If the user has logged in status, it will log out the user.

        Attributes:
            session: a flask specific dictionary that works over many different routes.
        Return:
            If the user has logged in status, it will log them out and redirect them to
            the home page. If the user does not have logged in status, they will be 
            immediately redirected to the home page.
        """
        if session.get('loggedin', False) == False:
            return redirect(url_for('home'))

        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('home'))

    @app.route("/upload", methods=['GET', 'POST'])
    def upload():
        """Routes to the upload page, where the user can upload images or html files.

        The user will be able to upload a file that will be uploaded to the
        wiki content bucket. They can only upload the following file types:
        md, html, txt, png, jpg, jpeg.

        Attributes:
            request.files: a flask dictionary that holds all of the files submitted
                in the file input in the upload.html.
            file_extension: has the file extension of the submitted file (like .html).
            allowed_types: has the only allowed file extensions for the uploaded file.
            message: a message displayed for the benefit of the user to let them know
                if the upload was successful or not.
            backend.upload(f, f.filename): the upload function used to upload the submitted
                file to the wiki content bucket.
        Returns:
            a rendered template of upload.html.
        """
        if session.get('loggedin', False) == False:
            return redirect(url_for('home'))

        backend = Backend()
        message = ''
        allowed_types = set(['.html', '.png', '.jpg', '.jpeg'])
        if request.method == 'POST':
            if 'file' not in request.files:
                message = 'File did not input'
                return render_template('upload.html', message=message)

            f = request.files['file']
            file_extension = pathlib.Path(f.filename).suffix
            if f.filename == '':
                message = 'File not chosen'
            elif f and '.' in f.filename and file_extension in allowed_types:
                message = 'Upload succesfull'
                backend.upload(f, f.filename)
            else:
                message = 'Only submit file types that are html, png, jpg, jpeg'

        return render_template('upload.html', message=message)
