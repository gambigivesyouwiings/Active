from core import db, app
from core.models import Catalogue, Users
from datetime import datetime


def save_post(img_url, brand, vehicle_type, model_year, engine_rating, price, fuel, transmission, mileage, drive_type,
              folder, extras, availability="local", reserved=False, title="untitled"):
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
                         img_url=img_url,
                         availability=availability,
                         reserved=reserved)

    with app.app_context():
        db.session.add(new_post)
        db.session.commit()


def set_default_user():
    # Create the default user
    default_user = Users(
        id=47,  # Explicitly set the ID to 47
        email="defaultuser@example.com",  # Placeholder email
        name="Default User",
        password="hashedpassword",  # Replace with a securely hashed password
        created_on=datetime.utcnow(),
        confirmed_on=datetime.utcnow(),
        is_admin=False,
        is_confirmed=True,
        is_default_user=True,  # Mark this as the default user
        edits=0,
        posts_made=0,
        phone="+254732252382",  # Or set a placeholder phone number if needed
        deletions=0
    )

    with app.app_context():
        # Add the default user to the database
        db.session.add(default_user)
        db.session.commit()


def create_app():
    with app.app_context():
        db.create_all()


def delete_app():
    with app.app_context():
        db.drop_all()


# set_default_user()
# create_app()
# save_post(title="lexus  D4-D LEXUS 450D", model_year=2019, engine_rating=4500, transmission="automatic", fuel="diesel",
#           price=18500000, mileage=20000, extras="5 Seats, beige interior leather, Electric seats, fog lights",
#           vehicle_type="SUV", drive_type="4WD", brand="lexus", folder="/static/assets/cars/lexus",
#           img_url="['back.jpeg','front.jpeg','interior.jpeg']")
# save_post(title="Nissan XTRAIL", model_year=2017, engine_rating=3500, transmission="automatic", fuel="petrol",
#           price=2500000, mileage=50000,
#           extras="Heater Seats with leather Power boot 360° camera. Original Nissan rims. ", vehicle_type="SUV",
#           drive_type="AWD", brand="nissan", folder="/static/assets/cars/nissanxtrail",
#           img_url="['back.jpeg','front.jpeg','interior.jpeg']")
# save_post(title="Honda Vezel Hybrid", model_year=2017, engine_rating=1500, transmission="automatic", fuel="hybrid",
#           price=2800000, mileage=85000,
#           extras="Anti-Collission Assist, Keyless Entry, Alloy Rims, Push to start, Bumper Fog lights.",
#           vehicle_type="saloon", drive_type="AWD", brand="honda", folder="/static/assets/cars/honda",
#           img_url="['back.jpeg','front.jpeg','interior.jpeg']")
