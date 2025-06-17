lesson_validator = {
    "bsonType": "object",
    "required": ["lessonId", "courseId", "title", "position", "createdAt"],
    "properties": {
        "lessonId": {"bsonType": "string"},
        "courseId": {"bsonType": "string"},  # Reference to courses
        "title": {"bsonType": "string"},
        "content": {"bsonType": "string"},
        "duration": {"bsonType": "int", "minimum": 1},  # in minutes
        "position": {"bsonType": "int", "minimum": 1},
        "createdAt": {"bsonType": "date"},
        "updatedAt": {"bsonType": "date"}
    }
}
