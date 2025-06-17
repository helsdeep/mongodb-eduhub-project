
# EduHub: E-learning Platform Backend

EduHub is a backend project for a robust, MongoDB-based e-learning platform. It covers essential features for managing users, courses, enrollments, lessons, assignments, submissions, and analytics with a focus on scalability, performance, and clean architecture.

---

## 📁 Project Structure

```
edu_hub/
├── database/
│   └── mongo_db.py             # MongoDB connection logic
│
├── models/                    # MongoDB schema validators
│   ├── __init__.py            # Aggregates all schema validators
│   ├── Users.py
│   ├── Courses.py
│   ├── Enrollments.py
│   ├── Lessons.py
│   ├── Assignments.py
│   └── Submissions.py
│
├── utils/
│   └── timestamp.py           # Returns UTC timestamp without microseconds
│
├── users.py                   # Seeder + CRUD + analytics for users
├── courses.py                 # Seeder + CRUD + analytics for courses
├── enrollments.py             # Seeder + analytics for enrollments
├── lessons.py                 # Seeder + CRUD for lessons
├── assignments.py             # Seeder + grade updates
├── submissions.py             # Seeder + scoring analytics
│
├── README.md
└── requirements.txt           # Python dependencies
```

---

## 🛠️ Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/your-username/edu_hub.git
cd edu_hub
```

2. **Create virtual environment & activate it**
```bash
python -m venv venv
source venv/bin/activate    # On Windows use: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up MongoDB**
Ensure MongoDB v8.0+ is installed locally or provide a MongoDB Atlas URI.
Update the connection string in `database/mongo_db.py` accordingly.

5. **Run the seeders**
```bash
python users.py
python courses.py
python enrollments.py
python lessons.py
python assignments.py
python submissions.py
```

---

## 🤩 Features

### ✅ Seeders
- Generates realistic dummy data using `faker`
- Inserts into respective collections with schema validation and integrity checks

### 🔄 CRUD Operations
- Add, read, update, and delete users, courses, lessons, enrollments, assignments, and submissions
- Supports soft deletes (e.g., deactivate user)

### 📊 Aggregation Pipelines
- Average course rating
- Total students per instructor
- Revenue per instructor
- Student engagement
- Completion rates
- Monthly enrollment trends

### 🔍 Advanced Queries
- Search/filter courses by tags, category, and title
- Filter users by date joined or activity
- Time-based lookups for due dates or grades

### ⚡ Indexing & Performance
- Indexes added for email, title, category, dueDate, courseId, and studentId
- Includes `.explain()`-based performance insights

---

## 🧪 Example Commands

### Seed Data:
```bash
python users.py
python courses.py
```

### Add a Lesson to a Course:
```python
from lessons import add_lesson_to_course
add_lesson_to_course(course_id='your-course-id')
```

### Get Top Students:
```python
from submissions import top_performing_students
```

### Search Courses:
```python
from courses import search_courses_by_title
search_courses_by_title("python")
```

---

## 📌 Notes
- All timestamps are stored in UTC without microseconds using `datetime.now(timezone.utc).isoformat(timespec='seconds')`
- All `UUIDs` are generated using `uuid4()`
- Validators ensure strict data integrity in each collection

---

## 📧 Contact
For questions, feel free to contact the project maintainer: **Oluwafemi**

---

Enjoy building with EduHub! 🚀
