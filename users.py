from faker import Faker
import uuid
import random
from datetime import timedelta

from database.mongo_db import db
from models.User import user_validator
from utils.timestamp import utc_now_iso


def create_users():
    # Create or modify the 'users' collection with validator
    if "users" not in db.list_collection_names():
        db.create_collection("users")
    db.command("collMod", "users", validator={"$jsonSchema": user_validator})

    users = db["users"]
    users.create_index("userId", unique=True)
    users.create_index("email", unique=True)

    fake = Faker()
    roles = ["student", "instructor"]
    skills_pool = ["Python", "MongoDB", "Data Analysis", "Machine Learning", "Web Development"]

    for i in range(20):
        role = random.choice(roles)
        user = {
            "userId": str(uuid.uuid4()),
            "email": fake.unique.email(),
            "firstName": fake.first_name(),
            "lastName": fake.last_name(),
            "role": role,
            "dateJoined": utc_now_iso(),
            "updatedAt": None,
            "profile": {
                "bio": fake.sentence(),
                "avatar": fake.image_url(),
                "skills": random.sample(skills_pool, k=random.randint(1, 4))
            },
            "isActive": random.choice([True, False])
        }

        try:
            users.insert_one(user)
            print(f"✅ Inserted user: {user['firstName']} {user['lastName']} ({role})")
        except Exception as e:
            print(f"❌ Failed to insert user: {e}")



def create_single_user():
    new_user = {
        "userId": str(uuid.uuid4()),
        "email": "newstudent@example.com",
        "firstName": "Lara",
        "lastName": "Ogunleye",
        "role": "student",
        "dateJoined": utc_now_iso(),
        "updatedAt": None,
        "profile": {
            "bio": "Eager learner passionate about cloud computing.",
            "avatar": "",
            "skills": ["Python", "Docker"]
        },
        "isActive": True
    }

    result = db["users"].insert_one(new_user)
    print(f"✅ New student added with _id: {result.inserted_id}")


def find_active_students():
    users = db["users"]
    active_students = users.find({
        "role": "student",
        "isActive": True
    }, {
        "_id": 0,
        "userId": 1,
        "firstName": 1,
        "lastName": 1,
        "dateJoined": 1,
        "email": 1
    })

    print("\n📘 Active Students:")
    for student in active_students:
        print(student)




def get_students_in_course(course_id: str):
    result = db["enrollments"].aggregate([
        { "$match": { "courseId": course_id } },
        {
            "$lookup": {
                "from": "users",
                "localField": "studentId",
                "foreignField": "userId",
                "as": "student"
            }
        },
        { "$unwind": "$student" },
        {
            "$project": {
                "_id": 0,
                "student.userId": 1,
                "student.firstName": 1,
                "student.lastName": 1,
                "student.email": 1,
                "status": 1
            }
        }
    ])

    print(f"\n📒 Students enrolled in course {course_id}:")
    for entry in result:
        print(entry)




def update_user_profile(user_id: str, bio: str, avatar: str, skills: list):
    result = db["users"].update_one(
        {"userId": user_id},
        {
            "$set": {
                "profile.bio": bio,
                "profile.avatar": avatar,
                "profile.skills": skills,
                "updatedAt": utc_now_iso()
            }
        }
    )
    print(f"\n👤 Profile update result for {user_id}: {result.modified_count} document(s) updated.")



def soft_delete_user(user_id: str):
    users = db["users"]

    user = users.find_one({"userId": user_id}, {"userId": 1, "isActive": 1})

    if not user:
        print(f"❌ User '{user_id}' not found.")
        return

    if not user['isActive']:
        print(f"⚠️ User '{user['userId']}' is already inactive.")
        return

    result = users.update_one(
        {"userId": user_id},
        {"$set": {"isActive": False, "updatedAt": utc_now_iso()}}
    )

    if result.modified_count:
        print(f"✅ User '{user_id}' marked as inactive.")
    else:
        print(f"❌ Failed to update user '{user_id}'.")



def get_recent_users(months=6):
    users = db["users"]
    six_months_ago = utc_now_iso() - timedelta(days=30 * months)

    results = users.find({
        "dateJoined": {"$gte": six_months_ago}
    }, {"_id": 0, "userId": 1, "firstName": 1, "lastName": 1})

    print("\n📘 Users who joined in the last 6 months:")
    for user in results:
        print(user)
    return list(results)


def average_grade_per_student():
    pipeline = [
        {"$match": {"score": {"$ne": None}}},  # Only graded submissions
        {
            "$group": {
                "_id": "$studentId",
                "averageScore": {"$avg": "$score"},
                "submissionsGraded": {"$sum": 1}
            }
        },
        {"$sort": {"averageScore": -1}}
    ]

    results = db["submissions"].aggregate(pipeline)

    print("📊 Average Grade per Student:")
    for doc in results:
        print(f"Student ID: {doc['_id']} | Avg Score: {doc['averageScore']:.2f} | Graded Submissions: {doc['submissionsGraded']}")




def top_performing_students_with_names(limit=5):
    pipeline = [
        {"$match": {"score": {"$ne": None}}},
        {
            "$group": {
                "_id": "$studentId",
                "averageScore": {"$avg": "$score"},
                "submissionsCount": {"$sum": 1}
            }
        },
        {"$sort": {"averageScore": -1}},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "userId",
                "as": "userInfo"
            }
        },
        {"$unwind": "$userInfo"},
        {
            "$project": {
                "_id": 0,
                "studentId": "$_id",
                "averageScore": 1,
                "submissionsCount": 1,
                "firstName": "$userInfo.firstName",
                "lastName": "$userInfo.lastName",
                "email": "$userInfo.email"
            }
        }
    ]

    results = db["submissions"].aggregate(pipeline)

    print(f"🏆 Top {limit} Performing Students (with names):")
    for doc in results:
        print(
            f"{doc['firstName']} {doc['lastName']} ({doc['email']}) "
            f"| Avg Score: {doc['averageScore']:.2f} "
            f"| Submissions: {doc['submissionsCount']}"
        )




def student_engagement_metrics():
    pipeline = [
        {
            "$group": {
                "_id": "$studentId",
                "submissionsMade": {"$sum": 1},
                "averageScore": {"$avg": "$score"}
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "userId",
                "as": "student_info"
            }
        },
        {"$unwind": "$student_info"},
        {
            "$project": {
                "studentId": "$_id",
                "name": {
                    "$concat": ["$student_info.firstName", " ", "$student_info.lastName"]
                },
                "submissionsMade": 1,
                "averageScore": {"$round": ["$averageScore", 2]}
            }
        },
        {"$sort": {"submissionsMade": -1}}
    ]

    results = db["submissions"].aggregate(pipeline)
    print("📊 Student Engagement:")
    for doc in results:
        print(f"{doc['name']} — {doc['submissionsMade']} submissions, Avg Score: {doc['averageScore']}")




# create_users()
# create_single_user()
# find_active_students()
# get_students_in_course("43fe060a-a921-468c-8e00-5ae7d947723f")
# update_user_profile()
# soft_delete_user("1eeccd9f-bba5-4a69-82bc-da723955fdb9")
# get_recent_users()
# average_grade_per_student()
# top_performing_students_with_names()
student_engagement_metrics()