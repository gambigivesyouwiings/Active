from flask import render_template, request, abort, redirect, url_for, flash, make_response, jsonify
from flask_wtf.csrf import CSRFError, generate_csrf
from core import app, db, login_manager, send_email, generate_token, confirm_token
from core.models import Catalogue, Users
from core.forms import PostForm, RegisterForm, LoginForm, PostEditForm, EditProfileForm, CreatePostForm
import time
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy import desc, or_, and_
from functools import wraps
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import shutil
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename
import re
import json
import uuid
from google import genai


def create_app():
    with app.app_context():
        db.create_all()


def generate_unique_filename(destination, filename):
    # Use Pathlib for better extension handling
    path = Path(filename)
    ext = "".join(path.suffixes)  # Captures all extensions (e.g., .tar.gz)
    base = path.stem  # Original filename without extensions

    # Generate a unique filename with original base + UUID + extensions
    while True:
        unique_name = f"{uuid.uuid4().hex}{ext}"
        dest_path = os.path.join(destination, unique_name)

        # Ensure the filename doesn't already exist in the destination
        if not os.path.exists(dest_path):
            return unique_name


def save_post(img_url, brand, vehicle_type, model_year, engine_rating, price, fuel, transmission, mileage, drive_type,
              folder, extras, description, availability="local", condition="Foreign used", user_id=0, reserved=False,
              title="untitled"):
    new_post = Catalogue(title=title.capitalize(),
                         brand=brand.capitalize(),
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
                         condition=condition,
                         description=description,
                         availability=availability,
                         user_id=user_id,
                         reserved=reserved)

    with app.app_context():
        db.session.add(new_post)
        db.session.commit()


image_file_types = ['.webp', '.svg', '.png', '.avif', '.jpg', '.jpeg', '.jfif', '.jpe', '.pjp', '.gif', '.apn']

admin_list = ["balywonder@gmail.com", "pgigz23@gmail.com", "gambikimathi@students.uonbi.ac.ke"]


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# handle CSRF error
@app.errorhandler(CSRFError)
def csrf_error(e):
    return e.description, 400


# Function wrapper to protect some routes from non-admin access
def admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.email in admin_list:
            return f(*args, **kwargs)
        elif not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


def super_admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.email not in admin_list:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


def getai(user_message):
    key = os.getenv("GEMINI")
    client = genai.Client(api_key=key)
    # Send to Gemini
    prompt = "Write a short paragraph summary of the following vehicle with the attached features.It's not a must to mention all of them, just pick and choose what you deem is relevant. Tailor it for a car website audience in a documentary-like tone."
    full_prompt = f"{prompt}\n\nVehicle features: {user_message}"
    response = client.models.generate_content(model="gemini-2.0-flash", contents=full_prompt)

    # return jsonify({
    #     'response': response.text
    # })
    return response.text


@app.template_filter('number_format')
def number_format(value):
    return f"{int(value):,}"


@app.before_request
def redirect_to_www():
    if request.host == "mushroommotors.com":
        return redirect(f"https://www.mushroommotors.com", code=301)


@app.route("/", methods=["POST", "GET"])
def home():
    unique_brands = db.session.query(Catalogue.brand).distinct().all()
    unique = [category[0] for category in unique_brands]

    if request.method == "POST":
        page = 1
        per_page = 10
        # Get JSON data from the request
        form_data = request.form

        # Start with the base query
        query = Catalogue.query

        # Apply filters only if the corresponding value is not empty
        if form_data.get('keyword'):
            print("active")
            keyword = form_data['keyword'].strip()
            query = query.filter(
                (Catalogue.brand.ilike(f'%{keyword}%')) | (Catalogue.title.ilike(f'%{keyword}%'))
            )

        if form_data.get('brand') and form_data.get('brand') != "all":
            brand = form_data['brand'].strip()
            query = query.filter(Catalogue.brand == brand)
            print(query)

        if form_data.get('model') != "all":
            print(form_data.get('model'))
            model = form_data['model'].strip()
            query = query.filter(Catalogue.title == model)

        if form_data.getlist('price') and len(form_data.getlist('price')) > 0:
            price_ranges = form_data.getlist('price')
            price_filters = []
            for price_range in price_ranges:
                try:
                    if price_range == "Above 10M":
                        price_filters.append(Catalogue.price > 10000000)
                    else:
                        print("no")
                        min_price, max_price = map(
                            lambda x: int(x.replace('K', '000').replace('M', '000000').strip()),
                            price_range.split('-')
                        )
                        price_filters.append(and_(Catalogue.price >= min_price, Catalogue.price <= max_price))
                except ValueError:
                    print("error detected")
                    continue  # Ignore invalid price formats
            query = query.filter(or_(*price_filters))
        if form_data.get('availability'):
            availability = form_data['availability'].strip()
            if availability == "local":
                query = query.filter(Catalogue.availability == "local")
            elif availability == "import":
                query = query.filter(Catalogue.availability == "import")
            # For 'all', no additional filtering is applied

        order = form_data.get('order')
        if order == "old model":
            query = query.order_by(Catalogue.model_year)
        elif order == "mileage":
            query = query.order_by(Catalogue.mileage)
        elif order == "name ascending":
            query = query.order_by(Catalogue.title)
        elif order == "name descending":
            query = query.order_by(desc(Catalogue.title))
        else:
            # Execute the query and return the results
            query = query.order_by(desc(Catalogue.model_year))

        # Paginate the query results
        vehicles = query.paginate(page=page, per_page=per_page)
        return render_template("blog.html", num=page, admin_list=admin_list, pages=vehicles, brands=unique,
                               csrf_token=generate_csrf())
    last_six_entries = Catalogue.query.order_by(Catalogue.sold).order_by(Catalogue.id.desc()).limit(6).all()
    total_vehicles = Catalogue.query.count() + 30
    trucks = Catalogue.query.filter(Catalogue.vehicle_type == "SUV").count()
    sold = Catalogue.query.filter(Catalogue.sold).count() + 10
    return render_template("index.html", trucks=trucks, total=total_vehicles, sold=sold, admin_list=admin_list,
                           csrf_token=generate_csrf(), brands=unique,
                           pages=last_six_entries)


