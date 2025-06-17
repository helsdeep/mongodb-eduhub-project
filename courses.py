from faker import Faker
from datetime import timedelta
import uuid
import random

from database.mongo_db import db
from models.Course import course_validator
from utils.timestamp import utc_now_iso


def create_courses():
    if "courses" not in db.list_collection_names():
        db.create_collection("courses")
    db.command("collMod", "courses", validator={"$jsonSchema": course_validator})

    courses = db["courses"]
    courses.create_index("courseId", unique=True)
    courses.create_index([("title", 1), ("category", 1)])


    users = list(db["users"].find({"role": "instructor"}, {"userId": 1}))
    students = list(db["users"].find({"role": "student"}, {"userId": 1}))

    if not users:
        print("❌ Cannot seed courses: no instructors found.")
        return

    fake = Faker()
    levels = ["beginner", "intermediate", "advanced"]
    categories = ["Data Science", "Web Development", "Finance", "DevOps", "Design"]
    tags_pool = ["Python", "MongoDB", "React", "Kubernetes", "Pandas", "Excel"]

    for _ in range(10):
        instructor = random.choice(users)
        created_at = utc_now_iso()
        updated_at = created_at
        is_published = random.choice([True, False])

        course = {
            "courseId": str(uuid.uuid4()),
            "title": fake.sentence(nb_words=5),
            "description": fake.paragraph(nb_sentences=3),
            "instructorId": instructor["userId"],
            "category": random.choice(categories),
            "level": random.choice(levels),
            "duration": round(random.uniform(1.0, 20.0), 1),
            "price": round(random.uniform(10.0, 100.0), 2),
            "tags": random.sample(tags_pool, k=random.randint(2, 5)),
            "createdAt": created_at,
            "updatedAt": updated_at,
            "isPublished": is_published,
            "ratings": []
        }

        # Add ratings only if the course is published
        if is_published and students:
            for _ in range(random.randint(2, 6)):
                student = random.choice(students)
                course["ratings"].append({
                    "studentId": student["userId"],
                    "rating": round(random.uniform(1.0, 5.0), 1),
                    "ratedAt": utc_now_iso()
                })

        try:
            courses.insert_one(course)
            print(f"✅ Inserted course: {course['title']} (Published: {course['isPublished']})")
        except Exception as e:
            print(f"❌ Failed to insert course: {e}")




def create_single_course():
    # Ensure users collection and instructor reference
    user = db["users"]
    instructor = user.find_one({"role": "instructor"})
    students = list(db["users"].find({"role": "student"}, {"userId": 1}))

    if not instructor:
        print("❌ Cannot add courses: missing or invalid instructor.")
        return

    # Create or modify 'courses' collection with validator
    if "courses" not in db.list_collection_names():
        db.create_collection("courses")
    db.command("collMod", "courses", validator={"$jsonSchema": course_validator})

    courses = db["courses"]
    courses.create_index("courseId", unique=True)

    fake = Faker()
    levels = ["beginner", "intermediate", "advanced"]
    categories = ["Data Science", "Web Development", "Finance", "DevOps", "Design"]
    tags_pool = ["Python", "MongoDB", "React", "Kubernetes", "Pandas", "Excel"]
    created_at = utc_now_iso() - timedelta(days=random.randint(1, 30))
    updated_at = created_at + timedelta(days=random.randint(0, 5))
    is_published = random.choice([True, False])

    course = {
            "courseId": str(uuid.uuid4()),
            "title": fake.sentence(nb_words=5),
            "description": fake.paragraph(nb_sentences=3),
            "instructorId": instructor["userId"],
            "category": random.choice(categories),
            "level": random.choice(levels),
            "duration": round(random.uniform(1.0, 20.0), 1),
            "price": round(random.uniform(10.0, 100.0), 2),
            "tags": random.sample(tags_pool, k=random.randint(2, 5)),
            "rating": [],
            "createdAt": created_at,
            "updatedAt": updated_at,
            "isPublished": random.choice([True, False])
        }
    
    if is_published and students:
            for _ in range(random.randint(2, 6)):
                student = random.choice(students)
                course["ratings"].append({
                    "studentId": student["userId"],
                    "rating": round(random.uniform(1.0, 5.0), 1),
                    "ratedAt": utc_now_iso()
                })

    try:
            courses.insert_one(course)
            print(f"✅ Inserted course: {course['title']} (Instructor: {course['instructorId']})")
    except Exception as e:
            print(f"❌ Failed to insert course: {e}")



def get_course_with_instructor():
    result = db["courses"].aggregate([
        {
            "$lookup": {
                "from": "users",
                "localField": "instructorId",
                "foreignField": "userId",
                "as": "instructor"
            }
        },
        { "$unwind": "$instructor" },
        {
            "$project": {
                "_id": 0,
                "courseId": 1,
                "title": 1,
                "category": 1,
                "level": 1,
                "instructor.firstName": 1,
                "instructor.lastName": 1,
                "instructor.email": 1
            }
        }
    ])

    print("\n📗 Courses with Instructor Info:")
    for course in result:
        print(course)



def get_courses_by_category(category: str):
    courses = db["courses"].find(
        {"category": category},
        {"_id": 0, "courseId": 1, "title": 1, "category": 1}
    )

    print(f"\n📙 Courses in '{category}' Category:")
    for course in courses:
        print(course)



