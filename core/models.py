from core import db
from flask_login import UserMixin


class Catalogue(db.Model):
    __tablename__ = "car_catalogue"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=True)
    brand = db.Column(db.String(250), nullable=True)
    vehicle_type = db.Column(db.String(250), nullable=True)
    model_year = db.Column(db.Integer, nullable=True)
    engine_rating = db.Column(db.String(250), nullable=True)
    price = db.Column(db.Integer, nullable=True)
    fuel = db.Column(db.String(250), nullable=True)
    transmission = db.Column(db.String(250), nullable=True)
    mileage = db.Column(db.Integer, nullable=True)
    drive_type = db.Column(db.String(250), nullable=True)
    extras = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(1000), nullable=True)
    folder_name = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.Text, nullable=True)
    availability = db.Column(db.String(250), nullable=True)
    condition = db.Column(db.String(250), nullable=True)
    reserved = db.Column(db.Boolean, default=False, nullable=True)
    sold = db.Column(db.Boolean, default=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)  # New foreign key


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    name = db.Column(db.String(250), unique=False, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    is_default_user = db.Column(db.Boolean, default=False)
    edits = db.Column(db.Integer, nullable=True)
    posts_made = db.Column(db.Integer, nullable=True)
    phone = db.Column(db.String(15), nullable=True)

    deletions = db.Column(db.Integer, nullable=True)
    posts = db.relationship('Catalogue', backref='author', lazy=True, cascade="save-update, merge, refresh-expire")  # New relationship
