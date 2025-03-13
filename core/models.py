from core import db


class Catalogue(db.Model):
    __tablename__ = "car_catalogue"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    brand = db.Column(db.String(250), nullable=True)
    vehicle_type = db.Column(db.String(250), nullable=True)
    model_year = db.Column(db.Integer, nullable=True)
    engine_rating = db.Column(db.String(250), nullable=True)
    price = db.Column(db.Integer, nullable=True)
    fuel = db.Column(db.String(250), nullable=True)
    transmission = db.Column(db.String(250), nullable=True)
    mileage = db.Column(db.Integer, nullable=True)
    drive_type = db.Column(db.String(250), nullable=True)
    extras = db.Column(db.String(250), nullable=True)

    folder_name = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=True)
