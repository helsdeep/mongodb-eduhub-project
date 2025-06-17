from faker import Faker
from datetime import timedelta
import uuid
import random

from database.mongo_db import db
from models.Assignment import assignment_validator
from utils.timestamp import utc_now_iso


def create_assignments():
    if "assignments" not in db.list_collection_names():
        db.create_collection("assignments")
    db.command("collMod", "assignments", validator={"$jsonSchema": assignment_validator})

    assignments = db["assignments"]
    assignments.create_index("assignmentId", unique=True)
    assignments.create_index("dueDate")

    courses = list(db["courses"].find({}, {"courseId": 1}))
    if not courses:
        print("❌ No courses found to assign assignments.")
        return

    fake = Faker()

    for i in range(10):
        course = random.choice(courses)
        created_at = utc_now_iso() - timedelta(days=random.randint(1, 60))
        due_date = created_at + timedelta(days=random.randint(7, 30))

        assignment = {
            "assignmentId": str(uuid.uuid4()),
            "courseId": course["courseId"],
            "title": fake.sentence(nb_words=6),
            "description": fake.paragraph(),
            "createdAt": created_at,
            "dueDate": due_date,
            "maxScore": random.randint(50, 100),
            "isPublished": random.choice([True, False])
        }

        try:
            assignments.insert_one(assignment)
            print(f"✅ Inserted assignment: {assignment['title']} for course {course['courseId']}")
        except Exception as e:
            print(f"❌ Failed to insert assignment: {e}")




def get_upcoming_assignments():
    assignments = db["assignments"]
    now = utc_now_iso()
    next_week = now + timedelta(days=7)

    results = assignments.find({
        "dueDate": {
            "$gte": now,
            "$lte": next_week
        }
    }, {"_id": 0, "assignmentId": 1, "title": 1})

    print("\n📘 Assignments due next week:")
    for assignment in results:
        print(assignment)
    return list(results)


def create_index_due_date():
    db["assignments"].create_index("dueDate")
    return



# create_assignments()
# get_upcoming_assignments()
# create_index_due_date()