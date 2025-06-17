# models/Enrollments.py

enrollment_validator = {
    "bsonType": "object",
    "required": ["enrollmentId", "studentId", "courseId", "enrolledAt", "progress", "status"],
    "properties": {
        "enrollmentId": {"bsonType": "string"},
        "studentId": {"bsonType": "string"},     # Reference to users.userId
        "courseId": {"bsonType": "string"},      # Reference to courses.courseId
        "enrolledAt": {"bsonType": "date"},
        "progress": {
            "bsonType": "double",
            "minimum": 0,
            "maximum": 100
        },
        "status": {
            "enum": ["enrolled", "in_progress", "completed"]
        }
    }
}
