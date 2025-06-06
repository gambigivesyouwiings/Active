from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, FileField, IntegerField, SelectField, MultipleFileField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, InputRequired, NumberRange, Regexp
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
            ('minivan', 'Minivan'),
            ('coupe', 'Coupe'),
            ('sports-car', 'Sports Car'),
            ('truck', 'Truck'),
            ('bike', 'Bike')
        ],
        default='saloon'  # Set the default selected value
    )
    model_year = IntegerField("Model year", validators=[DataRequired()])
    engine_rating = StringField("Engine rating (include cc,kW or equivalent)", id="rating", render_kw={"placeholder": "3500cc"})
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
            ('AWD', 'All Wheel Drive (AWD)'),  # Option with value 'all' and label 'All Brands'
            ('2WD', 'Two Wheel Drive (2WD)'),
            ('4WD', 'Four Wheel Drive (4WD)')
        ],
        default='AWD'  # Set the default selected value
    )
    availability = SelectField(
        'Vehicle Availability',
        choices=[
            ('local', 'Locally available'),  # Option with value 'all' and label 'All Brands'
            ('import', 'Direct Import/International Stock'),

        ],
        default='local'  # Set the default selected value
    )
    condition = SelectField(
        'Vehicle Condition',
        choices=[
            ('Foreign used', 'Foreign used'),
            ('Local used', 'Local used'),  # Option with value 'all' and label 'All Brands'
            ('New', 'New'),

        ],
        default='Foreign used'  # Set the default selected value
    )
    description = CKEditorField("Write a short description of the car, or tick box to auto-generate")
    ai = BooleanField("AI generated description")

    # Comfort Features
    sunroof = BooleanField('Sunroof')
    trimming = SelectField('Trimming', choices=[('', 'Select Trimming'), ('wood', 'Wood'), ('aluminum', 'Aluminum'),
                                                ('carbon_fiber', 'Carbon Fiber'), ('other', 'Other')])
    heated_seats = BooleanField('Heated Seats')
    sound_system = StringField('Sound System',
                               render_kw={"placeholder": "e.g., Bose, Harman Kardon, Factory Sound system"})
    power_windows = BooleanField('Power Windows')
    seat_material = SelectField('Seat Material',
                                choices=[('', 'Select Material'), ('leather', 'Leather'), ('cloth', 'Cloth'),
                                         ('vinyl', 'Vinyl'), ('suede', 'Suede'), ('alcantara', 'Alcantara')])
    air_conditioning = SelectField('Air Conditioning', choices=[('', 'Select Type'), ('single_zone', 'Single Zone'),
                                                                ('multi_zone', 'Multi Zone'),
                                                                ('automatic', 'Automatic')])
    powered_tailgate = BooleanField('Powered Tailgate')
    phone_connectivity = BooleanField('Phone Connectivity (Bluetooth, etc.)')
    auto_start_stop = BooleanField('Auto Start And Stop')

    # Safety Features
    srs_air_bags = BooleanField('SRS Air Bags')
    lane_assistance = BooleanField('Lane Assistance')
    hill_descent_control = BooleanField('Hill Descent Control')
    roll_stability_control = BooleanField('Roll Stability Control')
    standard_cruise_control = BooleanField('Standard Cruise Control')
    adaptive_cruise_control = BooleanField('Adaptive Cruise Control')
    antilock_braking_system = BooleanField('Antilock Braking System')
    emergency_braking_assist = BooleanField('Emergency Braking Assist')
    immobilizer_and_anti_theft = BooleanField('Immobilizer And Anti Theft')
    electronic_stability_control = BooleanField('Electronic Stability Control')

    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    name = StringField("Enter your name", id="brand", validators=[DataRequired()])
    email = EmailField("Enter your email address", validators=[DataRequired()])
    password = PasswordField("Enter your password", validators=[DataRequired(), Length(min=6, max=25)])
    confirm = PasswordField("Repeat password", validators=[InputRequired(), DataRequired(), EqualTo("password", message="Passwords must match.")])
    phone_number = StringField('Phone Number: This is how clients will reach you', id="model", validators=[
        DataRequired(),
        Regexp(r'^\+\d{1,15}$', message="Invalid phone number format")
    ], render_kw={"placeholder": "Format: +254123456789"})
    submit = SubmitField("Sign me Up")