def search_courses_by_title(query: str):
    regex_query = {"$regex": query, "$options": "i"}  # Case-insensitive
    courses = db["courses"].find(
        {"title": regex_query},
        {"_id": 0, "courseId": 1, "title": 1}
    )

    print(f"\n🔍 Courses matching '{query}':")
    for course in courses:
        print(course)



def publish_course(course_id: str):
    courses = db["courses"]
    course = courses.find_one({"courseId": course_id})

    if not course:
        print(f"❌ Course with ID {course_id} not found.")
        return

    # check for if the courseId provided is already published and does not publish it
    if course.get("isPublished"):
        print(f"⚠️ Course '{course_id}' is already published. No action taken.")
        return

    result = courses.update_one(
        {"courseId": course_id},
        {
            "$set": {
                "isPublished": True,
                "updatedAt": utc_now_iso()
            }
        }
    )
    print(f"\n📢 Course '{course_id}' marked as published: {result.modified_count} document(s) updated.")



def add_tags_to_course(course_id: str, new_tags: list):
    courses = db["courses"]
    course = courses.find_one({"courseId": course_id})

    if not course:
        print(f"❌ Course with ID {course_id} not found.")
        return
    
    result = courses.update_one(
        {"courseId": course_id},
        {
            "$addToSet": {
                "tags": { "$each": new_tags }
            },
            "$set": {
                "updatedAt": utc_now_iso()
            }
        }
    )
    print(f"\n🏷️ Tags added to course {course_id}: {result.modified_count} document(s) updated.")



def get_courses_in_price_range(min_price=50, max_price=200):
    courses = db["courses"]
    results = courses.find({"price": {"$gte": min_price, "$lte": max_price}}, {"_id": 0, "courseId": 1, "price": 1})
    print("\n📘 Courses within price range:")
    for course in results:
        print(course)
    return list(results)



def get_courses_by_tags(tag_list):
    courses = db["courses"]
    results = courses.find({"tags": {"$in": tag_list}}, {"_id": 0, "courseId": 1, "tags": 1})

    print("\n📘 Users who joined in the last 6 months:")
    for course in results:
        print(course)
    return list(results)




def average_course_rating():
    pipeline = [
        {
            "$match": {
                "ratings": {"$exists": True, "$ne": []}
            }
        },
        {
            "$project": {
                "courseId": 1,
                "title": 1,
                "averageRating": {"$avg": "$ratings.rating"},
                "numRatings": {"$size": "$ratings"}
            }
        },
        {
            "$sort": {"averageRating": -1}
        }
    ]

    results = db["courses"].aggregate(pipeline)

    print("⭐ Course Ratings Summary:")
    for doc in results:
        print(f"{doc['title']} ({doc['courseId']}): Avg Rating = {doc['averageRating']:.2f} from {doc['numRatings']} ratings")





def courses_grouped_by_category():
    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "totalCourses": {"$sum": 1}
            }
        },
        {
            "$sort": {"totalCourses": -1}
        }
    ]

    results = db["courses"].aggregate(pipeline)

    print("📂 Courses Grouped by Category:")
    for doc in results:
        print(f"Category: {doc['_id']} — Total Courses: {doc['totalCourses']}")




def average_rating_per_instructor():
    pipeline = [
        {
            "$unwind": "$ratings"
        },
        {
            "$group": {
                "_id": "$instructorId",
                "averageRating": {"$avg": "$ratings.rating"},
                "numRatings": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "instructorId": "$_id",
                "averageRating": {"$round": ["$averageRating", 2]},
                "numRatings": 1
            }
        },
        {"$sort": {"averageRating": -1}}
    ]

    results = db["courses"].aggregate(pipeline)

    print("⭐ Average Rating per Instructor:")
    for doc in results:
        print(f"Instructor: {doc['instructorId']} — Avg: {doc['averageRating']} ({doc['numRatings']} ratings)")




def popular_course_categories():
    pipeline = [
        {
            "$lookup": {
                "from": "courses",
                "localField": "courseId",
                "foreignField": "courseId",
                "as": "course_info"
            }
        },
        {"$unwind": "$course_info"},
        {
            "$group": {
                "_id": "$course_info.category",
                "enrollments": {"$sum": 1}
            }
        },
        {"$sort": {"enrollments": -1}}
    ]

    results = db["enrollments"].aggregate(pipeline)
    print("📚 Most Popular Course Categories:")
    for doc in results:
        print(f"{doc['_id']}: {doc['enrollments']} enrollments")




def create_course_index_title_category():
    db['courses'].create_index([("title", 1), ("category", 1)])
    return

# create_courses()
# create_single_course()
# get_course_with_instructor()
# get_courses_by_category("Finance")
# search_courses_by_title("det")
# publish_course("c481152b-5ee5-4f68-a4ac-a66ff84dc62d")
# add_tags_to_course("7d197809-a4f5-4669-9ea6-e76a2e6d8f57", ['Pymongo', 'SQL'])
# get_courses_in_price_range()
# get_courses_by_tags(["Python", "MongoDB"])
# average_course_rating()
# courses_grouped_by_category()
# average_rating_per_instructor()
# popular_course_categories()
# create_course_index_title_category()