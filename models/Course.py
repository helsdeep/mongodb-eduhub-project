course_validator = {
    "bsonType": "object",
    "required": ["courseId", "title", "description", "instructorId", "category", "level", "duration", "price", "tags", "createdAt", "updatedAt", "isPublished"],
    "properties": {
        "courseId": {
            "bsonType": "string",
            "description": "Unique identifier for the course"
        },
        "title": {
            "bsonType": "string",
            "description": "Course title"
        },
        "description": {
            "bsonType": "string",
            "description": "Detailed course description"
        },
        "instructorId": {
            "bsonType": "string",
            "description": "Reference to instructor in users collection"
        },
        "category": {
            "bsonType": "string",
            "description": "Subject category"
        },
        "level": {
            "enum": ["beginner", "intermediate", "advanced"],
            "description": "Course difficulty level"
        },
        "duration": {
            "bsonType": "double",
            "minimum": 0,
            "description": "Duration of course in hours"
        },
        "price": {
            "bsonType": "double",
            "minimum": 0,
            "description": "Price in USD"
        },
        "tags": {
            "bsonType": "array",
            "items": {
                "bsonType": "string"
            },
            "description": "Relevant keywords for filtering"
        },
        "ratings": {
            "bsonType": "array",
            "items": {
                "bsonType": "object",
                "required": ["studentId", "rating", "ratedAt"],
                "properties": {
                    "studentId": {
                        "bsonType": "string",
                        "description": "Student who gave the rating"
                    },
                    "rating": {
                        "bsonType": "double",
                        "minimum": 1.0,
                        "maximum": 5.0,
                        "description": "Rating score (1.0 - 5.0)"
                    },
                    "ratedAt": {
                        "bsonType": "date",
                        "description": "Timestamp of the rating"
                    }
                }
            },
            "description": "User-generated course reviews"
        },
        "createdAt": {
            "bsonType": "date",
            "description": "Course creation timestamp"
        },
        "updatedAt": {
            "bsonType": "date",
            "description": "Last update timestamp"
        },
        "isPublished": {
            "bsonType": "bool",
            "description": "Publish status"
        }
    }
}
