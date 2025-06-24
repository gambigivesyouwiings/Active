from .widgets import BootstrapSwitchInput
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, EmailField, TextAreaField, SubmitField, SelectField, MultipleFileField, IntegerField, BooleanField, PasswordField
from wtforms.validators import DataRequired, URL, Email, Length, NumberRange, Optional, ValidationError, InputRequired, Regexp, EqualTo
from flask_ckeditor import CKEditorField
from wtforms.fields import FormField, FieldList


# Define choices for SelectFields
VEHICLE_TYPES = [
            ('saloon', 'Saloon'), ('SUV', 'SUV'), ('hatchback', 'Hatchback'), ('convertible', 'Convertible'),
            ('minivan', 'Minivan'), ('coupe', 'Coupe'), ('sports-car', 'Sports Car'), ('truck', 'Truck'),
            ('bike', 'Bike'), ('Crossover', 'Crossover'), ('Other', 'Other')
        ]
FUEL_TYPES = [
    ('petrol', 'Petrol'), ('Diesel', 'Diesel'), ('Electric', 'Electric'),
    ('Hybrid', 'Hybrid'), ('Plug-in Hybrid', 'Plug-in Hybrid'), ('Flex Fuel', 'Flex Fuel')
]
TRANSMISSION_TYPES = [
    ('automatic', 'Automatic'), ('manual', 'Manual'), ('CVT', 'CVT'), ('Automated Manual', 'Automated Manual')
]
DRIVE_TYPES = [
            ('AWD', 'All Wheel Drive (AWD)'),
            ('2WD', 'Two Wheel Drive (2WD)'),
            ('4WD', 'Four Wheel Drive (4WD)')
        ]
AVAILABILITY_STATUS = [
            ('local', 'Locally available'),
            ('import', 'Direct Import/International Stock'),

        ]
CONDITION_TYPES = [
            ('Foreign used', 'Foreign used'),
            ('Local used', 'Local used'),
            ('New', 'New'),

        ]
SEAT_MATERIALS = [
    ('Cloth', 'Cloth'), ('Leather', 'Leather'), ('Synthetic Leather', 'Synthetic Leather'),
    ('suede', 'Suede'), ('Vinyl', 'Vinyl'), ('Alcantara', 'Alcantara'), ('Other', 'Other')
]
TRIMMING_TYPES = [
    ('Standard', 'Standard'), ('Wood Trim', 'Wood Trim'), ('Carbon Fiber', 'Carbon Fiber'),
    ('Metal Trim', 'Metal Trim'), ('Piano Black', 'Piano Black'), ('Other', 'Other')
]
AIR_CONDITIONING_TYPES = [
    ('Manual', 'Manual'), ('Automatic Climate Control', 'Automatic Climate Control'), ('Dual-Zone Automatic', 'Dual-Zone Automatic'), ('Multi-Zone Automatic', 'Multi-Zone Automatic')
]
SOUND_SYSTEM_TYPES = [
    ('Standard', 'Standard'), ('Premium', 'Premium'), ('High-End Branded', 'High-End Branded')
]
PAINT_COLORS = [
    ('White', 'White'), ('Black', 'Black'), ('Silver', 'Silver'), ('Gray', 'Gray'),
    ('Red', 'Red'), ('Blue', 'Blue'), ('Green', 'Green'), ('Yellow', 'Yellow'),
    ('Orange', 'Orange'), ('Brown', 'Brown'), ('Gold', 'Gold'), ('Beige', 'Beige'),
    ('Purple', 'Purple'), ('Other', 'Other')
]


