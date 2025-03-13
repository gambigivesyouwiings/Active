from flask import Flask, render_template, request, url_for, flash, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig
from flask_migrate import Migrate

# Create the Flask app instance
app = Flask(__name__)

# Load configuration from DevelopmentConfig
app.config.from_object(DevelopmentConfig)

# Initialize SQLAlchemy with the app instance
db = SQLAlchemy(app)

# Initialize Flask-Migrate with the app instance and database
migrate = Migrate(app, db)

# Import routes to register them with the app

from core import routes
