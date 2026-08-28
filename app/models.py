from datetime import datetime, timezone
from app import db


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40))
    service = db.Column(db.String(80), nullable=False)
    preferred_date = db.Column(db.Date)
    preferred_time = db.Column(db.Time)
    birth_date = db.Column(db.Date)
    birth_time = db.Column(db.Time)
    birth_place = db.Column(db.String(255))
    message = db.Column(db.Text)
    status = db.Column(db.String(30), nullable=False, default="new")
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Enquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(40))
    message = db.Column(db.Text)
    page_source = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contacted = db.Column(db.Boolean, nullable=False, default=False)