# Nested Form Classes for better organization
class VehicleSpecificationsForm(FlaskForm):
    brand = StringField("Vehicle Brand (e.g., Toyota)", validators=[DataRequired()])
    model = StringField("Vehicle Model (e.g., Camry)", validators=[DataRequired()])
    vehicle_type = SelectField("Vehicle Type", choices=VEHICLE_TYPES, default='saloon')
    model_year = IntegerField("Model Year", validators=[DataRequired(), NumberRange(min=1900, max=2050)])
    engine_rating = StringField("Engine Rating (e.g., 2.5L I4, V6, Electric)", default="1500cc", validators=[DataRequired()], render_kw={"placeholder": "1500cc"})
    price = IntegerField("Price", validators=[DataRequired()])
    mileage = IntegerField("Mileage", validators=[Optional(), NumberRange(max=1000000, message="Max-mileage!")])
    fuel = SelectField("Fuel Type", choices=FUEL_TYPES, default='petrol')
    transmission = SelectField("Transmission Type", choices=TRANSMISSION_TYPES, default='automatic')
    drive_type = SelectField("Drive Type", choices=DRIVE_TYPES, default='AWD')
    availability = SelectField("Availability Status", choices=AVAILABILITY_STATUS, default='local')
    condition = SelectField("Condition", choices=CONDITION_TYPES, default='Foreign used')


class ComfortInteriorFeaturesForm(FlaskForm):
    seat_material = SelectField("Seat Material", choices=SEAT_MATERIALS, validators=[DataRequired()])
    trimming = SelectField("Interior Trimming", choices=TRIMMING_TYPES, validators=[DataRequired()])
    air_conditioning = SelectField("Air Conditioning Type", choices=AIR_CONDITIONING_TYPES, validators=[DataRequired()])
    sound_system = SelectField("Sound System", choices=SOUND_SYSTEM_TYPES, validators=[DataRequired()])
    power_windows = BooleanField("Power Windows", default=True, widget=BootstrapSwitchInput())
    sunroof = BooleanField("Sunroof / Moonroof", widget=BootstrapSwitchInput())
    heated_seats = BooleanField("Heated Seats", widget=BootstrapSwitchInput())
    powered_tailgate = BooleanField("Powered Tailgate/Liftgate", widget=BootstrapSwitchInput())
    phone_connectivity = BooleanField("Smartphone Integration (e.g., Apple CarPlay/Android Auto)", default=True,
                                      widget=BootstrapSwitchInput())
    auto_start_stop = BooleanField("Engine Auto Start/Stop Function", widget=BootstrapSwitchInput())
    ventilated_seats = BooleanField("Ventilated Seats", widget=BootstrapSwitchInput())
    memory_seats = BooleanField("Memory Seats", widget=BootstrapSwitchInput())
    power_adjustable_seats = BooleanField("Power Adjustable Seats", default=True, widget=BootstrapSwitchInput())
    dual_zone_climate_control = BooleanField("Dual-Zone Climate Control", widget=BootstrapSwitchInput())
    rear_air_conditioning = BooleanField("Rear Air Conditioning", widget=BootstrapSwitchInput())
    steering_wheel_controls = BooleanField("Steering Wheel Controls", default=True, widget=BootstrapSwitchInput())
    heated_steering_wheel = BooleanField("Heated Steering Wheel", widget=BootstrapSwitchInput())
    auto_dimming_mirrors = BooleanField("Auto-Dimming Mirrors", widget=BootstrapSwitchInput())
    rain_sensing_wipers = BooleanField("Rain-Sensing Wipers", widget=BootstrapSwitchInput())
    cargo_cover = BooleanField("Cargo Cover", widget=BootstrapSwitchInput())
    split_folding_rear_seats = BooleanField("Split-Folding Rear Seats", default=True, widget=BootstrapSwitchInput())
    keyless_entry = BooleanField("Keyless Entry (Proximity Key)", default=True, widget=BootstrapSwitchInput())
    push_button_start = BooleanField("Push Button Start", default=True, widget=BootstrapSwitchInput())
    remote_start = BooleanField("Remote Engine Start", widget=BootstrapSwitchInput())


