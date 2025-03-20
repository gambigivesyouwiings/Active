from flask import Flask, render_template, request, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
from flask_wtf.csrf import CSRFProtect

# Create the Flask app instance
app = Flask(__name__)

# Load configuration from DevelopmentConfig
app.config.from_object(DevelopmentConfig)

# Initialize SQLAlchemy with the app instance
db = SQLAlchemy(app)

# Initialize Flask-Migrate with the app instance and database
migrate = Migrate(app, db)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
CORS(app)
Bootstrap(app)
dropzone = Dropzone(app)
csrf = CSRFProtect(app)

admin_list = ["gambikimathi@students.uonbi.ac.ke", "chadkirubi@gmail.com", "njengashwn@gmail.com"]


# This function sends mail to end-users with the Flask-Mail module
def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_USERNAME']
    )
    mail.send(msg)


# This function generates a unique token that is used for user account authentication
def generate_token(email):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])


# This function checks the token and returns the associated email address.
def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=expiration
        )
        return email
    except Exception:
        return False

# Import routes to register them with the app

from core import routes
