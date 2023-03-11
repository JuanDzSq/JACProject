from flaskr.backend import Backend
from flask import Flask, render_template, session
import io


def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        greeting = "Welcome to Team JAC's Wiki!!"
        return render_template("main.html", greeting = greeting)

    # TODO(Project 1): Implement additional routes according to the project requirements.

    @app.route("/nav_bar")
    def nav_bar():
        if 'username' in session:
            return f'{session["username"]}'    
        

        return render_template("navigation_bar.html", username = 'username')

    @app.route("/pages")
    def pages():
        return render_template("pages.html")

    @app.route("/pages/<name>")
    def get_pages(name):
        backend = Backend()
        name_page = name + ".html"
        content_str = backend.get_wiki_page(name_page)
        return render_template("template_page.html",content_str = content_str)

    #These pages will be inside "pages.html"
    #numbers are place holders for the actual name of the content
    @app.route("/pages/Survival")
    def Survival():
        return render_template("Survival.html")
    @app.route("/pages/Horror")
    def Horror():
        return render_template("Horror.html")
    @app.route("/pages/Sports")
    def Sports():
        return render_template("Sports.html")
    @app.route("/pages/Action_Adventure")
    def Action_Adventure():
        return render_template("Action_Adventure.html")
    @app.route("/pages/Simulation")
    def Simulation():
        return render_template("Simulation.html")
    @app.route("/pages/Multiplayer_Online_Battle")
    def Multiplayer_Online_Battle():
        return render_template("Multiplayer_Online_Battle.html")
    @app.route("/pages/First_Person_Shooter")
    def First_Person_Shooter():
        return render_template("First_Person_Shooter.html")
    @app.route("/pages/Puzzles")
    def Puzzles():
        return render_template("Puzzles.html")
    @app.route("/pages/Augumented_Reality")
    def Augumented_Reality():
        return render_template("Augumented_Reality.html")
    @app.route("/pages/Role_Playing")
    def Role_Playing():
        return render_template("Role_Playing")

    @app.route("/about")
    def about():
        return render_template("about.html")
    
    @app.route("/about_img")
    def about_images():
        Backend = backend()
        new_image_bytes = Backend.get_image("image_name")
        image = Image.open(io.BytesIO(new_image_bytes))
        
        return image
    

