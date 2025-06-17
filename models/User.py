user_validator = {
    "bsonType": "object",
    "required": ["userId", "email", "firstName", "lastName", "role", "updatedAt"],
    "properties": {
        "userId": {
            "bsonType": "string",
            "description": "Unique user identifier"
        },
        "email": {
            "bsonType": "string",
            "pattern": "^.+@.+\\..+$",
            "description": "Valid email address"
        },
        "firstName": {
            "bsonType": "string",
            "description": "First name is required"
        },
        "lastName": {
            "bsonType": "string",
            "description": "Last name is required"
        },
        "role": {
            "enum": ["student", "instructor"],
            "description": "Role must be student or instructor"
        },
        "dateJoined": {
            "bsonType": "date",
            "description": "User join date"
        },
        "updatedAt": {
            "bsonType": ["date", "null"],
            "description": "Last user information update date"
        },
        "profile": {
            "bsonType": "object",
            "properties": {
                "bio": {"bsonType": "string"},
                "avatar": {"bsonType": "string"},
                "skills": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                }
            }
        },
        "isActive": {
            "bsonType": "bool",
            "description": "Boolean for account status"
        }
    }
}
