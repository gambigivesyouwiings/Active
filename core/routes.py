from flask import render_template, request
from core import app, db
from core.models import Catalogue
import time
from sqlalchemy.exc import IntegrityError, ProgrammingError


def create_app():
    with app.app_context():
        db.create_all()


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

    number = int(post.price)
    price = f"{number:,}"

    return render_template("blog-details.html", images=images, post=post, price=price)


@app.route('/search')
def search():
    query = request.args.get("query")
    print(query)
    if query:
        results = Catalogue.query.filter(Catalogue.title.ilike(f"%{query}%") | Catalogue.brand.ilike(f"%{query}%")).limit(10).all()
    else:
        # results = Catalogue.query.limit(20).all()
        return '<div class="p-2 hide bd-highlight" id="results"></div>'
    if results:
        print(results)
    else:
        return render_template("noresults.html")

    return render_template("search.html", results=results)


@app.route("/portfolio_det")
def portfolio_details():
    return render_template("portfolio-details.html")

