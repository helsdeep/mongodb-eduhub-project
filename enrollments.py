from datetime import timedelta
import uuid
import random

from database.mongo_db import db
from models.Enrollment import enrollment_validator
from utils.timestamp import utc_now_iso


def create_enrollments():
    if "enrollments" not in db.list_collection_names():
        db.create_collection("enrollments")
    db.command("collMod", "enrollments", validator={"$jsonSchema": enrollment_validator})

    enrollments = db["enrollments"]
    enrollments.create_index("enrollmentId", unique=True)
    enrollments.create_index([("studentId", 1), ("courseId", 1)], unique=True)

    users = list(db["users"].find({"role": "student"}, {"userId": 1}))
    courses = list(db["courses"].find({"isPublished": True}, {"courseId": 1}))

    if not users or not courses:
        print("❌ Cannot seed enrollments: missing users or courses.")
        return

    statuses = ["enrolled", "in_progress", "completed"]

    for i in range(15):
        student = random.choice(users)
        course = random.choice(courses)
        enrolled_at = utc_now_iso() - timedelta(days=random.randint(1, 30))
        status = random.choice(statuses)
        progress = {
            "enrolled": 0.0,
            "in_progress": round(random.uniform(10.0, 90.0), 1),
            "completed": 100.0
        }[status]

        enrollment = {
            "enrollmentId": str(uuid.uuid4()),
            "studentId": student["userId"],
            "courseId": course["courseId"],
            "enrolledAt": enrolled_at,
            "progress": progress,
            "status": status
        }

        try:
            enrollments.insert_one(enrollment)
            print(f"✅ Enrolled {student['userId']} in course {course['courseId']}")
        except Exception as e:
            print(f"❌ Failed to insert enrollment: {e}")



def enroll_student(user_id: str, course_id: str):
    #creates the enrollments collection with the enrollment validator if enrollment collection is not present in the database
    if "enrollments" not in db.list_collection_names():
        db.create_collection("enrollments")
    db.command("collMod", "enrollments", validator={"$jsonSchema": enrollment_validator})

    enrollments = db["enrollments"]
    enrollments.create_index("enrollmentId", unique=True)
    enrollments.create_index([("studentId", 1), ("courseId", 1)], unique=True)

    student = db["users"].find_one({"userId": user_id}, {"userId": 1, "role": 1})
    course = db["courses"].find_one({"courseId": course_id}, {"courseId": 1, "isPublished": 1})
    user = db["users"].find_one({"role": "student"}, {"userId": 1, "role": 1})

    if not student or not course or not user:
        print("❌ Cannot add enrollment: missing/invalid user or course.")
        return
    
    if student['role'] != user['role']:
        print("❌ Cannot add enrollment: This user is not a student")
        return    

    
    if not course['isPublished']:
        print("❌ Cannot add enrollment: course is not published")
        return
    
    existing = enrollments.find_one({
        "studentId": student["userId"],
        "courseId": course["courseId"]
    })

    if existing:
        print(f"⚠️ Student {student['userId']} is already enrolled in course {course['courseId']}")
        return

    enrollment = {
        "enrollmentId": str(uuid.uuid4()),
        "studentId": student['userId'],
        "courseId": course['courseId'],
        "enrolledAt": utc_now_iso(),
        "progress": 0.0,
        "status": "enrolled"
    }

    try:
        enrollments.insert_one(enrollment)
        print(f"✅ Enrolled {student['userId']} in course {course['courseId']}")
    except Exception as e:
        print(f"❌ Failed to insert enrollment: {e}")
    


def delete_enrollment(enrollment_id: str):
    enrollments = db["enrollments"]
    result = enrollments.delete_one({"enrollmentId": enrollment_id})

    if result.deleted_count:
        print(f"✅ Enrollment '{enrollment_id}' deleted successfully.")
    else:
        print(f"❌ Enrollment '{enrollment_id}' not found.")




def enrollment_stats_per_course():
    pipeline = [
        {
            "$group": {
                "_id": "$courseId",
                "totalEnrollments": {"$sum": 1}
            }
        },
        {
            "$sort": {"totalEnrollments": -1}
        }
    ]

    results = db["enrollments"].aggregate(pipeline)

    print("📊 Total Enrollments per Course:")
    for doc in results:
        print(f"Course ID: {doc['_id']} — Enrollments: {doc['totalEnrollments']}")



def course_completion_rate():
    pipeline = [
        {
            "$group": {
                "_id": "$courseId",
                "total": {"$sum": 1},
                "completed": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}}
            }
        },
        {
            "$project": {
                "completionRate": {
                    "$cond": [
                        {"$eq": ["$total", 0]},
                        0,
                        {"$round": [{"$multiply": [{"$divide": ["$completed", "$total"]}, 100]}, 1]}
                    ]
                },
                "total": 1,
                "completed": 1
            }
        },
        {"$sort": {"completionRate": -1}}
    ]

    results = db["enrollments"].aggregate(pipeline)

    print("✅ Completion Rate by Course (%):")
    for doc in results:
        print(f"Course ID: {doc['_id']} | {doc['completed']} completed out of {doc['total']} — {doc['completionRate']}%")



def total_students_per_instructor():
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
                "_id": "$course_info.instructorId",
                "studentsTaught": {"$addToSet": "$studentId"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "instructorId": "$_id",
                "totalStudents": {"$size": "$studentsTaught"}
            }
        },
        {"$sort": {"totalStudents": -1}}
    ]

    results = db["enrollments"].aggregate(pipeline)

    print("👨‍🏫 Total Students Taught by Instructor:")
    for doc in results:
        print(f"Instructor: {doc['instructorId']} — {doc['totalStudents']} students")




def revenue_per_instructor():
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
                "_id": "$course_info.instructorId",
                "totalRevenue": {"$sum": "$course_info.price"},
                "enrollments": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "instructorId": "$_id",
                "totalRevenue": {"$round": ["$totalRevenue", 2]},
                "enrollments": 1
            }
        },
        {"$sort": {"totalRevenue": -1}}
    ]

    results = db["enrollments"].aggregate(pipeline)

    print("💰 Revenue per Instructor:")
    for doc in results:
        print(f"Instructor: {doc['instructorId']} — ${doc['totalRevenue']} from {doc['enrollments']} enrollments")



def monthly_enrollment_trends():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$enrolledAt"},
                    "month": {"$month": "$enrolledAt"}
                },
                "totalEnrollments": {"$sum": 1}
            }
        },
        {
            "$sort": {
                "_id.year": 1,
                "_id.month": 1
            }
        }
    ]

    results = db["enrollments"].aggregate(pipeline)
    print("📈 Monthly Enrollment Trends:")
    for doc in results:
        year = doc["_id"]["year"]
        month = doc["_id"]["month"]
        print(f"{year}-{month:02d}: {doc['totalEnrollments']} enrollments")



# create_enrollments()
enroll_student(9, "6ea29704-fe4c-45ef-b842-a5df5134367f")
# delete_enrollment("")
# enrollment_stats_per_course()
# course_completion_rate()
# total_students_per_instructor()
# revenue_per_instructor()
# monthly_enrollment_trends()