from flaskr.backend import Backend
from fileinput import filename
import pathlib
from flask import Flask, render_template, request, redirect, url_for, session

"""Contains all of the routes for the pages of our wiki, along with their implementation."""

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        return render_template("main.html")

    @app.route("/sign_up", methods =['GET', 'POST'])
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

    @app.route("/login", methods =['GET', 'POST'])
    def login():
        """Routes wiki to the login page, where the user can submit their login credentials.

        By submitting login credentials to the form in login.html, the username and password
        will be checked against what is in the username/password bucket. If both the pair 
        have a match, then the login is succesful and the user gains logged in status and be 
        rerouted to the home page. If the user is already loggedin and attempts to enter this
        route, they will be rerouted to the home page.

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
                return render_template('main.html')
            else:
                message = 'Incorrect username or password.'

        return render_template('login.html', message=message)

    @app.route("/logout", methods =['GET', 'POST'])
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

    @app.route("/upload", methods =['GET', 'POST'])
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