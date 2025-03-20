from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, FileField, IntegerField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, EqualTo, Length, InputRequired, NumberRange
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize


# WTForm for posts
class CreatePostForm(FlaskForm):
    file = MultipleFileField("Add Images Here", id="fike", validators=[FileRequired(message="Please upload a file."), FileAllowed(['jpg', 'jpeg', 'png', 'gif']), FileSize(max_size=16000000, message="File must be less than 16 MB!")])
    brand = StringField("Brand of the vehicle", id="brand", validators=[DataRequired()])
    model = StringField("Vehicle make/ model", id="model", validators=[DataRequired()])
    vehicle_type = SelectField(
        'Build-type of the vehicle',
        choices=[
            ('saloon', 'Saloon'),  # Option with value 'all' and label 'All Brands'
            ('SUV', 'SUV'),
            ('hatchback', 'Hatchback'),
            ('convertible', 'Convertible'),
            ('truck', 'Truck'),
            ('bike', 'Bike')
        ],
        default='saloon'  # Set the default selected value
    )
    model_year = IntegerField("Model year", validators=[DataRequired()])
    engine_rating = StringField("Engine rating",id="rating", render_kw={"placeholder": "3500cc"})
    price = IntegerField("Price", validators=[DataRequired()])
    mileage = IntegerField("Mileage", validators=[DataRequired(), NumberRange(max=1000000, message="Max-mileage!.")])
    fuel = SelectField(
        'Fuel Type',
        choices=[
            ('petrol', 'Petrol'),  # Option with value 'all' and label 'All Brands'
            ('diesel', 'Diesel'),
            ('hybrid', 'Hybrid'),
            ('electric', 'Electric'),
            ('hydrogen/biofuel', 'Hydrogen/Biofuel'),
        ],
        default='petrol'  # Set the default selected value
    )
    transmission = SelectField(
        'Tranmission type',
        choices=[
            ('automatic', 'Automatic'),  # Option with value 'all' and label 'All Brands'
            ('manual', 'Manual')
        ],
        default='automatic'  # Set the default selected value
    )
    drive_type = SelectField(
        'Drive-type of the vehicle',
        choices=[
            ('AWD', 'AWD'),  # Option with value 'all' and label 'All Brands'
            ('FWD', 'FWD'),
            ('RWD', 'RWD')
        ],
        default='FWD'  # Set the default selected value
    )
    availability = SelectField(
        'Vehicle Availability',
        choices=[
            ('local', 'Locally available'),  # Option with value 'all' and label 'All Brands'
            ('import', 'Direct Import/International Stock'),

        ],
        default='local'  # Set the default selected value
    )
    extras = CKEditorField("Car Description", validators=[DataRequired()])

    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    name = StringField("Enter your name", validators=[DataRequired()])
    email = EmailField("Enter your email address", validators=[DataRequired()])
    password = PasswordField("Enter your password", validators=[DataRequired(), Length(min=6, max=25)])
    confirm = PasswordField("Repeat password", validators=[InputRequired(), DataRequired(), EqualTo("password", message="Passwords must match.")])
    submit = SubmitField("Sign me Up")


class LoginForm(FlaskForm):
    email = EmailField("Enter your email address", validators=[DataRequired()])
    password = PasswordField("Enter your password", validators=[DataRequired()])
    submit = SubmitField("Sign me In")

