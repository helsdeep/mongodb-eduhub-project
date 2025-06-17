from faker import Faker
from datetime import timedelta
import uuid
import random

from database.mongo_db import db
from models.Submission import submission_validator
from utils.timestamp import utc_now_iso


def create_submissions():
    if "submissions" not in db.list_collection_names():
        db.create_collection("submissions")
    db.command("collMod", "submissions", validator={"$jsonSchema": submission_validator})

    submissions = db["submissions"]
    submissions.create_index("submissionId", unique=True)

    students = list(db["users"].find({"role": "student"}, {"userId": 1}))
    assignments = list(db["assignments"].find({}, {"assignmentId": 1}))

    if not students or not assignments:
        print("❌ Cannot add submissions: missing students or assignments.")
        return

    fake = Faker()

    for i in range(12):
        student = random.choice(students)
        assignment = random.choice(assignments)

        submitted_at = utc_now_iso() - timedelta(days=random.randint(0, 15))
        is_graded = random.choice([True, False])
        graded_at = utc_now_iso() if is_graded else None
        score = random.randint(50, 100) if is_graded else 0
        feedback = fake.sentence() if is_graded else "None"

        submission = {
            "submissionId": str(uuid.uuid4()),
            "assignmentId": assignment["assignmentId"],
            "studentId": student["userId"],
            "submittedAt": submitted_at,
            "gradedAt": graded_at,
            "score": score,
            "feedback": feedback,
            "isGraded": is_graded
        }

        try:
            submissions.insert_one(submission)
            print(f"✅ Inserted submission from student {student['userId']} for assignment {assignment['assignmentId']}")
        except Exception as e:
            print(f"❌ Failed to insert submission: {e}")




def update_assignment_grade(submission_id: str, grade: float):
    submissions = db["submissions"]
    submission = submissions.find_one({"submissionId": submission_id})

    if not submission:
        print(f"❌ Submission with ID {submission_id} not found.")
        return

    result = submissions.update_one(
        {"submissionId": submission_id},
        {
            "$set": {
                "grade": grade,
                "gradedAt": utc_now_iso()
            }
        }
    )
    print(f"\n📝 Grade updated for submission {submission_id}: {result.modified_count} document(s) updated.")





create_submissions()
# update_assignment_grade("42e5b615-457d-452e-803a-a15cf44e70b6", 76)
