# models/Assignments.py

assignment_validator = {
    "bsonType": "object",
    "required": ["assignmentId", "courseId", "title", "description", "createdAt", "dueDate"],
    "properties": {
        "assignmentId": {"bsonType": "string"},
        "courseId": {"bsonType": "string"},  # Reference to courses.courseId
        "title": {"bsonType": "string"},
        "description": {"bsonType": "string"},
        "createdAt": {"bsonType": "date"},
        "dueDate": {"bsonType": "date"},
        "maxScore": {
            "bsonType": "int",
            "minimum": 1
        },
        "isPublished": {"bsonType": "bool"}
    }
}
