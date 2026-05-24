from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ---------------- QUESTIONS ----------------
class Question(db.Model):
    __tablename__ = "question"

    id = db.Column(db.Integer, primary_key=True)

    topic = db.Column(db.String(100), nullable=False)

    question_text = db.Column(db.String(500), nullable=False)

    option_a = db.Column(db.String(300), nullable=False)
    option_b = db.Column(db.String(300), nullable=False)
    option_c = db.Column(db.String(300), nullable=False)
    option_d = db.Column(db.String(300), nullable=False)

    correct_answer = db.Column(db.String(1), nullable=False)

    explanation = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return f"<Question {self.id}>"


# ---------------- USERS ----------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    first_name = db.Column(
        db.String(100),
        nullable=False
    )

    surname = db.Column(
        db.String(100),
        nullable=False
    )

    other_name = db.Column(
        db.String(100)
    )

    email = db.Column(
        db.String(200),
        nullable=True,
        unique=True
    )

    # Relationships
    progress = db.relationship(
        "UserProgress",
        backref="user",
        uselist=False
    )

    quiz_history = db.relationship(
        "QuizHistory",
        backref="user",
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<User {self.username}>"


# ---------------- USER PROGRESS ----------------
class UserProgress(db.Model):
    __tablename__ = "user_progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    topics = db.Column(db.String(300))

    total_score = db.Column(
        db.Integer,
        default=0
    )

    quizzes_taken = db.Column(
        db.Integer,
        default=0
    )

    def __repr__(self):
        return f"<UserProgress {self.user_id}>"


# ---------------- QUIZ HISTORY ----------------
class QuizHistory(db.Model):
    __tablename__ = "quiz_history"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    topic = db.Column(db.String(100))

    score = db.Column(db.Integer)

    date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return (
            f"<QuizHistory "
            f"user_id={self.user_id} "
            f"score={self.score}>"
        )


# ---------------- ANNOUNCEMENTS ----------------
class Announcement(db.Model):
    __tablename__ = "announcement"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(300),
        nullable=True
    )

    message = db.Column(
        db.Text,
        nullable=True
    )

    date = db.Column(
        db.String(30),
        nullable=True
    )

    time = db.Column(
        db.String(20),
        nullable=True
    )

    def __repr__(self):
        return f"<Announcement {self.title}>"


# ---------------- CLASS STATUS ----------------
class ClassStatus(db.Model):
    __tablename__ = "class_status"

    id = db.Column(db.Integer, primary_key=True)

    is_live = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    link = db.Column(
        db.String(200),
        nullable=True
    )

    def __repr__(self):
        return f"<ClassStatus live={self.is_live}>"


# ---------------- QUOTE ----------------
class Quote(db.Model):
    __tablename__ = "today_quote"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(500),
        nullable=True
    )

    message = db.Column(
        db.Text,
        nullable=True
    )

    action = db.Column(
        db.String(500),
        nullable=True
    )

    def __repr__(self):
        return f"<Quote {self.id}>"