class SafetyDriverAssistanceForm(FlaskForm):
    srs_air_bags = BooleanField("SRS Airbags (Multiple)", default=True, widget=BootstrapSwitchInput())
    lane_assistance = BooleanField("Lane Keep Assist / Lane Departure Warning", widget=BootstrapSwitchInput())
    hill_descent_control = BooleanField("Hill Descent Control", widget=BootstrapSwitchInput())
    roll_stability_control = BooleanField("Roll Stability Control", widget=BootstrapSwitchInput())
    standard_cruise_control = BooleanField("Standard Cruise Control", default=True, widget=BootstrapSwitchInput())
    adaptive_cruise_control = BooleanField("Adaptive Cruise Control", widget=BootstrapSwitchInput())
    antilock_braking_system = BooleanField("Anti-lock Braking System (ABS)", default=True,
                                           widget=BootstrapSwitchInput())
    emergency_braking_assist = BooleanField("Emergency Braking Assist", widget=BootstrapSwitchInput())
    immobilizer_and_anti_theft = BooleanField("Immobilizer & Anti-Theft System", default=True,
                                              widget=BootstrapSwitchInput())
    electronic_stability_control = BooleanField("Electronic Stability Control (ESC)", default=True,
                                                widget=BootstrapSwitchInput())
    rear_view_camera = BooleanField("Rear View Camera", default=True, widget=BootstrapSwitchInput())
    parking_sensors_front = BooleanField("Front Parking Sensors", widget=BootstrapSwitchInput())
    parking_sensors_rear = BooleanField("Rear Parking Sensors", widget=BootstrapSwitchInput())
    camera_360 = BooleanField("360-Degree Camera System (Surround View)", widget=BootstrapSwitchInput())
    blind_spot_monitoring = BooleanField("Blind Spot Monitoring", widget=BootstrapSwitchInput())
    rear_cross_traffic_alert = BooleanField("Rear Cross-Traffic Alert", widget=BootstrapSwitchInput())
    driver_attention_alert = BooleanField("Driver Attention Alert", widget=BootstrapSwitchInput())
    traffic_sign_recognition = BooleanField("Traffic Sign Recognition", widget=BootstrapSwitchInput())
    automatic_high_beams = BooleanField("Automatic High Beams", widget=BootstrapSwitchInput())
    tire_pressure_monitoring = BooleanField("Tire Pressure Monitoring System (TPMS)", default=True,
                                            widget=BootstrapSwitchInput())


class InfotainmentFeaturesForm(FlaskForm):
    navigation_system = BooleanField("Built-in Navigation System", widget=BootstrapSwitchInput())
    bluetooth_connectivity = BooleanField("Bluetooth Connectivity", default=True, widget=BootstrapSwitchInput())
    usb_ports = BooleanField("USB Ports Present", default=True, widget=BootstrapSwitchInput())
    wireless_charging = BooleanField("Wireless Phone Charging", widget=BootstrapSwitchInput())
    wi_fi_hotspot = BooleanField("Wi-Fi Hotspot", widget=BootstrapSwitchInput())


class ExteriorFeaturesForm(FlaskForm):
    led_headlights = BooleanField("LED Headlights", widget=BootstrapSwitchInput())
    alloy_wheels = BooleanField("Alloy Wheels", default=True, widget=BootstrapSwitchInput())
    roof_rails = BooleanField("Roof Rails", widget=BootstrapSwitchInput())
    spoiler = BooleanField("Rear Spoiler", widget=BootstrapSwitchInput())
    paint_color = SelectField("Exterior Paint Color", choices=PAINT_COLORS, validators=[DataRequired()])
    exterior_color_metallic = BooleanField("Metallic Paint Finish", widget=BootstrapSwitchInput())


class PerformanceFeaturesForm(FlaskForm):
    sport_suspension = BooleanField("Sport Suspension", widget=BootstrapSwitchInput())
    selectable_drive_modes = BooleanField("Selectable Drive Modes (e.g., Sport, Eco)", widget=BootstrapSwitchInput())
    paddle_shifters = BooleanField("Paddle Shifters", widget=BootstrapSwitchInput())