@app.route("/contact_us", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        send_email(to="mushroommotors25@gmail.com", subject=subject,
                   template=f"<div><p>You have a message from: {name} {email}</p><br><p>{message}</p></div>")
        # if email != "":
        #     flash("Your message has been sent. Thank you!")
        print(email)
    return render_template("contact.html", csrf_token=generate_csrf())


@app.route("/services", methods=["GET", "POST"])
def services():
    obj = time.localtime()
    t = time.asctime(obj)
    total_vehicles = Catalogue.query.count() + 30
    trucks = Catalogue.query.filter(Catalogue.vehicle_type == "SUV").count()
    sold = Catalogue.query.filter(Catalogue.sold).count() + 10
    return render_template("services.html", total=total_vehicles, suv=trucks, sold=sold, time=t)


@app.route("/mportfolio")
def portfolio():
    return render_template("portfolio.html")


@app.route("/about_us")
def about():
    return render_template("about.html")


@app.route("/vehicles", methods=["GET", "POST"])
def blog():
    unique_brands = db.session.query(Catalogue.brand).distinct().all()
    unique = [category[0] for category in unique_brands]
    # Get the page number from the query string
    try:
        page = int(request.args.get('page', '1'))
    except ValueError:
        page = 1
        print("The value error exception occurred on blog")
    per_page = 12  # Number of items per page
    selected_brand = request.args.get('selected_brand')
    selected_type = request.args.get('selected_type')
    selected_user = request.args.get('selected_user')

    if request.method == "POST":
        # Get JSON data from the request
        form_data = request.get_json()

        # Start with the base query
        query = Catalogue.query

        # Apply filters only if the corresponding value is not empty
        if form_data.get('keyword'):
            keyword = form_data['keyword'].strip()
            query = query.filter(
                (Catalogue.brand.ilike(f'%{keyword}%')) | (Catalogue.title.ilike(f'%{keyword}%'))
            )

        if form_data.get('brand') and form_data.get('brand') != "all":
            brand = form_data['brand'].strip()
            query = query.filter(Catalogue.brand == brand)

        if form_data.get('model') != "all":
            model = form_data['model'].strip()
            query = query.filter(Catalogue.title == model)

        if form_data.get('price') and len(form_data['price']) > 0:
            price_ranges = form_data['price']
            price_filters = []
            for price_range in price_ranges:
                try:
                    if price_range == "Above 10M":
                        price_filters.append(Catalogue.price > 10000000)
                    else:
                        print("no")
                        min_price, max_price = map(
                            lambda x: int(x.replace('K', '000').replace('M', '000000').strip()),
                            price_range.split('-')
                        )
                        print(min_price)
                        print(max_price)
                        price_filters.append(and_(Catalogue.price >= min_price, Catalogue.price <= max_price))
                except ValueError:
                    print("error detected")
                    continue  # Ignore invalid price formats
            query = query.filter(or_(*price_filters))
        if form_data.get('availability'):
            availability = form_data['availability'].strip()
            if availability == "local":
                query = query.filter(Catalogue.availability == "local")
            elif availability == "import":
                query = query.filter(Catalogue.availability == "import")
            # For 'all', no additional filtering is applied

        order = form_data.get('order')
        if order == "old model":
            query = query.order_by(Catalogue.model_year)
        elif order == "mileage":
            query = query.order_by(Catalogue.mileage)
        elif order == "name ascending":
            query = query.order_by(Catalogue.title)
        elif order == "name descending":
            query = query.order_by(desc(Catalogue.title))
        else:
            # Execute the query and return the results
            query = query.order_by(desc(Catalogue.model_year))

        # Paginate the query results
        vehicles = query.paginate(page=page, per_page=per_page)
        return render_template("filter_vehicles.html", num=page, pages=vehicles)

    if selected_brand:
        query = Catalogue.query
        query = query.filter(
            Catalogue.title.ilike(f"%{selected_brand}%") | Catalogue.brand.ilike(f"%{selected_brand}%"))
        query = query.order_by(desc(Catalogue.model_year))
        pages = query.paginate(page=page, per_page=per_page)
        return render_template("blog.html", num=page, pages=pages, admin_list=admin_list, brands=unique,
                               csrf_token=generate_csrf())
    if selected_type:
        query = Catalogue.query
        query = query.filter(
            Catalogue.vehicle_type.ilike(f"%{selected_type}%"))
        query = query.order_by(desc(Catalogue.model_year))
        pages = query.paginate(page=page, per_page=per_page)
        return render_template("blog.html", num=page, admin_list=admin_list, pages=pages, brands=unique,
                               csrf_token=generate_csrf())

    if selected_user:
        query = Catalogue.query

        # Filter by user_id
        query = query.filter(Catalogue.user_id == selected_user)

        # Order by model_year in descending order
        query = query.order_by(desc(Catalogue.model_year))

        # Paginate the results
        pages = query.paginate(page=page, per_page=per_page)
        return render_template("blog.html", num=page, admin_list=admin_list, pages=pages, brands=unique,
                               csrf_token=generate_csrf())

    pages = db.paginate(db.select(Catalogue).order_by(Catalogue.sold).order_by(desc(Catalogue.id)), page=page,
                        per_page=per_page)
    return render_template("blog.html", num=page, pages=pages, admin_list=admin_list, brands=unique,
                           csrf_token=generate_csrf())


@app.route("/team")
def team():
    return render_template("team.html")


@app.route("/enquiry")
def get_quote():
    return render_template("get-a-quote.html")


@app.route("/vehicle_details/<int:post_id>")
def blog_details(post_id):
    try:
        post = Catalogue.query.get_or_404(post_id)
    except ProgrammingError:
        images = []
    else:
        folder = post.folder_name
        data = post.img_url
        text = data.strip("[]")
        urls = text.split(",")

        images = []
        for url in urls:
            path = folder + "/" + url.strip().strip("'")
            images.append(path)

    number = int(post.price)
    price = f"{number:,}"
    features_data = {}
    if post.extras:
        try:
            features_data = json.loads(post.extras)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for vehicle ID {post_id}: {post.extras}")
            features_data = {'error': 'Could not load features'}
    # features = post.extras.split(",")
    # feature = [x.strip() for x in features if len(x.split(":")) <= 1]
    # spects = {
    #     x.split(":")[0].strip(): x.split(":")[1].strip()
    #     for x in re.split(r"[,;]", post.extras) if ":" in x
    # }
    # if post.user_id:
    #     user = db.session.query(Users).filter_by(id=post.user_id).first()
    #     if user:
    #         phone_number = user.phone
    #     else:
    #         phone_number = "+254732252382"

    # else:
    #     phone_number = "+254732252382"

    phone_number = "+254732252382"

    similar_six_entries = Catalogue.query.filter(
        Catalogue.vehicle_type.ilike(f"%{post.title}%") | Catalogue.brand.ilike(f"%{post.brand}%") | and_(
            Catalogue.price >= post.price - 1000000, Catalogue.price <= post.price + 1000000)).limit(6).all()

    return render_template("blog-details.html", pages=similar_six_entries, phone_number=phone_number,
                           features=features_data,
                           images=images, post=post, price=price, csrf_token=generate_csrf())


@app.route('/search', methods=["GET", "POST"])
def search():
    query = request.args.get("query")
    print(query)
    if query:
        results = Catalogue.query.filter(
            Catalogue.title.ilike(f"%{query}%") | Catalogue.brand.ilike(f"%{query}%")).limit(10).all()
    else:
        # results = Catalogue.query.limit(20).all()
        return '<div class="p-2 hide bd-highlight" id="results"></div>'
    if results:
        pass
    else:
        return render_template("noresults.html")

    return render_template("search.html", results=results)


@app.route("/options", methods=["POST"])
def options():
    brand = request.form.get('brand')
    results = Catalogue.query.filter(Catalogue.brand.ilike(f"%{brand}%")).distinct().all()
    models = [category.title for category in results]

    return render_template("options.html", models=models)


# Gives admin a chance to verify that indeed they want to delete a post
@app.route("/pre_delete/<int:index>", methods=["GET", "POST"])
@admin_only
def pre_delete(index):
    vehicle = Catalogue.query.get_or_404(index)
    if not current_user.is_admin:
        abort(403)  # Restrict to admins
    return render_template('confirm_delete_vehicle.html', csrf=generate_csrf(), vehicle=vehicle)


@app.route("/stock/<int:index>", methods=["GET", "POST"])
@admin_only
def stock(index):
    vehicle = Catalogue.query.get_or_404(index)
    if not current_user.is_admin:
        abort(403)  # Restrict to admins
    if request.method == "POST":
        sold = request.form.get('sold') == 'true'
        reserved = request.form.get('reserved') == 'true'
        available = request.form.get("availability") == 'true'

        # Fetch the user and toggle stock_availability status
        if sold:
            vehicle.sold = True
            vehicle.reserved = False
            print("sold")
        if reserved:
            vehicle.sold = False
            vehicle.reserved = True
            print("reserve")
        if available:
            vehicle.sold = False
            vehicle.reserved = False
            print("available")

        db.session.commit()
        # Return a partial HTML snippet with the updated checkbox state
        return render_template("update_stock.html", page=vehicle)

    return render_template('confirm_stock.html', csrf=generate_csrf(), vehicle=vehicle)


@app.route("/delete/<int:post_id>", methods=["DELETE"])
@admin_only
def delete_vehicle(post_id):
    vehicle = Catalogue.query.get_or_404(post_id)
    profile = Users.query.get_or_404(current_user.id)
    if profile.deletions:
        profile.deletions += 1
    else:
        profile.deletions = 1
    # Extract image URLs and paths
    folder = vehicle.folder_name
    try:
        shutil.rmtree(f"core/{folder}")
    except shutil.Error:
        flash("An error occurred, can't delete!", "danger")
        return redirect(url_for('blog'))

    db.session.delete(vehicle)
    db.session.commit()
    return '', 200  # HTMX expects an empty response


@app.route('/upload', methods=['GET', 'POST'])
@admin_only
def upload():
    form = PostForm()

    if form.validate_on_submit():
        # # --- MANUAL CHECK ---
        # if not form.file.data:
        #     flash("Please select at least one image to upload.", "error")
        #     # If the check fails on an AJAX request, return a JSON error
        #     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        #         return jsonify({'status': 'error', 'errors': {'file': ['Please upload a file.']}}), 400
        #     # For a standard submission, just re-render the form
        #     return render_template('upload.html', form=form)
        # # --- END OF MANUAL CHECK ---
        profile = Users.query.get_or_404(current_user.id)
        if profile.posts_made:
            profile.posts_made += 1
        else:
            profile.posts_made = 1
        uploaded_files = []
        new_name = datetime.now().strftime("%Y%m%d%S%f")
        destination = os.path.join("core/static/assets/cars/", new_name)
        try:
            if not os.path.exists(destination):
                os.makedirs(destination)
                print(f"Directory created: {destination}")
        except OSError as e:
            print(f"Error creating directory: {e}")
        # files = request.files.getlist(form.file)  # Fetch all uploaded files

        for key, file in request.files.items():
            # Process each file (e.g., save to a directory)
            file_name = secure_filename(file.filename)
            unique_filename = generate_unique_filename(destination, file_name)
            file.save(f'{destination}/{unique_filename}')
            uploaded_files.append(unique_filename)
            # Pass the data to the `save_post` function

        features = {
            'comfort': {
                'sunroof': form.comfort_interior.sunroof.data,
                'trimming': form.comfort_interior.trimming.data,
                'heated_seats': form.comfort_interior.heated_seats.data,
                'sound_system': form.comfort_interior.sound_system.data,
                'power_windows': form.comfort_interior.power_windows.data,
                'seat_material': form.comfort_interior.seat_material.data,
                'air_conditioning': form.comfort_interior.air_conditioning.data,
                'powered_tailgate': form.comfort_interior.powered_tailgate.data,
                'phone_connectivity': form.comfort_interior.phone_connectivity.data,
                # This is now the broader smartphone integration
                'auto_start_stop': form.comfort_interior.auto_start_stop.data,
                'ventilated_seats': form.comfort_interior.ventilated_seats.data,
                'memory_seats': form.comfort_interior.memory_seats.data,
                'power_adjustable_seats': form.comfort_interior.power_adjustable_seats.data,
                'dual_zone_climate_control': form.comfort_interior.dual_zone_climate_control.data,
                'rear_air_conditioning': form.comfort_interior.rear_air_conditioning.data,
                'steering_wheel_controls': form.comfort_interior.steering_wheel_controls.data,
                'heated_steering_wheel': form.comfort_interior.heated_steering_wheel.data,
                'auto_dimming_mirrors': form.comfort_interior.auto_dimming_mirrors.data,
                'rain_sensing_wipers': form.comfort_interior.rain_sensing_wipers.data,
                'cargo_cover': form.comfort_interior.cargo_cover.data,
                'split_folding_rear_seats': form.comfort_interior.split_folding_rear_seats.data,
                'keyless_entry': form.comfort_interior.keyless_entry.data,
                'push_button_start': form.comfort_interior.push_button_start.data,
                'remote_start': form.comfort_interior.remote_start.data,
            },
            'safety': {
                'srs_air_bags': form.safety_assistance.srs_air_bags.data,
                'lane_assistance': form.safety_assistance.lane_assistance.data,
                'hill_descent_control': form.safety_assistance.hill_descent_control.data,
                'roll_stability_control': form.safety_assistance.roll_stability_control.data,
                'standard_cruise_control': form.safety_assistance.standard_cruise_control.data,
                'adaptive_cruise_control': form.safety_assistance.adaptive_cruise_control.data,
                'antilock_braking_system': form.safety_assistance.antilock_braking_system.data,
                'emergency_braking_assist': form.safety_assistance.emergency_braking_assist.data,
                'immobilizer_and_anti_theft': form.safety_assistance.immobilizer_and_anti_theft.data,
                'electronic_stability_control': form.safety_assistance.electronic_stability_control.data,
                'rear_view_camera': form.safety_assistance.rear_view_camera.data,
                'parking_sensors_front': form.safety_assistance.parking_sensors_front.data,
                'parking_sensors_rear': form.safety_assistance.parking_sensors_rear.data,
                'camera_360': form.safety_assistance.camera_360.data,  # Adjusted field name
                'blind_spot_monitoring': form.safety_assistance.blind_spot_monitoring.data,
                'rear_cross_traffic_alert': form.safety_assistance.rear_cross_traffic_alert.data,
                'driver_attention_alert': form.safety_assistance.driver_attention_alert.data,
                'traffic_sign_recognition': form.safety_assistance.traffic_sign_recognition.data,
                'automatic_high_beams': form.safety_assistance.automatic_high_beams.data,
                'tire_pressure_monitoring': form.safety_assistance.tire_pressure_monitoring.data,
            },
            'infotainment': {
                'navigation_system': form.infotainment.navigation_system.data,
                'bluetooth_connectivity': form.infotainment.bluetooth_connectivity.data,
                'usb_ports': form.infotainment.usb_ports.data,
                'wireless_charging': form.infotainment.wireless_charging.data,
                'wi_fi_hotspot': form.infotainment.wi_fi_hotspot.data,
            },
            'exterior': {
                'led_headlights': form.exterior.led_headlights.data,
                'alloy_wheels': form.exterior.alloy_wheels.data,
                'roof_rails': form.exterior.roof_rails.data,
                'spoiler': form.exterior.spoiler.data,
                'paint_color': form.exterior.paint_color.data,
                'exterior_color_metallic': form.exterior.exterior_color_metallic.data,
            },
            'performance': {
                'sport_suspension': form.performance.sport_suspension.data,
                'selectable_drive_modes': form.performance.selectable_drive_modes.data,
                'paddle_shifters': form.performance.paddle_shifters.data,
            }
        }

        extras = json.dumps(features)  # Serialize the dictionary to JSON

        content = {
            'brand': form.vehicle_specs.brand.data,
            'vehicle_type': form.vehicle_specs.vehicle_type.data,
            'model_year': form.vehicle_specs.model_year.data,
            'engine_rating': form.vehicle_specs.engine_rating.data,
            'fuel': form.vehicle_specs.fuel.data,
            'transmission': form.vehicle_specs.transmission.data,
            'drive_type': form.vehicle_specs.drive_type.data,
            'extra_features': extras,
            'availability': form.vehicle_specs.availability.data,
            'condition': form.vehicle_specs.condition.data,
            'model': form.vehicle_specs.model.data
        }

        if form.ai.data:
            description = getai(content)
        else:
            description = form.description.data

        save_post(
            img_url=f"{uploaded_files}",
            brand=form.vehicle_specs.brand.data,
            vehicle_type=form.vehicle_specs.vehicle_type.data,
            model_year=form.vehicle_specs.model_year.data,
            engine_rating=form.vehicle_specs.engine_rating.data,
            price=form.vehicle_specs.price.data,
            fuel=form.vehicle_specs.fuel.data,
            transmission=form.vehicle_specs.transmission.data,
            mileage=form.vehicle_specs.mileage.data,
            drive_type=form.vehicle_specs.drive_type.data,
            folder=f"/static/assets/cars/{new_name}",
            extras=extras,
            description=f"{description}",
            availability=form.vehicle_specs.availability.data,
            condition=form.vehicle_specs.condition.data,
            user_id=current_user.id,
            title=f"{form.vehicle_specs.model.data}"
            # Combine brand and model for the title, accessed via vehicle_specs
        )

        # Check if the request was an AJAX call from Dropzone
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # For Dropzone, return a success JSON response
            return jsonify({'status': 'success', 'message': 'Post created successfully!'}), 200
        else:
            # For a standard form submission, flash a message and redirect
            flash("Post created successfully!", "success")
            return redirect(url_for('upload'))

    # This block runs if the form is loaded via GET or if validation fails on POST
    else:
        # If validation fails on an AJAX request, return the errors as JSON
        if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return a 400 Bad Request status with the form errors
            return jsonify({'status': 'error', 'errors': form.errors}), 400

    return render_template('upload.html', form=form)


@app.route("/upload2", methods=["GET", "POST"])
@login_required
@admin_only
def upload2():
    form = CreatePostForm()
    if request.method == 'POST':
        file = request.files.get("file")
        extension = os.path.splitext(file.filename)[-1]
        if not file:
            make_response(jsonify(message="File not detected"), 400)

        dz_uuid = request.form.get("dzuuid")
        # if not dz_uuid:
        #     # Assume this file has not been chunked
        #     with open(storage_path / f"{uuid.uuid4()}_{secure_filename(file.filename)}", "wb") as f:
        #         file.save(f)
        #     return "File Saved"

        # Chunked download
        try:
            current_chunk = int(request.form["dzchunkindex"])
            total_chunks = int(request.form["dztotalchunkcount"])
            print(total_chunks)
        except KeyError as err:
            return f"Not all required fields supplied, missing {err}"
        except ValueError:
            return f"Values provided were not in expected format"

        save_dir = f"/static/chunks/{dz_uuid}/"

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Save the individual chunk
        with open(save_dir + str(request.form["dzchunkindex"]), "wb") as f:
            file.save(f)

        # See if we have all the chunks downloaded
        # with lock:
        #     chucks[dz_uuid].append(current_chunk)
        #     completed = len(chucks[dz_uuid]) == total_chunks

        file_count = sum(len(files) for _, _, files in os.walk(save_dir))
        # Concat all the files into the final file when all are downloaded
        s = f"{dz_uuid}{extension}"
        if file_count == total_chunks:
            with open(s, "wb") as f:
                for file_number in range(total_chunks):
                    f.write(Path(save_dir + str(file_number)).read_bytes())
            print(f"{file.filename} has been uploaded")
            shutil.rmtree(save_dir)
            is_image = False

            # Now to check if the file is a video file or image file and make thumbnails
            if os.path.splitext(s)[-1].upper() in image_file_types:
                is_image = True

            if is_image:
                # This is purely for image type posts
                destination = f"static/assets/img/new_folder/"
                if not os.path.exists(destination):
                    os.makedirs(destination)

                new_name = datetime.now().strftime("%m%d%S%f") + os.path.splitext(file.filename)[-1]
                image_file = os.path.join(destination, new_name)
                os.rename(s, image_file)

                image = Image.open(image_file)
                img_resize = image.resize((417, 597))
                img_resize.save(image_file)

                save_post(img_url=image_file, title=file.filename)
                flash("Files Uploaded Successfully!")
                return redirect(url_for('upload'))
    return render_template("upload.html", form=form)


@app.route("/edit-profile/<int:index>", methods=["GET", "POST"])
@admin_only
def edit_profile(index):
    form = EditProfileForm()
    if current_user.id != index:
        abort(403)  # Restrict to admins
    profile = Users.query.get_or_404(index)

    # Populate form fields for GET requests
    if request.method == 'GET':
        form.name.data = profile.name
        form.phone_number.data = profile.phone

    if form.validate_on_submit():
        profile.name = form.name.data
        profile.phone = form.phone_number.data
        db.session.commit()  # Save changes to the database
        return redirect(url_for('home'))

    return render_template("edit_profile.html", form=form, user=profile)


# This route is for editing a blog post thumbnail, title etc.
@app.route("/edit-post/<int:index>", methods=["GET", "POST"])
@admin_only
def edit(index):
    form = PostEditForm()
    vehicle = Catalogue.query.get_or_404(index)
    try:
        page = int(request.args.get('page', '1'))
    except ValueError:
        page = 1
        print("The value error exception occurred on edit")

    if page is None:
        page = 1

    # Extract image URLs and paths
    folder = vehicle.folder_name
    urls = [url.strip().strip("'") for url in vehicle.img_url.strip("[]").split(",")]
    images = [f"{folder}/{url}" for url in urls]
    print(images)

    # Populate form fields for GET requests
    if request.method == 'GET':
        # Populate Vehicle Specifications sub-form
        form.vehicle_specs.brand.data = vehicle.brand
        form.vehicle_specs.model.data = vehicle.title  # Model is title in Catalogue
        form.vehicle_specs.vehicle_type.data = vehicle.vehicle_type
        form.vehicle_specs.model_year.data = vehicle.model_year
        form.vehicle_specs.engine_rating.data = vehicle.engine_rating
        form.vehicle_specs.price.data = vehicle.price
        form.vehicle_specs.mileage.data = vehicle.mileage
        form.vehicle_specs.fuel.data = vehicle.fuel
        form.vehicle_specs.transmission.data = vehicle.transmission
        form.vehicle_specs.drive_type.data = vehicle.drive_type
        form.vehicle_specs.availability.data = vehicle.availability
        form.vehicle_specs.condition.data = vehicle.condition or 'Foreign-used'

        # Populate description fields (direct on form)
        form.description.data = vehicle.description or 'N/A'
        # Assuming vehicle.ai exists or defaults to False
        # If 'ai' is not stored in DB, it will always be unchecked unless default is set in form.
        # form.ai.data = vehicle.ai # Uncomment if 'ai' status is stored in Catalogue

        if vehicle.extras:
            try:
                features = json.loads(vehicle.extras)

                # Populate Comfort & Interior Features
                if 'comfort' in features:  # Updated key name
                    form.comfort_interior.sunroof.data = features['comfort'].get('sunroof')
                    form.comfort_interior.trimming.data = features['comfort'].get('trimming')
                    form.comfort_interior.heated_seats.data = features['comfort'].get('heated_seats')
                    form.comfort_interior.sound_system.data = features['comfort'].get('sound_system')
                    form.comfort_interior.power_windows.data = features['comfort'].get('power_windows')
                    form.comfort_interior.seat_material.data = features['comfort'].get('seat_material')
                    form.comfort_interior.air_conditioning.data = features['comfort'].get('air_conditioning')
                    form.comfort_interior.powered_tailgate.data = features['comfort'].get('powered_tailgate')
                    form.comfort_interior.phone_connectivity.data = features['comfort'].get(
                        'phone_connectivity')
                    form.comfort_interior.auto_start_stop.data = features['comfort'].get('auto_start_stop')
                    form.comfort_interior.ventilated_seats.data = features['comfort'].get('ventilated_seats')
                    form.comfort_interior.memory_seats.data = features['comfort'].get('memory_seats')
                    form.comfort_interior.power_adjustable_seats.data = features['comfort'].get(
                        'power_adjustable_seats')
                    form.comfort_interior.dual_zone_climate_control.data = features['comfort'].get(
                        'dual_zone_climate_control')
                    form.comfort_interior.rear_air_conditioning.data = features['comfort'].get(
                        'rear_air_conditioning')
                    form.comfort_interior.steering_wheel_controls.data = features['comfort'].get(
                        'steering_wheel_controls')
                    form.comfort_interior.heated_steering_wheel.data = features['comfort'].get(
                        'heated_steering_wheel')
                    form.comfort_interior.auto_dimming_mirrors.data = features['comfort'].get(
                        'auto_dimming_mirrors')
                    form.comfort_interior.rain_sensing_wipers.data = features['comfort'].get(
                        'rain_sensing_wipers')
                    form.comfort_interior.cargo_cover.data = features['comfort'].get('cargo_cover')
                    form.comfort_interior.split_folding_rear_seats.data = features['comfort'].get(
                        'split_folding_rear_seats')
                    form.comfort_interior.keyless_entry.data = features['comfort'].get('keyless_entry')
                    form.comfort_interior.push_button_start.data = features['comfort'].get('push_button_start')
                    form.comfort_interior.remote_start.data = features['comfort'].get('remote_start')

                # Populate Safety & Driver Assistance
                if 'safety' in features:  # Updated key name
                    form.safety_assistance.srs_air_bags.data = features['safety'].get('srs_air_bags')
                    form.safety_assistance.lane_assistance.data = features['safety'].get('lane_assistance')
                    form.safety_assistance.hill_descent_control.data = features['safety'].get(
                        'hill_descent_control')
                    form.safety_assistance.roll_stability_control.data = features['safety'].get(
                        'roll_stability_control')
                    form.safety_assistance.standard_cruise_control.data = features['safety'].get(
                        'standard_cruise_control')
                    form.safety_assistance.adaptive_cruise_control.data = features['safety'].get(
                        'adaptive_cruise_control')
                    form.safety_assistance.antilock_braking_system.data = features['safety'].get(
                        'antilock_braking_system')
                    form.safety_assistance.emergency_braking_assist.data = features['safety'].get(
                        'emergency_braking_assist')
                    form.safety_assistance.immobilizer_and_anti_theft.data = features['safety'].get(
                        'immobilizer_and_anti_theft')
                    form.safety_assistance.electronic_stability_control.data = features['safety'].get(
                        'electronic_stability_control')
                    form.safety_assistance.rear_view_camera.data = features['safety'].get('rear_view_camera')
                    form.safety_assistance.parking_sensors_front.data = features['safety'].get(
                        'parking_sensors_front')
                    form.safety_assistance.parking_sensors_rear.data = features['safety'].get(
                        'parking_sensors_rear')
                    form.safety_assistance.camera_360.data = features['safety'].get('camera_360')
                    form.safety_assistance.blind_spot_monitoring.data = features['safety'].get(
                        'blind_spot_monitoring')
                    form.safety_assistance.rear_cross_traffic_alert.data = features['safety'].get(
                        'rear_cross_traffic_alert')
                    form.safety_assistance.driver_attention_alert.data = features['safety'].get(
                        'driver_attention_alert')
                    form.safety_assistance.traffic_sign_recognition.data = features['safety'].get(
                        'traffic_sign_recognition')
                    form.safety_assistance.automatic_high_beams.data = features['safety'].get(
                        'automatic_high_beams')
                    form.safety_assistance.tire_pressure_monitoring.data = features['safety'].get(
                        'tire_pressure_monitoring')

                # Populate Infotainment Features (NEW)
                if 'infotainment' in features:
                    form.infotainment.navigation_system.data = features['infotainment'].get('navigation_system')
                    form.infotainment.bluetooth_connectivity.data = features['infotainment'].get(
                        'bluetooth_connectivity')
                    form.infotainment.usb_ports.data = features['infotainment'].get('usb_ports')
                    form.infotainment.wireless_charging.data = features['infotainment'].get('wireless_charging')
                    form.infotainment.wi_fi_hotspot.data = features['infotainment'].get('wi_fi_hotspot')

                # Populate Exterior Features (NEW)
                if 'exterior' in features:
                    form.exterior.led_headlights.data = features['exterior'].get('led_headlights')
                    form.exterior.alloy_wheels.data = features['exterior'].get('alloy_wheels')
                    form.exterior.roof_rails.data = features['exterior'].get('roof_rails')
                    form.exterior.spoiler.data = features['exterior'].get('spoiler')
                    form.exterior.paint_color.data = features['exterior'].get('paint_color')
                    form.exterior.exterior_color_metallic.data = features['exterior'].get('exterior_color_metallic')

                # Populate Performance Features (NEW)
                if 'performance' in features:
                    form.performance.sport_suspension.data = features['performance'].get('sport_suspension')
                    form.performance.selectable_drive_modes.data = features['performance'].get('selectable_drive_modes')
                    form.performance.paddle_shifters.data = features['performance'].get('paddle_shifters')

            except json.JSONDecodeError:
                flash("Error loading existing features.", "warning")

    if form.validate_on_submit():
        profile = Users.query.get_or_404(current_user.id)

        if profile.edits:
            profile.edits += 1
        else:
            profile.edits = 1

        # Update vehicle details from vehicle_specs sub-form
        vehicle.brand = form.vehicle_specs.brand.data
        vehicle.vehicle_type = form.vehicle_specs.vehicle_type.data
        vehicle.model_year = form.vehicle_specs.model_year.data
        vehicle.engine_rating = form.vehicle_specs.engine_rating.data
        vehicle.price = form.vehicle_specs.price.data
        vehicle.mileage = form.vehicle_specs.mileage.data
        vehicle.fuel = form.vehicle_specs.fuel.data
        vehicle.transmission = form.vehicle_specs.transmission.data
        vehicle.drive_type = form.vehicle_specs.drive_type.data
        vehicle.availability = form.vehicle_specs.availability.data
        vehicle.condition = form.vehicle_specs.condition.data
        vehicle.title = form.vehicle_specs.model.data  # Update title from model data

        # Update description and AI flag (direct on form)
        vehicle.description = form.description.data
        # You might want to save form.ai.data to vehicle.ai if you have such a field in your model

        if form.stock.data == "sold":
            vehicle.sold = True
            vehicle.reserved = False  # Ensure reserved is false if sold
        elif form.stock.data == "reserved":
            vehicle.reserved = True
            vehicle.sold = False  # Ensure sold is false if reserved
        else:  # "available" or any other value
            vehicle.reserved = False
            vehicle.sold = False

        # Construct the features dictionary from all sub-forms for serialization
        features = {
            'comfort': {
                'sunroof': form.comfort_interior.sunroof.data,
                'trimming': form.comfort_interior.trimming.data,
                'heated_seats': form.comfort_interior.heated_seats.data,
                'sound_system': form.comfort_interior.sound_system.data,
                'power_windows': form.comfort_interior.power_windows.data,
                'seat_material': form.comfort_interior.seat_material.data,
                'air_conditioning': form.comfort_interior.air_conditioning.data,
                'powered_tailgate': form.comfort_interior.powered_tailgate.data,
                'phone_connectivity': form.comfort_interior.phone_connectivity.data,
                'auto_start_stop': form.comfort_interior.auto_start_stop.data,
                'ventilated_seats': form.comfort_interior.ventilated_seats.data,
                'memory_seats': form.comfort_interior.memory_seats.data,
                'power_adjustable_seats': form.comfort_interior.power_adjustable_seats.data,
                'dual_zone_climate_control': form.comfort_interior.dual_zone_climate_control.data,
                'rear_air_conditioning': form.comfort_interior.rear_air_conditioning.data,
                'steering_wheel_controls': form.comfort_interior.steering_wheel_controls.data,
                'heated_steering_wheel': form.comfort_interior.heated_steering_wheel.data,
                'auto_dimming_mirrors': form.comfort_interior.auto_dimming_mirrors.data,
                'rain_sensing_wipers': form.comfort_interior.rain_sensing_wipers.data,
                'cargo_cover': form.comfort_interior.cargo_cover.data,
                'split_folding_rear_seats': form.comfort_interior.split_folding_rear_seats.data,
                'keyless_entry': form.comfort_interior.keyless_entry.data,
                'push_button_start': form.comfort_interior.push_button_start.data,
                'remote_start': form.comfort_interior.remote_start.data,
            },
            'safety_assistance': {
                'srs_air_bags': form.safety_assistance.srs_air_bags.data,
                'lane_assistance': form.safety_assistance.lane_assistance.data,
                'hill_descent_control': form.safety_assistance.hill_descent_control.data,
                'roll_stability_control': form.safety_assistance.roll_stability_control.data,
                'standard_cruise_control': form.safety_assistance.standard_cruise_control.data,
                'adaptive_cruise_control': form.safety_assistance.adaptive_cruise_control.data,
                'antilock_braking_system': form.safety_assistance.antilock_braking_system.data,
                'emergency_braking_assist': form.safety_assistance.emergency_braking_assist.data,
                'immobilizer_and_anti_theft': form.safety_assistance.immobilizer_and_anti_theft.data,
                'electronic_stability_control': form.safety_assistance.electronic_stability_control.data,
                'rear_view_camera': form.safety_assistance.rear_view_camera.data,
                'parking_sensors_front': form.safety_assistance.parking_sensors_front.data,
                'parking_sensors_rear': form.safety_assistance.parking_sensors_rear.data,
                'camera_360': form.safety_assistance.camera_360.data,
                'blind_spot_monitoring': form.safety_assistance.blind_spot_monitoring.data,
                'rear_cross_traffic_alert': form.safety_assistance.rear_cross_traffic_alert.data,
                'driver_attention_alert': form.safety_assistance.driver_attention_alert.data,
                'traffic_sign_recognition': form.safety_assistance.traffic_sign_recognition.data,
                'automatic_high_beams': form.safety_assistance.automatic_high_beams.data,
                'tire_pressure_monitoring': form.safety_assistance.tire_pressure_monitoring.data,
            },
            'infotainment': {
                'navigation_system': form.infotainment.navigation_system.data,
                'bluetooth_connectivity': form.infotainment.bluetooth_connectivity.data,
                'usb_ports': form.infotainment.usb_ports.data,
                'wireless_charging': form.infotainment.wireless_charging.data,
                'wi_fi_hotspot': form.infotainment.wi_fi_hotspot.data,
            },
            'exterior': {
                'led_headlights': form.exterior.led_headlights.data,
                'alloy_wheels': form.exterior.alloy_wheels.data,
                'roof_rails': form.exterior.roof_rails.data,
                'spoiler': form.exterior.spoiler.data,
                'paint_color': form.exterior.paint_color.data,
                'exterior_color_metallic': form.exterior.exterior_color_metallic.data,
            },
            'performance': {
                'sport_suspension': form.performance.sport_suspension.data,
                'selectable_drive_modes': form.performance.selectable_drive_modes.data,
                'paddle_shifters': form.performance.paddle_shifters.data,
            }
        }

        vehicle.extras = json.dumps(features)  # Serialize the dictionary to JSON

        # Update 'content' for getai function if needed
        content = {
            'brand': form.vehicle_specs.brand.data,
            'vehicle_type': form.vehicle_specs.vehicle_type.data,
            'model_year': form.vehicle_specs.model_year.data,
            'engine_rating': form.vehicle_specs.engine_rating.data,
            'fuel': form.vehicle_specs.fuel.data,
            'transmission': form.vehicle_specs.transmission.data,
            'mileage': form.vehicle_specs.mileage.data,
            'drive_type': form.vehicle_specs.drive_type.data,
            'extra_features': features,  # Pass the dictionary, not the JSON string, if getai expects it
            'availability': form.vehicle_specs.availability.data,
            'condition': form.vehicle_specs.condition.data,
            'model': form.vehicle_specs.model.data  # Using model data for the model field
        }

        if form.ai.data:
            description = getai(content)
        else:
            description = form.description.data

        vehicle.description = description

        # Process thumbnail assignment first
        thumbnail_image_id = request.form.get("thumbnail_image")  # Thumbnail index (optional)
        thumbnail = None
        if thumbnail_image_id:
            thumbnail_idx = int(thumbnail_image_id)
            if thumbnail_idx < len(urls):  # Ensure index is valid
                thumbnail = urls[thumbnail_idx]

        # Process image deletion
        selected_images = request.form.getlist('delete_images')  # Image indices to delete
        if selected_images:
            selected_indices = list(map(int, selected_images))  # Convert indices to integers
            for idx in selected_indices:
                try:
                    os.remove(f"core/{images[idx]}")  # Remove physical file
                    print(f"Deleting {images[idx]}")
                except FileNotFoundError:
                    print(f"File {images[idx]} not found.")
            # Remove URLs from the list in reverse order to prevent index shifting
            for idx in sorted(selected_indices, reverse=True):
                del urls[idx]

        # Move the thumbnail to the front if it's valid and not marked for deletion
        if thumbnail and thumbnail not in urls:
            flash("Thumbnail cannot be set as it has been deleted.", "warning")
        elif thumbnail and thumbnail in urls:
            urls.remove(thumbnail)
            urls.insert(0, thumbnail)

        # Process new file uploads
        if form.file.data and any(file.filename for file in form.file.data):
            for file in form.file.data:
                if file.filename:  # Only process files with a valid filename
                    file_name = secure_filename(file.filename)
                    unique_filename = generate_unique_filename(f"core/{folder}", file_name)
                    file_path = f'core/{folder.strip("/")}/{unique_filename}'
                    file.save(file_path)
                    urls.append(unique_filename)

        # Update vehicle image URLs
        vehicle.img_url = f"[{', '.join(urls)}]"

        if not vehicle.user_id:
            vehicle.user_id = current_user.id

        db.session.commit()  # Save changes to the database
        return redirect(url_for('blog', page=page))  # Redirect after successful update

    return render_template('edit.html', csrf_token=generate_csrf(), images=images, form=form, vehicle=vehicle)


@app.route("/update-image-order", methods=["POST"])
@admin_only
def update_image_order():
    index = request.form.get('index')
    print(index)
    vehicle = Catalogue.query.get_or_404(index)
    new_order = request.form.getlist('order[]')  # This will now correctly receive the data

    if new_order:
        print(new_order)
        urls = [img_url.split('/')[-1] for img_url in new_order]
        vehicle.img_url = f"[{', '.join(urls)}]"
        db.session.commit()
        # print(f"[{', '.join(urls)}]")
        # print(urls)

        # Re-render the image preview section
        folder = vehicle.folder_name
        urls = [url.strip().strip("'") for url in vehicle.img_url.strip("[]").split(",")]
        images = [f"{folder}/{url}" for url in urls]
        return render_template('_image_preview.html', csrf_token=generate_csrf(), images=images, vehicle=vehicle)
    else:
        return render_template('_error_message.html', error="No image order received."), 400


# if edit_form.validate_on_submit():
#     img_to_remove = request.args.get("img_to_remove")
#     file = edit_form.file.data
#
#     # This filters any non-image file types
#     try:
#         file.save(file.filename)
#         image = Image.open(file.filename)
#         img_resize = image.resize((417, 597))
#         img_resize.save(file.filename)
#
#     except UnidentifiedImageError:
#         os.remove(file.filename)
#         flash("That's not an image file!")
#         return redirect(url_for('edit', index=index))
#
#     # This moves the uploaded file to the videos folder from the project root
#
#     destination = f"static/assets/videos/"
#     try:
#         shutil.move(file.filename, destination)
#     except shutil.Error:
#         os.remove(file.filename)
#         flash("That file already exists")
#         return redirect(url_for('edit', index=index))
#     else:
#         image_file = destination + file.filename
#
#     # This removes the original image after successfully moving the new file
#     try:
#         if img_to_remove != image_file:
#             os.remove(img_to_remove)
#     except FileNotFoundError:
#         pass
#     except TypeError:
#         pass
#     flash("Files Uploaded Successfully!")
#
#     # now to effect these changes in the database
#     vehicle.img_url = image_file
#     db.session.commit()
#     return redirect(url_for('home'))
# return render_template("edit.html", form=edit_form)


@app.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)


