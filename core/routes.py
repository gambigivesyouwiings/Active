from flask import render_template, request, abort, redirect, url_for, flash, make_response, jsonify
from flask_wtf.csrf import CSRFError, generate_csrf
from core import app, db, login_manager, send_email, generate_token, confirm_token
from core.models import Catalogue, Users
from core.forms import CreatePostForm, RegisterForm, LoginForm
import time
from sqlalchemy.exc import IntegrityError, ProgrammingError
from functools import wraps
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import shutil
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename



def create_app():
    with app.app_context():
        db.create_all()


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


image_file_types = ['.webp', '.svg', '.png', '.avif', '.jpg', '.jpeg', '.jfif', '.jpe', '.pjp', '.gif', '.apn']

admin_list = ["gambikimathi@students.uonbi.ac.ke", "chadkirubi@gmail.com", "njengashwn@gmail.com"]


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
        if current_user.email not in admin_list:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


@app.before_request
def redirect_to_www():
    if request.host == "mushroommotors.com":
        return redirect(f"https://www.mushroommotors.com", code=301)


@app.route("/")
def home():
    return render_template("index.html", csrf_token=generate_csrf())


@app.route("/contact_us", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        send_email(to="gambikimathi@gmail.com", subject=subject, template=f"<div><p>You have a message from: {name} {email}</p><br><p>{message}</p></div>")
        # if email != "":
        #     flash("Your message has been sent. Thank you!")
        print(email)
    return render_template("contact.html", csrf_token=generate_csrf())


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


@app.route('/vehicles', methods=['OPTIONS'])
def handle_options():
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.route("/vehicles", methods=["GET", "POST"])
def blog():
    unique_brands = db.session.query(Catalogue.brand).distinct().all()
    unique = [category[0] for category in unique_brands]
    # Get the page number from the query string
    page = int(request.args.get('page', 1))
    per_page = 10  # Number of items per page

    if request.method == "POST":
        # Get JSON data from the request
        form_data = request.get_json()

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

        if form_data.get('price') and len(form_data['price']) > 0:
            price_ranges = form_data['price']
            for price_range in price_ranges:
                try:
                    if price_range == "Above 10M":
                        query = query.filter(Catalogue.price > 10000000)

                    else:
                        min_price, max_price = map(
                            lambda x: int(x.replace('K', '000').replace('M', '000000').strip()),
                            price_range.split('-')
                        )
                        query = query.filter(Catalogue.price >= min_price, Catalogue.price <= max_price)

                except ValueError:
                    print("error detected")
                    continue  # Ignore invalid price formats
        if form_data.get('availability'):
            availability = form_data['availability'].strip()
            if availability == "local":
                query = query.filter(Catalogue.availability == "local")
            elif availability == "import":
                query = query.filter(Catalogue.availability == "import")
            # For 'all', no additional filtering is applied

        # Execute the query and return the results
        query = query.order_by(Catalogue.model_year)

        # Paginate the query results
        vehicles = query.paginate(page=page, per_page=per_page)
        return render_template("filter_vehicles.html", pages=vehicles)

    pages = db.paginate(db.select(Catalogue).order_by(Catalogue.model_year), page=page, per_page=per_page)
    return render_template("blog.html", pages=pages, brands=unique, csrf_token=generate_csrf())


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
            path = folder + "/" + url.strip().strip("'")
            images.append(path)

    number = int(post.price)
    price = f"{number:,}"

    return render_template("blog-details.html", images=images, post=post, price=price)


@app.route('/search')
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
        print(results)
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
    return render_template("delete.html", id=index)


@app.route("/delete/<int:post_id>", methods=["GET", "POST"])
@admin_only
def delete(post_id):
    blog_to_delete = db.session.query(Catalogue).filter_by(id=post_id).first()
    if blog_to_delete.img_url:
        try:
            os.remove(blog_to_delete.img_url)
        except FileNotFoundError:
            pass
    if blog_to_delete.video_url:
        try:
            os.remove(blog_to_delete.video_url)
        except FileNotFoundError:
            pass

    db.session.delete(blog_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
@admin_only
def upload():
    form = CreatePostForm()
    if request.method == 'POST':
        uploaded_files = []
        new_name = datetime.now().strftime("%Y%m%d%S%f")
        destination = os.path.join("core/static/assets/cars/", new_name)
        try:
            if not os.path.exists(destination):
                os.makedirs(destination)
                print(f"Directory created: {destination}")
        except OSError as e:
            print(f"Error creating directory: {e}")
        files = request.files.getlist(form.file)  # Fetch all uploaded files

        for file in form.file.data:
            # Process each file (e.g., save to a directory)
            print("((file")
            file_name = secure_filename(file.filename)
            file.save(f'{destination}/{file_name}')
            uploaded_files.append(file_name)
            # Pass the data to the `save_post` function
        save_post(
            img_url=f"{uploaded_files}",  # Pass the list of file paths as the image URLs
            brand=form.brand.data,
            vehicle_type=form.vehicle_type.data,
            model_year=form.model_year.data,
            engine_rating=form.engine_rating.data,
            price=form.price.data,
            fuel=form.fuel.data,
            transmission=form.transmission.data,
            mileage=form.mileage.data,
            drive_type=form.drive_type.data,
            folder=f"/static/assets/cars/{new_name}",  # Using the brand as the folder name for simplicity
            extras=form.extras.data,
            availability=form.availability.data,  # This can be extended for user input or other logic
            title=f"{form.model.data}"  # Combine brand and model for the title
            )
        flash("Post created successfully!", "success")
        return redirect(url_for('upload'))

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


# This route is for editing a blog post thumbnail, title etc.
@app.route("/edit-post/<index>", methods=["GET", "POST"])
@login_required
@admin_only
def edit(index):
    edit_form = CreatePostForm()
    blog_to_edit = db.session.query(Catalogue).filter_by(id=index).first()

    if edit_form.validate_on_submit():
        img_to_remove = request.args.get("img_to_remove")
        file = edit_form.file.data

        # This filters any non-image file types
        try:
            file.save(file.filename)
            image = Image.open(file.filename)
            img_resize = image.resize((417, 597))
            img_resize.save(file.filename)

        except UnidentifiedImageError:
            os.remove(file.filename)
            flash("That's not an image file!")
            return redirect(url_for('edit', index=index))

        # This moves the uploaded file to the videos folder from the project root

        destination = f"static/assets/videos/"
        try:
            shutil.move(file.filename, destination)
        except shutil.Error:
            os.remove(file.filename)
            flash("That file already exists")
            return redirect(url_for('edit', index=index))
        else:
            image_file = destination + file.filename

        # This removes the original image after successfully moving the new file
        try:
            if img_to_remove != image_file:
                os.remove(img_to_remove)
        except FileNotFoundError:
            pass
        except TypeError:
            pass
        flash("Files Uploaded Successfully!")

        # now to effect these changes in the database
        blog_to_edit.img_url = image_file
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=edit_form)


@app.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)


@app.route("/portfolio_det")
def portfolio_details():
    return render_template("portfolio-details.html")


# Register route gets user data from form and saves to database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        user = Users()
        user.name = request.form.get("name")
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
    return render_template("forgot.html")


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