class PostForm(FlaskForm):
    file = MultipleFileField("Upload Images", validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    description = CKEditorField("Write a short description of the car, or set to auto-generate")
    ai = BooleanField("Generate description using AI", default=True, widget=BootstrapSwitchInput())

    # Embed other forms
    vehicle_specs = FormField(VehicleSpecificationsForm)
    comfort_interior = FormField(ComfortInteriorFeaturesForm)
    safety_assistance = FormField(SafetyDriverAssistanceForm)
    infotainment = FormField(InfotainmentFeaturesForm)
    exterior = FormField(ExteriorFeaturesForm)
    performance = FormField(PerformanceFeaturesForm)

    submit = SubmitField("Submit Post")


class PostEditForm(FlaskForm):
    file = MultipleFileField("Upload Images", validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    description = CKEditorField("Write a short description of the car, or set to auto-generate")
    ai = BooleanField("Generate new description using AI", widget=BootstrapSwitchInput())
    stock = SelectField(
        'Stock Availability',
        choices=[
            ('available', 'Available'),
            ('reserved', 'Reserved'),
            ('sold', 'Sold')
        ],
        default='available'
    )

    # Embed other forms
    vehicle_specs = FormField(VehicleSpecificationsForm)
    comfort_interior = FormField(ComfortInteriorFeaturesForm)
    safety_assistance = FormField(SafetyDriverAssistanceForm)
    infotainment = FormField(InfotainmentFeaturesForm)
    exterior = FormField(ExteriorFeaturesForm)
    performance = FormField(PerformanceFeaturesForm)

    submit = SubmitField("Submit Post")


# WTForm for posts
class CreatePostForm(FlaskForm):
    file = MultipleFileField("Add Images Here", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif']), FileSize(max_size=16000000, message="File must be less than 16 MB!")])
    brand = StringField("Brand of the vehicle", id="brand", validators=[DataRequired()])
    model = StringField("Vehicle make/ model", id="model", validators=[DataRequired()])
    vehicle_type = SelectField(
        'Build-type of the vehicle',
        choices=[
            ('saloon', 'Saloon'),
            ('SUV', 'SUV'),
            ('hatchback', 'Hatchback'),
            ('convertible', 'Convertible'),
            ('minivan', 'Minivan'),
            ('coupe', 'Coupe'),
            ('sports-car', 'Sports Car'),
            ('truck', 'Truck'),
            ('bike', 'Bike')
        ],
        default='saloon'
    )
    model_year = IntegerField("Model year", validators=[DataRequired()])
    engine_rating = StringField("Engine rating (include cc,kW or equivalent)", id="rating", render_kw={"placeholder": "3500cc"})
    price = IntegerField("Price", validators=[DataRequired()])
    mileage = IntegerField("Mileage", validators=[DataRequired(), NumberRange(max=1000000, message="Max-mileage!.")])
    fuel = SelectField(
        'Fuel Type',
        choices=[
            ('petrol', 'Petrol'),
            ('diesel', 'Diesel'),
            ('hybrid', 'Hybrid'),
            ('electric', 'Electric'),
            ('hydrogen/biofuel', 'Hydrogen/Biofuel'),
        ],
        default='petrol'
    )
    transmission = SelectField(
        'Tranmission type',
        choices=[
            ('automatic', 'Automatic'),
            ('manual', 'Manual')
        ],
        default='automatic'
    )
    drive_type = SelectField(
        'Drive-type of the vehicle',
        choices=[
            ('AWD', 'All Wheel Drive (AWD)'),
            ('2WD', 'Two Wheel Drive (2WD)'),
            ('4WD', 'Four Wheel Drive (4WD)')
        ],
        default='AWD'
    )
    availability = SelectField(
        'Vehicle Availability',
        choices=[
            ('local', 'Locally available'),
            ('import', 'Direct Import/International Stock'),

        ],
        default='local'
    )
    condition = SelectField(
        'Vehicle Condition',
        choices=[
            ('Foreign used', 'Foreign used'),
            ('Local used', 'Local used'),
            ('New', 'New'),

        ],
        default='Foreign used'
    )
    description = CKEditorField("Write a short description of the car, or tick box to auto-generate")
    # Apply the custom widget here
    ai = BooleanField("AI generated description", widget=BootstrapSwitchInput())

    # Comfort Features
    # Apply the custom widget to all BooleanFields
    sunroof = BooleanField('Sunroof', widget=BootstrapSwitchInput())
    trimming = SelectField('Trimming', choices=[('', 'Select Trimming'), ('wood', 'Wood'), ('aluminum', 'Aluminum'),
                                                ('carbon_fiber', 'Carbon Fiber'), ('other', 'Other')])
    heated_seats = BooleanField('Heated Seats', widget=BootstrapSwitchInput())
    sound_system = StringField('Sound System',
                               render_kw={"placeholder": "e.g., Bose, Harman Kardon, Factory Sound system"})
    power_windows = BooleanField('Power Windows', widget=BootstrapSwitchInput())
    seat_material = SelectField('Seat Material',
                                choices=[('', 'Select Material'), ('leather', 'Leather'), ('cloth', 'Cloth'),
                                         ('vinyl', 'Vinyl'), ('suede', 'Suede'), ('alcantara', 'Alcantara')])
    air_conditioning = SelectField('Air Conditioning', choices=[('', 'Select Type'), ('single_zone', 'Single Zone'),
                                                                ('multi_zone', 'Multi Zone'),
                                                                ('automatic', 'Automatic')])
    powered_tailgate = BooleanField('Powered Tailgate', widget=BootstrapSwitchInput())
    phone_connectivity = BooleanField('Phone Connectivity (Bluetooth, etc.)', widget=BootstrapSwitchInput())
    auto_start_stop = BooleanField('Auto Start And Stop', widget=BootstrapSwitchInput())

    # Safety Features
    srs_air_bags = BooleanField('SRS Air Bags', widget=BootstrapSwitchInput())
    lane_assistance = BooleanField('Lane Assistance', widget=BootstrapSwitchInput())
    hill_descent_control = BooleanField('Hill Descent Control', widget=BootstrapSwitchInput())
    roll_stability_control = BooleanField('Roll Stability Control', widget=BootstrapSwitchInput())
    standard_cruise_control = BooleanField('Standard Cruise Control', widget=BootstrapSwitchInput())
    adaptive_cruise_control = BooleanField('Adaptive Cruise Control', widget=BootstrapSwitchInput())
    antilock_braking_system = BooleanField('Antilock Braking System', widget=BootstrapSwitchInput())
    emergency_braking_assist = BooleanField('Emergency Braking Assist', widget=BootstrapSwitchInput())
    immobilizer_and_anti_theft = BooleanField('Immobilizer And Anti Theft', widget=BootstrapSwitchInput())
    electronic_stability_control = BooleanField('Electronic Stability Control', widget=BootstrapSwitchInput())

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
            ('available', 'Available'),
            ('reserved', 'Reserved'),
            ('sold', 'Sold')
        ],
        default='available'
    )
    vehicle_type = SelectField(
        'Build-type of the vehicle',
        choices=[
            ('saloon', 'Saloon'),
            ('SUV', 'SUV'),
            ('hatchback', 'Hatchback'),
            ('convertible', 'Convertible'),
            ('truck', 'Truck'),
            ('bike', 'Bike')
        ],
        default='saloon'
    )
    model_year = IntegerField("Model year", validators=[DataRequired()])
    engine_rating = StringField("Engine rating", id="rating", render_kw={"placeholder": "3500cc"})
    price = IntegerField("Price", validators=[DataRequired()])
    mileage = IntegerField("Mileage", validators=[DataRequired(), NumberRange(max=1000000, message="Max-mileage!.")])
    fuel = SelectField(
        'Fuel Type',
        choices=[
            ('petrol', 'Petrol'),
            ('diesel', 'Diesel'),
            ('hybrid', 'Hybrid'),
            ('electric', 'Electric'),
            ('hydrogen/biofuel', 'Hydrogen/Biofuel'),
        ],
        default='petrol'
    )
    transmission = SelectField(
        'Tranmission type',
        choices=[
            ('automatic', 'Automatic'),
            ('manual', 'Manual')
        ],
        default='automatic'
    )
    drive_type = SelectField(
        'Drive-type of the vehicle',
        choices=[
            ('AWD', 'All Wheel Drive (AWD)'),
            ('2WD', 'Two Wheel Drive (2WD)'),
            ('4WD', 'Four Wheel Drive (4WD)')
        ],
        default='AWD'
    )
    availability = SelectField(
        'Vehicle Availability',
        choices=[
            ('local', 'Locally available'),
            ('import', 'Direct Import/International Stock'),

        ],
        default='local'
    )
    condition = SelectField(
        'Vehicle Condition',
        choices=[
            ('Foreign used', 'Foreign used'),
            ('Local used', 'Local used'),
            ('New', 'New'),

        ],
        default='Foreign used'
    )
    description = CKEditorField("Write a short description of the car, or tick box to auto-generate")
    # Apply the custom widget here
    ai = BooleanField("AI generated description", widget=BootstrapSwitchInput())

    # Comfort Features
    # Apply the custom widget to all BooleanFields
    sunroof = BooleanField('Sunroof', widget=BootstrapSwitchInput())
    trimming = SelectField('Trimming', choices=[('', 'Select Trimming'), ('wood', 'Wood'), ('aluminum', 'Aluminum'),
                                                ('carbon_fiber', 'Carbon Fiber'), ('other', 'Other')])
    heated_seats = BooleanField('Heated Seats', widget=BootstrapSwitchInput())
    sound_system = StringField('Sound System',
                               render_kw={"placeholder": "e.g., Bose, Harman Kardon, Factory Sound system"})
    power_windows = BooleanField('Power Windows', widget=BootstrapSwitchInput())
    seat_material = SelectField('Seat Material',
                                choices=[('', 'Select Material'), ('leather', 'Leather'), ('cloth', 'Cloth'),
                                         ('vinyl', 'Vinyl'), ('suede', 'Suede'), ('alcantara', 'Alcantara')])
    air_conditioning = SelectField('Air Conditioning', choices=[('', 'Select Type'), ('single_zone', 'Single Zone'),
                                                                ('multi_zone', 'Multi Zone'),
                                                                ('automatic', 'Automatic')])
    powered_tailgate = BooleanField('Powered Tailgate', widget=BootstrapSwitchInput())
    phone_connectivity = BooleanField('Phone Connectivity (Bluetooth, etc.)', widget=BootstrapSwitchInput())
    auto_start_stop = BooleanField('Auto Start And Stop', widget=BootstrapSwitchInput())

    # Safety Features
    srs_air_bags = BooleanField('SRS Air Bags', widget=BootstrapSwitchInput())
    lane_assistance = BooleanField('Lane Assistance', widget=BootstrapSwitchInput())
    hill_descent_control = BooleanField('Hill Descent Control', widget=BootstrapSwitchInput())
    roll_stability_control = BooleanField('Roll Stability Control', widget=BootstrapSwitchInput())
    standard_cruise_control = BooleanField('Standard Cruise Control', widget=BootstrapSwitchInput())
    adaptive_cruise_control = BooleanField('Adaptive Cruise Control', widget=BootstrapSwitchInput())
    antilock_braking_system = BooleanField('Antilock Braking System', widget=BootstrapSwitchInput())
    emergency_braking_assist = BooleanField('Emergency Braking Assist', widget=BootstrapSwitchInput())
    immobilizer_and_anti_theft = BooleanField('Immobilizer And Anti Theft', widget=BootstrapSwitchInput())
    electronic_stability_control = BooleanField('Electronic Stability Control', widget=BootstrapSwitchInput())

    submit = SubmitField("Submit Post")


class EditProfileForm(FlaskForm):
    name = StringField("Enter your name", id="brand", validators=[DataRequired()])
    phone_number = StringField('Phone Number: This is how clients will reach you. N/B: Format - +254123456789', id="model", validators=[
        DataRequired(),
        Regexp(r'^\+\d{1,15}$', message="Invalid phone number format")
    ])
    submit = SubmitField("Update Profile")