@app.route("/admin")
@login_required
@super_admin_only
def admin():
    users = Users.query.all()
    return render_template("admin.html", admin_list=admin_list, csrf=generate_csrf(), users=users)


@app.route('/toggle-admin', methods=['POST'])
@super_admin_only
def toggle_admin():
    # Parse data from the form
    user_id = request.form.get('user_id')
    is_admin = request.form.get('is_admin') == 'true'

    # Fetch the user and toggle admin status
    user = Users.query.get_or_404(user_id)
    user.is_admin = is_admin
    db.session.commit()
    status = not user.is_admin
    # Return a partial HTML snippet with the updated checkbox state
    return render_template("update-admin.html", id=user.id, admin=status)


@app.route('/confirm-delete-user/<int:user_id>')
@super_admin_only
def confirm_delete_user(user_id):
    user = Users.query.get_or_404(user_id)
    if not current_user.is_admin:
        abort(403)  # Restrict to admins
    return render_template('confirm_delete_user.html', csrf=generate_csrf(), user=user)


@app.route('/delete-user/<int:user_id>', methods=['DELETE'])
@super_admin_only
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)  # Only admins can delete users
    default_user_id = 47
    user = Users.query.get_or_404(user_id)
    name = user.name
    # Reassign all orphaned posts to the default user
    posts = Catalogue.query.filter_by(user_id=user_id).all()
    for post in posts:
        post.user_id = default_user_id

    db.session.delete(user)
    db.session.commit()
    flash(f"User: {name}'s record has been deleted ")
    return '', 200  # HTMX expects an empty response


