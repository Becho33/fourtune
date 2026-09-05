# Riina Kushu — Intuitive Readings

A responsive Flask website for a Japanese intuitive reader, with service pages, secure enquiry and booking forms, SQLite persistence, CSRF protection, and a scroll-intent contact prompt.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="replace-with-a-long-random-value"
export ADMIN_PASSWORD="replace-with-a-strong-private-password"
export MAIL_SERVER="smtp.example.com"
export MAIL_PORT="587"
export MAIL_USERNAME="your-smtp-username"
export MAIL_PASSWORD="your-smtp-password"
export MAIL_FROM="bookings@example.com"
export BOOKING_NOTIFICATION_EMAIL="you@example.com"
export WHATSAPP_NUMBER="447700900000"
flask --app run.py run --debug
```

The database is created automatically at `instance/fortune.db` on first launch. You can also initialise it explicitly:

```bash
flask --app run.py shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

Open <http://127.0.0.1:5000>.

Customers can look up a request at <http://127.0.0.1:5000/my-booking> using the booking reference shown after submission and the matching email address.

Riina can manage all requests at <http://127.0.0.1:5000/admin/login>. Set `ADMIN_PASSWORD` before starting the server. The development fallback is `change-me-now` and must not be used for a deployed website.

Booking notification emails are sent when all mail settings above are configured. `WHATSAPP_NUMBER` must contain the full international number, including country code and without a leading `+`; the chat widget remains hidden if it is not set.

## Structure

- `app/__init__.py` — application factory and extensions
- `app/models.py` — booking and enquiry database models
- `app/forms.py` — validated, CSRF-protected forms
- `app/routes.py` — page and JSON API routes
- `app/templates/` — reusable Jinja templates
- `app/static/` — site CSS, JavaScript and imagery
- `config.py` — environment-aware configuration
- `run.py` — development entry point
- `instance/fortune.db` — generated SQLite database (not committed)

For production, use a strong `SECRET_KEY`, a production WSGI server, HTTPS, and a managed database.
