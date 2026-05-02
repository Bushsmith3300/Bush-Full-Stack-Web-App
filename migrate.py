import sqlite3
from app import app, db
from models import Question, User

# 🔁 your SQLite file
SQLITE_DB = "chemistry.db"

conn = sqlite3.connect(SQLITE_DB)
cursor = conn.cursor()

with app.app_context():

    print("🚀 Starting migration...")

    # ------------------ USERS ------------------
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    for u in users:
        new_user = User(
            id=u[0],
            username=u[1],
            password=u[2],
            first_name=u[3],
            surname=u[4],
            other_name=u[5]
        )
        db.session.add(new_user)

    print(f"✅ Migrated {len(users)} users")

    # ------------------ QUESTIONS ------------------
    cursor.execute("SELECT * FROM question")
    questions = cursor.fetchall()

    for q in questions:
        new_q = Question(
            id=q[0],
            topic=q[1],
            question_text=q[2],
            option_a=q[3],
            option_b=q[4],
            option_c=q[5],
            option_d=q[6],
            correct_answer=q[7],
            explanation=q[8]
        )
        db.session.add(new_q)

    print(f"✅ Migrated {len(questions)} questions")

    # ------------------ COMMIT ------------------
    db.session.commit()
    print("🎉 Migration completed successfully!")

conn.close()