# Register route gets user data from form and saves to database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        user = Users()
        user.name = request.form.get("name")
        user.phone = request.form.get("phone_number")
        user.email = request.form.get("email").lower()
        user.created_on = datetime.now()
        password = request.form.get("password")
        confirmed_pass = request.form.get("confirm")
        if password != confirmed_pass:
            flash("passwords do not much")
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password, salt_length=5)
        user.password = hashed_password
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            flash('User already exists! Try logging in instead')
            return redirect(url_for('login'))
        token = generate_token(user.email)
        confirm_url = url_for("confirm_email", token=token, _external=True)
        html = render_template("email.html", confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)
        flash("successfully registered")
        login_user(user)
        return redirect(url_for("auth"))
    return render_template("register.html", form=form)


# Route to give email auth page
@app.route('/auth2')
def auth():
    return render_template("email-auth.html")


# Login to the website account for user
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("password")
        try:
            user = db.session.query(Users).filter_by(email=user_email).first()
            pwhash = user.password
            check = check_password_hash(pwhash, user_password)

        except AttributeError:
            flash("That email seems to not be in our database")
            return redirect(url_for('login'))

        else:
            if check:
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("That password is not correct")
                return redirect(url_for('login'))
    return render_template("login.html", form=form)


@app.route("/resend")
@login_required
def resend_confirmation():
    if current_user.is_confirmed:
        flash("Your account has already been confirmed.", "success")
        return redirect(url_for("home"))
    token = generate_token(current_user.email)
    confirm_url = url_for("confirm_email", token=token, _external=True)
    html = render_template("email.html", confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash("A new confirmation email has been sent.", "success")
    return redirect(url_for("home"))


# Log out user from their session
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# Confirm the user's email
@app.route("/confirm/<token>")
def confirm_email(token):
    email = confirm_token(token)
    user = Users.query.filter_by(email=email).first_or_404()
    if user.is_confirmed:
        flash("Account already confirmed.", "success")
        return redirect(url_for("home"))

    if user.email == email:
        user.is_confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")
    else:
        flash("The confirmation link is invalid or has expired.", "danger")
    return redirect(url_for("home"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form.get("email")
        user = db.session.query(Users).filter_by(email=email).first()
        if user is None:
            flash("That email is not registered in our database")
            return redirect(url_for('forgot'))
        else:
            token = generate_token(user.email)
            confirm_url = url_for("reset_password", token=token, _external=True)
            html = render_template("confirm_reset.html", confirm_url=confirm_url)
            subject = "Reset your password"
            send_email(user.email, subject, html)
            flash("A password reset link has been sent to your email", "success")
            return redirect(url_for("home"))
    return render_template("forgot.html", csrf_token=generate_csrf())


@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = confirm_token(token)
    reset_form = RegisterForm()
    user = Users.query.filter_by(email=email).first_or_404()
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm")
        if password != confirm_password:
            flash("passwords do not much")
            return redirect(url_for('reset_password', token=token))
        hashed_password = generate_password_hash(password, salt_length=5)
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been reset successfully")
        return redirect(url_for("login"))
    reset_form.email.data = email
    reset_form.name.data = user.name
    return render_template("reset.html", email=email, form=reset_form)
