from flask_wtf import FlaskForm
from wtforms import DateField, EmailField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

SERVICES = [
    ("tarot", "Tarot — £60"),
    ("astrology", "Astrology — £60"),
    ("palmistry", "Palmistry — £60"),
    ("four-pillars", "Four Pillars of Destiny — £60"),
]


class BookingForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = EmailField("Email address", validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField("Telephone number", validators=[Optional(), Length(max=40)])
    service = SelectField("Preferred reading", choices=SERVICES, validators=[DataRequired()])
    preferred_date = DateField("Preferred date", validators=[Optional()])
    preferred_time = TimeField("Preferred time", validators=[Optional()])
    birth_date = DateField("Date of birth", validators=[Optional()])
    birth_time = TimeField("Time of birth", validators=[Optional()])
    birth_place = StringField("Place of birth", validators=[Optional(), Length(max=255)])
    message = TextAreaField("Message / question", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("Request My Reading")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = EmailField("Email address", validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField("Telephone number", validators=[Optional(), Length(max=40)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=3000)])
    submit = SubmitField("Send Message")


class BookingLookupForm(FlaskForm):
    reference = IntegerField("Booking reference", validators=[DataRequired(), NumberRange(min=1)])
    email = EmailField("Email address", validators=[DataRequired(), Email(), Length(max=255)])
    submit = SubmitField("View My Booking")


class AdminLoginForm(FlaskForm):
    password = PasswordField("Admin password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class BookingStatusForm(FlaskForm):
    status = SelectField("Status", choices=[
        ("new", "New"),
        ("contacted", "Contacted"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ], validators=[DataRequired()])
    submit = SubmitField("Update")
