from functools import wraps
import hmac

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.forms import AdminLoginForm, BookingForm, BookingLookupForm, BookingStatusForm, ContactForm, SERVICES
from app.models import Booking, Enquiry

main = Blueprint("main", __name__)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect(url_for("main.admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

SERVICE_DATA = {
    "tarot": {"name": "Tarot Reading", "eyebrow": "Symbol · Intuition · Reflection", "intro": "A reflective practice using symbolic cards to illuminate the emotions, choices and influences around your present situation.", "topics": ["Important decisions", "Relationships", "Career changes", "Life transitions", "Personal direction", "A fresh perspective"], "detail": "Tarot does not need to be viewed as a fixed prediction. I use the cards as a thoughtful mirror—an invitation to recognise patterns, explore possibilities and listen more closely to your own intuition."},
    "astrology": {"name": "Astrology Reading", "eyebrow": "Pattern · Potential · Timing", "intro": "Your birth chart is a map of the sky at the moment you were born, offering a rich symbolic language for understanding your nature and life patterns.", "topics": ["Personality", "Relationships", "Career and ambitions", "Life cycles", "Strengths and challenges", "Personal development"], "detail": "A detailed reading considers the Sun, Moon, planets and astrological houses. Your date, approximate time and place of birth help create the clearest possible chart."},
    "palmistry": {"name": "Palmistry Reading", "eyebrow": "Character · Change · Direction", "intro": "Palmistry is the traditional interpretation of the hands—their form, lines and subtle characteristics—as a reflection of personality and possibility.", "topics": ["Character", "Emotional nature", "Relationships", "Life direction", "Ambition", "Creativity and strengths"], "detail": "Our hands can change gradually throughout life. I see palmistry not as a fixed verdict, but as a personal portrait of the qualities you carry and the person you are becoming."},
    "four-pillars": {"name": "Four Pillars of Destiny", "eyebrow": "Balance · Cycles · Opportunity", "intro": "Also known as BaZi, this East Asian system uses birth information to explore character, natural strengths, relationships and the changing seasons of a life.", "topics": ["Personality", "Natural talents", "Relationships", "Career tendencies", "Life cycles", "Periods of opportunity"], "detail": "The year, month, day and hour of birth form four symbolic pillars. Together they create a chart for exploring balance, recurring themes and periods of transition. Date, time and place of birth are helpful for a detailed reading."},
}


@main.route("/")
def index(): return render_template("index.html", services=SERVICE_DATA)


@main.route("/services")
def services(): return render_template("services.html", services=SERVICE_DATA)


@main.route("/tarot")
@main.route("/astrology")
@main.route("/palmistry")
@main.route("/four-pillars")
def service_detail():
    slug = request.path.strip("/")
    if slug not in SERVICE_DATA: return redirect(url_for("main.services"))
    return render_template("service_detail.html", service=SERVICE_DATA[slug], slug=slug)


@main.route("/about")
def about(): return render_template("about.html")


@main.route("/booking", methods=["GET", "POST"])
def booking():
    form = BookingForm()
    requested = request.args.get("service")
    if request.method == "GET" and requested in dict(SERVICES): form.service.data = requested
    if form.validate_on_submit():
        booking = Booking(name=form.name.data, email=form.email.data, phone=form.phone.data, service=form.service.data, preferred_date=form.preferred_date.data, preferred_time=form.preferred_time.data, birth_date=form.birth_date.data, birth_time=form.birth_time.data, birth_place=form.birth_place.data, message=form.message.data)
        db.session.add(booking); db.session.commit()
        flash(f"Thank you. Your booking reference is #{booking.id}. Keep this number to view your request later.", "success")
        return redirect(url_for("main.booking"))
    return render_template("booking.html", form=form)


@main.route("/my-booking", methods=["GET", "POST"])
def my_booking():
    form = BookingLookupForm()
    booking_record = None
    if form.validate_on_submit():
        booking_record = db.session.get(Booking, form.reference.data)
        if not booking_record or booking_record.email.strip().casefold() != form.email.data.strip().casefold():
            booking_record = None
            flash("No booking matched that reference and email address.", "warning")
    return render_template("my_booking.html", form=form, booking=booking_record, services=dict(SERVICES))


@main.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_authenticated"):
        return redirect(url_for("main.admin_bookings"))
    form = AdminLoginForm()
    if form.validate_on_submit():
        expected = current_app.config["ADMIN_PASSWORD"]
        if hmac.compare_digest(form.password.data, expected):
            session.clear()
            session["admin_authenticated"] = True
            return redirect(url_for("main.admin_bookings"))
        flash("Incorrect admin password.", "warning")
    return render_template("admin_login.html", form=form)


@main.post("/admin/logout")
@admin_required
def admin_logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("main.admin_login"))


@main.route("/admin/bookings")
@admin_required
def admin_bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template("admin_bookings.html", bookings=bookings, services=dict(SERVICES), status_form=BookingStatusForm())


@main.post("/admin/bookings/<int:booking_id>/status")
@admin_required
def admin_booking_status(booking_id):
    booking_record = db.get_or_404(Booking, booking_id)
    form = BookingStatusForm()
    if form.validate_on_submit():
        booking_record.status = form.status.data
        db.session.commit()
        flash(f"Booking #{booking_record.id} updated.", "success")
    else:
        flash("That status could not be applied.", "warning")
    return redirect(url_for("main.admin_bookings"))


@main.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        db.session.add(Enquiry(name=form.name.data, email=form.email.data, phone=form.phone.data, message=form.message.data, page_source="contact")); db.session.commit()
        flash("Thank you for your message. I will contact you shortly.", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form)


@main.route("/privacy")
def privacy(): return render_template("privacy.html")


@main.post("/api/enquiry")
def enquiry_api():
    data = request.get_json(silent=True) or request.form
    name, email, phone = (str(data.get(k, "")).strip() for k in ("name", "email", "phone"))
    if not email and not phone: return jsonify(success=False, error="Please provide an email address or telephone number."), 400
    if email and ("@" not in email or len(email) > 255): return jsonify(success=False, error="Please enter a valid email address."), 400
    if any(len(v) > m for v, m in ((name, 120), (phone, 40))): return jsonify(success=False, error="Please check your details."), 400
    try:
        db.session.add(Enquiry(name=name, email=email, phone=phone, page_source=str(data.get("page_source", "popup"))[:255])); db.session.commit()
    except SQLAlchemyError:
        db.session.rollback(); current_app.logger.exception("Could not save enquiry")
        return jsonify(success=False, error="Something went wrong. Please try again."), 500
    return jsonify(success=True)
