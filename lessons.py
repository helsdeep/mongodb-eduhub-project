from faker import Faker
import uuid
import random

from database.mongo_db import db
from models.Lesson import lesson_validator
from utils.timestamp import utc_now_iso


def create_lessons():
    if "lessons" not in db.list_collection_names():
        db.create_collection("lessons")
    db.command("collMod", "lessons", validator={"$jsonSchema": lesson_validator})

    lessons = db["lessons"]
    lessons.create_index("lessonId", unique=True)

    courses = list(db["courses"].find({}, {"courseId": 1, "title": 1}))
    if not courses:
        print("❌ No courses found to assign lessons.")
        return

    fake = Faker()
    total_lessons = 25
    lesson_counter = 0

    while lesson_counter < total_lessons:
        course = random.choice(courses)
        position = lessons.count_documents({"courseId": course["courseId"]}) + 1

        lesson = {
            "lessonId": str(uuid.uuid4()),
            "courseId": course["courseId"],
            "title": fake.sentence(nb_words=5),
            "content": fake.paragraph(nb_sentences=5),
            "duration": random.randint(5, 20),  # in minutes
            "position": position,
            "createdAt": utc_now_iso(),
            "updatedAt": utc_now_iso()
        }

        try:
            lessons.insert_one(lesson)
            lesson_counter += 1
            print(f"✅ [{lesson_counter}/25] Inserted lesson for course {course['courseId']}")
        except Exception as e:
            print(f"❌ Failed to insert lesson: {e}")




def add_lesson_to_course():
    # Ensure lessons collection exists with validator
    if "lessons" not in db.list_collection_names():
        db.create_collection("lessons")
    db.command("collMod", "lessons", validator={"$jsonSchema": lesson_validator})

    lessons = db["lessons"]
    lessons.create_index("lessonId", unique=True)

    # Fetch a course to attach the lesson to
    course = db["courses"].find_one()
    if not course:
        print("❌ No course found to add a lesson.")
        return

    # Determine next lesson position for this course
    current_position = lessons.count_documents({"courseId": course["courseId"]}) + 1

    fake = Faker()

    lesson = {
        "lessonId": str(uuid.uuid4()),
        "courseId": course["courseId"],
        "title": fake.sentence(nb_words=5),
        "content": fake.paragraph(nb_sentences=5),
        "duration": fake.random_int(min=5, max=20),  # in minutes
        "position": current_position,
        "createdAt": utc_now_iso(),
        "updatedAt": utc_now_iso()
    }

    try:
        lessons.insert_one(lesson)
        print(f"✅ Added lesson {lesson['title']} to course {course['courseId']} (Position {current_position})")
    except Exception as e:
        print(f"❌ Failed to add lesson: {e}")



def delete_lesson(lesson_id: str):
    lessons = db["lessons"]
    result = lessons.delete_one({"lessonId": lesson_id})

    if result.deleted_count:
        print(f"✅ Lesson '{lesson_id}' removed from course.")
    else:
        print(f"❌ Lesson '{lesson_id}' not found.")





create_lessons()
# add_lesson_to_course()
# delete_lesson("")