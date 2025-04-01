import mimetypes
from flask import Flask, render_template, request, url_for, flash, jsonify
import json
import smtplib
from flask_bootstrap import Bootstrap
import os
import time
from random import randint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, ProgrammingError
from flask_migrate import Migrate

# from quickstart import GoogleDriveApi


map_api = os.getenv("map_api")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///content.db"


user, password = 'mushroommotors', 'kirubinjenga'
host = 'mushroommotors.mysql.pythonanywhere-services.com'
db_name = 'mushroommotors$again'

# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{user}:{password}@{host}/{db_name}"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()

Bootstrap(app=app)
db.init_app(app)


class Catalogue(db.Model):
    __tablename__ = "car_catalogue"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    brand = db.Column(db.String(250), nullable=True)
    vehicle_type = db.Column(db.String(250), nullable=True)
    model_year = db.Column(db.String(250), nullable=True)
    engine_rating = db.Column(db.String(250), nullable=True)
    price = db.Column(db.String(250), nullable=True)
    fuel = db.Column(db.String(250), nullable=True)
    transmission = db.Column(db.String(250), nullable=True)
    mileage = db.Column(db.String(250), nullable=True)
    drive_type = db.Column(db.String(250), nullable=True)
    extras = db.Column(db.String(250), nullable=True)

    folder_name = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=True)


def save_post(img_url, brand, vehicle_type, model_year, engine_rating, price, fuel, transmission, mileage, drive_type,
              folder, extras, title="untitled", ):
    new_post = Catalogue(title=title,
                         brand=brand,
                         vehicle_type=vehicle_type,
                         model_year=model_year,
                         engine_rating=engine_rating,
                         price=price,
                         fuel=fuel,
                         transmission=transmission,
                         mileage=mileage,
                         drive_type=drive_type,
                         extras=extras,
                         folder_name=folder,
                         img_url=img_url)

    with app.app_context():
        db.session.add(new_post)
        db.session.commit()


def create_app():
    with app.app_context():
        db.create_all()


def delete_app():
    with app.app_context():
        db.drop_all()


# delete_app()
# create_app()
# save_post(title="lexus  D4-D LEXUS 450D", model_year=2019, engine_rating=4500, transmission="automatic", fuel="diesel", price=18500000, mileage=20000, extras="5 Seats, beige interior leather, Electric seats, fog lights", vehicle_type="SUV", drive_type="4WD", brand="lexus", folder="/static/assets/cars/lexus", img_url="['back.jpeg','front.jpeg','interior.jpeg']")
# save_post(title="Nissan XTRAIL", model_year=2017, engine_rating=3500, transmission="automatic", fuel="petrol", price=2500000, mileage=50000, extras="Heater Seats with leather Power boot 360° camera. Original Nissan rims. ", vehicle_type="SUV", drive_type="AWD", brand="nissan", folder="/static/assets/cars/nissanxtrail", img_url="['back.jpeg','front.jpeg','interior.jpeg']")
# save_post(title="Honda Vezel Hybrid", model_year=2017, engine_rating=1500, transmission="automatic", fuel="hybrid", price=2800000, mileage=85000, extras="Anti-Collission Assist, Keyless Entry, Alloy Rims, Push to start, Bumper Fog lights.", vehicle_type="saloon", drive_type="AWD", brand="honda", folder="/static/assets/cars/honda", img_url="['back.jpeg','front.jpeg','interior.jpeg']")

# app.config['GOOGLEMAPS_KEY'] = os.getenv("google_key")
# drive = GoogleDriveApi()
# f = drive.download_file(real_file_id="1-e_w9p52otiIp5S8onSNB3tnPruDPQFC", path="static")
# print(f)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact_us", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        # if email != "":
        #     flash("Your message has been sent. Thank you!")
        print(email)
    return render_template("contact.html")


@app.route("/services", methods=["GET", "POST"])
def services():
    obj = time.localtime()
    t = time.asctime(obj)
    return render_template("services.html", time=t)


@app.route("/mportfolio")
def portfolio():
    return render_template("portfolio.html")


@app.route("/about_us")
def about():
    return render_template("about.html")


@app.route("/vehicles")
def blog():
    pages = db.paginate(db.select(Catalogue).order_by(Catalogue.model_year))
    return render_template("blog.html", pages=pages)


@app.route("/team")
def team():
    return render_template("team.html")


@app.route("/enquiry")
def get_quote():
    return render_template("get-a-quote.html")


@app.route("/blog_details/<int:post_id>")
def blog_details(post_id):
    try:
        post = db.session.query(Catalogue).filter_by(id=post_id).first()
    except ProgrammingError:
        posts = []
        create_app()
    else:
        folder = post.folder_name
        data = post.img_url
        text = data.strip("[]")
        urls = text.split(",")

        images = []
        for url in urls:
            path = folder + "/" + url.strip("'")
            images.append(path)

    print(images)
    number = int(post.price)
    price = f"{number:,}"

    return render_template("blog-details.html", images=images, post=post, price=price)


@app.route("/portfolio_det")
def portfolio_details():
    return render_template("admin.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