class LoginForm(FlaskForm):
    email = EmailField("Enter your email address", validators=[DataRequired()])
    password = PasswordField("Enter your password", validators=[DataRequired()])
    submit = SubmitField("Sign me In")


class EditForm(FlaskForm):
    file = MultipleFileField("Add Images Here", id="fike", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif']), FileSize(max_size=16000000, message="File must be less than 16 MB!")])
    brand = StringField("Brand of the vehicle", id="brand", validators=[DataRequired()])
    model = StringField("Vehicle make/ model", id="model", validators=[DataRequired()])
    stock = SelectField(
        'Stock Availability',
        choices=[
            ('available', 'Available'),  # Option with value 'all' and label 'All Brands'
            ('reserved', 'Reserved'),
            ('sold', 'Sold')
        ],
        default='available'  # Set the default selected value
    )
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
    engine_rating = StringField("Engine rating", id="rating", render_kw={"placeholder": "3500cc"})
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
            ('AWD', 'All Wheel Drive (AWD)'),  # Option with value 'all' and label 'All Brands'
            ('2WD', 'Two Wheel Drive (2WD)'),
            ('4WD', 'Four Wheel Drive (4WD)')
        ],
        default='AWD'  # Set the default selected value
    )
    availability = SelectField(
        'Vehicle Availability',
        choices=[
            ('local', 'Locally available'),  # Option with value 'all' and label 'All Brands'
            ('import', 'Direct Import/International Stock'),

        ],
        default='local'  # Set the default selected value
    )
    condition = SelectField(
        'Vehicle Condition',
        choices=[
            ('Foreign used', 'Foreign used'),
            ('Local used', 'Local used'),  # Option with value 'all' and label 'All Brands'
            ('New', 'New'),

        ],
        default='Foreign used'  # Set the default selected value
    )
    description = CKEditorField("Write a short description of the car, or tick box to auto-generate")
    ai = BooleanField("AI generated description")

    # Comfort Features
    sunroof = BooleanField('Sunroof')
    trimming = SelectField('Trimming', choices=[('', 'Select Trimming'), ('wood', 'Wood'), ('aluminum', 'Aluminum'),
                                                ('carbon_fiber', 'Carbon Fiber'), ('other', 'Other')])
    heated_seats = BooleanField('Heated Seats')
    sound_system = StringField('Sound System',
                               render_kw={"placeholder": "e.g., Bose, Harman Kardon, Factory Sound system"})
    power_windows = BooleanField('Power Windows')
    seat_material = SelectField('Seat Material',
                                choices=[('', 'Select Material'), ('leather', 'Leather'), ('cloth', 'Cloth'),
                                         ('vinyl', 'Vinyl'), ('suede', 'Suede'), ('alcantara', 'Alcantara')])
    air_conditioning = SelectField('Air Conditioning', choices=[('', 'Select Type'), ('single_zone', 'Single Zone'),
                                                                ('multi_zone', 'Multi Zone'),
                                                                ('automatic', 'Automatic')])
    powered_tailgate = BooleanField('Powered Tailgate')
    phone_connectivity = BooleanField('Phone Connectivity (Bluetooth, etc.)')
    auto_start_stop = BooleanField('Auto Start And Stop')

    # Safety Features
    srs_air_bags = BooleanField('SRS Air Bags')
    lane_assistance = BooleanField('Lane Assistance')
    hill_descent_control = BooleanField('Hill Descent Control')
    roll_stability_control = BooleanField('Roll Stability Control')
    standard_cruise_control = BooleanField('Standard Cruise Control')
    adaptive_cruise_control = BooleanField('Adaptive Cruise Control')
    antilock_braking_system = BooleanField('Antilock Braking System')
    emergency_braking_assist = BooleanField('Emergency Braking Assist')
    immobilizer_and_anti_theft = BooleanField('Immobilizer And Anti Theft')
    electronic_stability_control = BooleanField('Electronic Stability Control')

    submit = SubmitField("Submit Post")


class EditProfileForm(FlaskForm):
    name = StringField("Enter your name", id="brand", validators=[DataRequired()])
    phone_number = StringField('Phone Number: This is how clients will reach you. N/B: Format - +254123456789', id="model", validators=[
        DataRequired(),
        Regexp(r'^\+\d{1,15}$', message="Invalid phone number format")
    ])
    submit = SubmitField("Update Profile")