import sqlite3
from app import app, db
from models import Question, User, UserProgress, QuizHistory

conn = sqlite3.connect("chemistry.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

with app.app_context():

    # -----------------------------------
    # QUESTIONS
    # -----------------------------------
    cursor.execute("SELECT * FROM question")
    questions = cursor.fetchall()

    for q in questions:
        db.session.add(Question(
            id=q["id"],
            topic=q["topic"],
            question_text=q["question_text"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            correct_answer=q["correct_answer"],
            explanation=q["explanation"]
        ))

    db.session.commit()
    print("✅ Questions migrated")


    # -----------------------------------
    # USERS
    # -----------------------------------
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    for u in users:
        db.session.add(User(
            id=u["id"],
            username=u["username"],
            password=u["password"],
            first_name=u["first_name"],
            surname=u["surname"],
            other_name=u["other_name"]
        ))

    db.session.commit()
    print("✅ Users migrated")


    # -----------------------------------
    # USER PROGRESS (EMPTY SAFE MIGRATION)
    # -----------------------------------
    cursor.execute("SELECT * FROM user_progress")
    progress = cursor.fetchall()

    for p in progress:
        db.session.add(UserProgress(
            id=p["id"],
            user_id=p["user_id"],
            topics=p["topics"],
            total_score=p["total_score"],
            quizzes_taken=p["quizzes_taken"]
        ))

    db.session.commit()
    print("✅ User progress migrated")


    # -----------------------------------
    # QUIZ HISTORY
    # -----------------------------------
    cursor.execute("SELECT * FROM quiz_history")
    history = cursor.fetchall()

    for h in history:
        db.session.add(QuizHistory(
            id=h["id"],
            user_id=h["user_id"],
            topic=h["topic"],
            score=h["score"],
            date=h["date"]
        ))

    db.session.commit()
    print("✅ Quiz history migrated")


conn.close()
print("🎉 ALL DATA MIGRATED SUCCESSFULLY")