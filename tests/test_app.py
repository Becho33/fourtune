from app import create_app, db
from app.models import Booking


class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test"
    ADMIN_PASSWORD = "correct-horse"


def client():
    app = create_app(TestConfig)
    with app.test_client() as test_client:
        yield test_client


def test_pages():
    for c in client():
        for path in ["/", "/services", "/tarot", "/astrology", "/palmistry", "/four-pillars", "/about", "/booking", "/contact", "/privacy", "/my-booking", "/admin/login"]:
            assert c.get(path).status_code == 200


def test_language_toggle_is_available_sitewide():
    for c in client():
        for path in ["/", "/services", "/booking", "/contact", "/privacy"]:
            page = c.get(path)
            assert b'class="language-toggle"' in page.data
            assert b'js/language.js' in page.data


def test_enquiry_requires_contact_method():
    for c in client():
        response = c.post("/api/enquiry", json={"name": "A"})
        assert response.status_code == 400
        assert response.json["success"] is False


def test_enquiry_is_saved():
    for c in client():
        response = c.post("/api/enquiry", json={"email": "reader@example.com"})
        assert response.status_code == 200
        assert response.json == {"success": True}


def test_customer_booking_lookup_requires_matching_email():
    for c in client():
        with c.application.app_context():
            booking = Booking(name="Reader", email="reader@example.com", service="tarot")
            db.session.add(booking)
            db.session.commit()
            reference = booking.id
        good = c.post("/my-booking", data={"reference": reference, "email": "READER@example.com"})
        assert b"Tarot" in good.data
        bad = c.post("/my-booking", data={"reference": reference, "email": "other@example.com"})
        assert b"No booking matched" in bad.data


def test_admin_authentication_and_status_update():
    for c in client():
        protected = c.get("/admin/bookings")
        assert protected.status_code == 302
        failed = c.post("/admin/login", data={"password": "wrong"})
        assert b"Incorrect admin password" in failed.data
        signed_in = c.post("/admin/login", data={"password": "correct-horse"})
        assert signed_in.status_code == 302
        with c.application.app_context():
            booking = Booking(name="Reader", email="reader@example.com", service="astrology")
            db.session.add(booking)
            db.session.commit()
            reference = booking.id
        updated = c.post(f"/admin/bookings/{reference}/status", data={"status": "confirmed"})
        assert updated.status_code == 302
        with c.application.app_context():
            assert db.session.get(Booking, reference).status == "confirmed"
