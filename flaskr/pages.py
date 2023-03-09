from flaskr.backend import Backend
from fileinput import filename
import pathlib
from flask import Flask, render_template, request, redirect, url_for, session

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        return render_template("main.html")

    @app.route("/sign_up", methods =['GET', 'POST'])
    def sign_up():
        if session.get('loggedin', False) == True:
            return redirect(url_for('home'))

        backend = Backend()
        message = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            account_check = backend.sign_up(username, password)
            if account_check:  # Sign up is successful
                session['loggedin'] = True  
                session['username'] = username
                return redirect(url_for('home'))
            else:
                message = 'This username is already in use.'

        return render_template('sign_up.html', message=message)

    @app.route("/login", methods =['GET', 'POST'])
    def login():
        if session.get('loggedin', False) == True:
            return redirect(url_for('home'))

        backend = Backend()
        message = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            account_check = backend.sign_in(username, password)
            if account_check:  # Login is successful
                session['loggedin'] = True  
                session['username'] = username
                return render_template('main.html')
            else:
                message = 'Incorrect username or password.'

        return render_template('login.html', message=message)

    @app.route("/logout", methods =['GET', 'POST'])
    def logout():
        if session.get('loggedin', False) == False:
            return redirect(url_for('home'))

        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('home'))

    @app.route("/upload", methods =['GET', 'POST'])
    def upload():
        if session.get('loggedin', False) == False:
            return redirect(url_for('home'))

        backend = Backend()
        message = ''
        allowed_types = set(['.md', '.html', '.txt'])
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
                message = 'Only submit file types that are md, html, txt'

        return render_template('upload.html', message=message)