import os
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from models import db, Question, User, QuizHistory, UserProgress
from sqlalchemy import func, inspect
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

csrf = CSRFProtect(app)

app.secret_key = os.getenv("SECRET_KEY", "Bhbush3300/")

if not app.secret_key or len(app.secret_key) < 16:
    raise ValueError("SECRET_KEY missing or too weak!")

app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["PREFERRED_URL_SCHEME"] = "https"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = True


database_url = os.getenv("DATABASE_URL")

if database_url and database_url.strip():
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

else:
    # 🔐 block production fallback to SQLite
    if os.getenv("RENDER"):
        raise ValueError("Production requires PostgreSQL")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chemistry.db"


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------- STATIC DATA ----------------


announcements = [{
    "title": "Form 2 end of Semester Examination",
    "message": "Study Chemical Equilibrium and Acids, Bases and Salts in addition to topics treated in class",
    "date": "25th May 2026 to 5th June 2026",
    "time": ""},

{
    "title": "Chemistry Online Class",
    "message": "There will be an online chemistry class for 2 Science 7, 8, 9, 10 and 11",
    "date": "Friday 8th May, 2026",
    "time": "4:00 pm"}]

today_quote = {
    "title": "Quote of the Day",
    "message": "Loneliness is the price you pay to achieve academic excellence!",
    "action": "Make it count!"
}


class_status = {
    "is_live": False,
    "link": "https://meet.google.com"
}



# ---------------- QUESTIONS API ----------------


@app.route("/questions/<path:topic>")
def get_questions(topic):

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    topic = topic.lower().strip()

    # ✅ RANDOMIZED QUESTIONS
    questions = Question.query.filter(
        Question.topic.ilike(f"%{topic}%")
    ).order_by(func.random()).all()

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

# ---------------- PAGES ----------------


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("aboutpage.html")

@app.route("/contact")
def contact():
    return render_template("contactpage.html")



# ---------------- ANNOUNCEMENTS ----------------


@app.route("/announcements")
def announcement_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "announcements.html",
        announcements=announcements,
        user=user,
        today_quote=today_quote
    )


# ---------------- REGISTER ----------------


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        first_name = request.form["first_name"]
        surname = request.form["surname"]
        other_name = request.form.get("other_name", "")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("You already have a BTA account", "success")
            return redirect(url_for("login"))

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            first_name=first_name,
            surname=surname,
            other_name=other_name)

        db.session.add(new_user)
        db.session.flush()  # get user.id without commit

        progress = UserProgress(user_id=new_user.id)
        db.session.add(progress)

        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")



# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Username does not exist! Create an account", "error")
            return redirect(url_for("login"))

        if not check_password_hash(user.password, password):
            flash("Incorrect password", "error")
            return redirect(url_for("login"))

        # 🔐 Regenerate session (important security step)

        session.clear()
        session["user_id"] = user.id
        session["username"] = user.username

        session.permanent = True  # ( makes session expire based on config time )


        return redirect(url_for("dashboard"))

    return render_template("login.html")


#---------DASHBOARD-----------------

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    # ✅ SAFE VERSION (works regardless of relationship type)
    last_quiz = QuizHistory.query\
        .filter_by(user_id=user.id)\
        .order_by(QuizHistory.date.desc())\
        .first()

    return render_template(
        "dashboard.html",
        user=user,
        last_quiz=last_quiz,
        class_status=class_status
    )
   



# ---------------- SUBJECT SELECT ----------------
@app.route("/subject_select", methods=["GET", "POST"])
def subject_select():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    return render_template("subject_select.html", user=user)



# ---------------- TOPIC SELECT ----------------
@app.route("/topic_select", methods=["GET", "POST"])
def topic_select():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if request.method == "POST":
        selected = request.form.getlist("topics")

        if not selected:
            flash("Select at least one topic", "error")
            return redirect(url_for("topic_select"))

        return redirect(url_for("quiz", topic=selected[0]))

    return render_template("topic_select.html", user=user)



# ---------------- ENTER CLASS ----------------
@app.route("/enter_class")
def enter_class():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))

    if not class_status["is_live"]:
        flash("Class is not live yet", "error")
        return redirect(url_for("dashboard"))

    return redirect(class_status["link"])

@app.route("/init-db")
def init_db():
    if not os.getenv("RENDER"):  # only allow locally
        db.create_all()
        return "Database initialized locally!"
    return "Not allowed in production"



# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for("login"))


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

