submission_validator = {
    "bsonType": "object",
    "required": ["submissionId", "assignmentId", "studentId", "submittedAt"],
    "properties": {
        "submissionId": {"bsonType": "string"},
        "assignmentId": {"bsonType": "string"},  # Reference to assignments
        "studentId": {"bsonType": "string"},     # Reference to users
        "submittedAt": {"bsonType": "date"},
        "gradedAt": {"bsonType": ["date", "null"]},
        "score": {"bsonType": "int", "minimum": 0},
        "feedback": {"bsonType": "string"},
        "isGraded": {"bsonType": "bool"}
    }
}
