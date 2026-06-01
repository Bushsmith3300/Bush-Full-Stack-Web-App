import os
import re
from dotenv import load_dotenv
from datetime import timedelta

from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    redirect,
    url_for,
    session,
    flash
)

from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

from models import (
    db,
    Question,
    User,
    QuizHistory,
    UserProgress,
    Announcement,
    ClassStatus,
    Quote
)


# ---------------- LOAD ENV ----------------
load_dotenv()


# ---------------- APP ----------------
app = Flask(__name__)
CORS(app)


# ---------------- SECRET KEY ----------------
app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    if os.getenv("RENDER_ENV") == "production":
        raise ValueError("SECRET_KEY must be set in production!")

    # Local fallback only
    app.secret_key = "dev-secret-key-change-this"


# ---------------- SESSION SECURITY ----------------
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# HTTP locally, HTTPS in production
app.config["PREFERRED_URL_SCHEME"] = (
    "https"
    if os.getenv("RENDER_ENV") == "production"
    else "http"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Secure cookies only in production
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv("RENDER_ENV") == "production"
)

# Safer local cookie handling
app.config["SESSION_COOKIE_NAME"] = (
    "__Host-session"
    if os.getenv("RENDER_ENV") == "production"
    else "session"
)


# ---------------- DATABASE ----------------
database_url = os.getenv("DATABASE_URL")
print("DATABASE_URL =", database_url)

# Local fallback
if not database_url:
    if os.getenv("RENDER_ENV") == "production":
        raise ValueError("DATABASE_URL must be set in production")

    database_url = "sqlite:///chemistry.db"


# FIX deprecated postgres:// URLs
if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )


# PostgreSQL / Supabase SSL settings
if database_url.startswith("postgresql://"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {
            "sslmode": "require"
        },
        "pool_pre_ping": True,
        "pool_recycle": 300
    }


# SQLAlchemy config
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ---------------- INIT DB ----------------
db.init_app(app)

migrate = Migrate(app, db)

CSRFProtect(app)


# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("aboutpage.html")


@app.route("/contact")
def contact():
    return render_template("contactpage.html")


# ---------------- QUESTIONS API ----------------
@app.route("/questions/<path:topic>")
def get_questions(topic):

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    topic = topic.lower().strip()

    questions = (
        Question.query
        .filter(Question.topic.ilike(f"%{topic}%"))
        .order_by(func.random())
        .all()
    )

    return jsonify({
        "questions": [
            {
                "question": q.question_text,
                "options": [
                    {"letter": "A", "text": q.option_a},
                    {"letter": "B", "text": q.option_b},
                    {"letter": "C", "text": q.option_c},
                    {"letter": "D", "text": q.option_d},
                ],
                "answer": q.correct_answer,
                "explanation": q.explanation
            }
            for q in questions
        ]
    })


# ---------------- QUIZ PAGE ----------------
@app.route("/quiz/<path:topic>")
def quiz(topic):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "quiz_screen2.html",
        topic=topic,
        user=user
    )


# ---------------- ANNOUNCEMENTS ----------------
@app.route("/announcements")
def announcement_page():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    announcements = Announcement.query.all()

    quote = Quote.query.first()

    return render_template(
        "announcements.html",
        announcements=announcements,
        user=user,
        today_quote=quote
    )


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip().lower()

        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        first_name = request.form.get(
            "first_name",
            ""
        ).strip()

        surname = request.form.get(
            "surname",
            ""
        ).strip()

        other_name = request.form.get(
            "other_name",
            ""
        ).strip()

        # Validation
        if not username or len(username) < 3:
            flash(
                "Username must be at least 3 characters",
                "error"
            )
            return redirect(url_for("register"))

        if not re.match(r"^[a-z0-9_]+$", username):
            flash(
                "Username can only contain letters, numbers, and underscore",
                "error"
            )
            return redirect(url_for("register"))

        if len(password) < 6:
            flash(
                "Password must be at least 6 characters",
                "error"
            )
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))

        if not first_name or not surname:
            flash(
                "First name and surname are required",
                "error"
            )
            return redirect(url_for("register"))

        # Existing user check
        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            flash(
                "You already have a BTA account. Login instead!",
                "error"
            )
            return redirect(url_for("login"))

        # Create user
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            first_name=first_name,
            surname=surname,
            other_name=other_name
        )

        db.session.add(new_user)
        db.session.flush()

        progress = UserProgress(
            user_id=new_user.id
        )

        db.session.add(progress)
        db.session.commit()

        flash(
            "Registration successful!",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip().lower()

        password = request.form.get("password", "")

        if not username or not password:
            flash(
                "Invalid username or password",
                "error"
            )
            return redirect(url_for("login"))

        user = User.query.filter_by(
            username=username
        ).first()

        if not user or not check_password_hash(
            user.password,
            password
        ):
            flash(
                "Invalid username or password",
                "error"
            )
            return redirect(url_for("login"))

        session.clear()

        session["user_id"] = user.id
        session["username"] = user.username

        session.permanent = True

        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(
        User,
        session["user_id"]
    )

    if not user:
        session.clear()
        return redirect(url_for("login"))

    last_quiz = (
        QuizHistory.query
        .filter_by(user_id=user.id)
        .order_by(QuizHistory.date.desc())
        .first()
    )

    status = ClassStatus.query.first()

    quote = Quote.query.first()

    return render_template(
        "dashboard.html",
        user=user,
        last_quiz=last_quiz,
        class_status=status,
        today_quote=quote
    )


# ---------------- SUBJECT SELECT ----------------
@app.route("/subject_select", methods=["GET", "POST"])
def subject_select():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(
        User,
        session["user_id"]
    )

    return render_template(
        "subject_select.html",
        user=user
    )


# ---------------- TOPIC SELECT ----------------
@app.route("/topic_select", methods=["GET", "POST"])
def topic_select():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(
        User,
        session["user_id"]
    )

    if request.method == "POST":

        selected = request.form.getlist("topics")

        if not selected:
            flash(
                "Select at least one topic",
                "error"
            )
            return redirect(url_for("topic_select"))

        return redirect(
            url_for("quiz", topic=selected[0])
        )

    return render_template(
        "topic_select.html",
        user=user
    )


# ---------------- ENTER CLASS ----------------
@app.route("/enter_class")
def enter_class():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(
        User,
        session["user_id"]
    )

    if not user:
        session.clear()
        return redirect(url_for("login"))

    status = ClassStatus.query.first()

    if not status or not status.is_live:
        flash(
            "Class is not live yet",
            "error"
        )
        return redirect(url_for("dashboard"))

    return redirect(status.link)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out",
        "success"
    )

    return redirect(url_for("login"))


# ---------------- DB CHECK ----------------
@app.route("/db-check")
def db_check():

    return {
        "database_url": str(
            app.config["SQLALCHEMY_DATABASE_URI"]
        )
    }


# ---------------- ERROR HANDLER ----------------
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


    app.run(debug=True)
