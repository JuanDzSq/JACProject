from flask import Flask, render_template, request, redirect, url_for, session

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        return render_template("main.html")

    @app.route("/sign_up", methods =['GET', 'POST'])
    def sign_up():
        message = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            account_check = sign_up(username, password)
            if account_check:
                session['loggedin'] = True
                session['username'] = username
                return render_template('main.html')
            else:
                message = 'This username is already in use.'
        return render_template('sign_up.html', message = message)

    @app.route("/login", methods =['GET', 'POST'])
    def login():
        message = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            account_check = sign_in(username, password)
            if account_check:
                session['loggedin'] = True
                session['username'] = username
                return render_template('main.html')
            else:
                message = 'Incorrect username or password.]'
        return render_template('login.html', message = message)

    @app.route("/logout", methods =['GET', 'POST'])
    def logout():
        session.pop('loggedin', None)
        session.pop('username', None)
        redirect(url_for('home'))
