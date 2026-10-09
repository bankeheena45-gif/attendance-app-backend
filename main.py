from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import connection
from datetime import datetime

app = FastAPI()


# -------------------------------
# Request models
# -------------------------------

class TeacherRegister(BaseModel):
    name: str
    email: str
    password: str


class TeacherLogin(BaseModel):
    email: str
    password: str


class StudentRegister(BaseModel):
    name: str
    roll_number: str
    class_name: str
    section: str
    face_data: str


class AttendanceCreate(BaseModel):
    student_id: int
    subject: str


# -------------------------------
# Teacher registration
# -------------------------------

@app.post("/teacher/register")
def register(teacher: TeacherRegister):
    cursor = connection.cursor()

    sql = """
        INSERT INTO teachers (name, email, password)
        VALUES (%s, %s, %s)
    """

    values = (
        teacher.name,
        teacher.email,
        teacher.password
    )

    cursor.execute(sql, values)
    connection.commit()
    cursor.close()

    return {"message": "Teacher registered successfully"}


# -------------------------------
# Teacher login
# -------------------------------

@app.post("/teacher/login")
def login(teacher: TeacherLogin):
    cursor = connection.cursor()

    sql = """
        SELECT * FROM teachers
        WHERE email = %s AND password = %s
    """

    values = (
        teacher.email,
        teacher.password
    )

    cursor.execute(sql, values)
    result = cursor.fetchone()
    cursor.close()

    if result:
        return {"message": "Login successful"}

    return {"message": "Invalid email or password"}


# -------------------------------
# Student registration
# -------------------------------

@app.post("/student/register")
def register_student(student: StudentRegister):
    cursor = connection.cursor()

    sql = """
        INSERT INTO students
        (name, roll_number, class, section, face_data)
        VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        student.name,
        student.roll_number,
        student.class_name,
        student.section,
        student.face_data
    )

    cursor.execute(sql, values)
    connection.commit()
    cursor.close()

    return {"message": "Student registered successfully"}


# -------------------------------
# Get all students
# -------------------------------

@app.get("/students")
def get_students():
    cursor = connection.cursor(dictionary=True)

    sql = """
        SELECT id, name, roll_number, class, section, face_data
        FROM students
        ORDER BY id
    """

    cursor.execute(sql)
    students = cursor.fetchall()
    cursor.close()

    return students


# -------------------------------
# Mark attendance
# -------------------------------

@app.post("/attendance/mark")
def mark_attendance(attendance: AttendanceCreate):
    cursor = connection.cursor(buffered=True)

    current_date = datetime.now().date()
    current_time = datetime.now().time()
    
    cursor.execute(
        "SELECT id FROM students WHERE id = %s",
        (attendance.student_id,)
    )

    student = cursor.fetchone()

    if not student:
        cursor.close()
        raise HTTPException(
              status_code=404,
              detail="Student not found"
)

    cursor.execute("""
        SELECT id FROM attendance
        WHERE student_id = %s
          AND date = %s
          AND LOWER(TRIM(subject)) = LOWER(TRIM(%s))
    """, (
        attendance.student_id,
        current_date,
        attendance.subject
    ))

    existing = cursor.fetchone()

    if existing:
        cursor.close()
        return {
            "message": "Attendance already marked for this subject today"
        }

    sql = """
        INSERT INTO attendance
        (student_id, date, time, subject, status)
        VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        attendance.student_id,
        current_date,
        current_time,
        attendance.subject.strip(),
        "Present"
    )

    cursor.execute(sql, values)
    connection.commit()
    cursor.close()

    return {
    "message": "Attendance marked successfully",
    "student_id": attendance.student_id,
    "subject": attendance.subject.strip(),
    "date": str(current_date),
    "status": "Present"
}

# -------------------------------
# Get attendance with filters
# -------------------------------

@app.get("/attendance")
def get_attendance(date: str = None, subject: str = None):

    cursor = connection.cursor(dictionary=True)

    sql = """
        SELECT
            attendance.id AS attendance_id,
            attendance.student_id,
            students.roll_number,
            students.name,
            students.class,
            students.section,
            attendance.date,
            attendance.time,
            attendance.subject,
            attendance.status
        FROM attendance
        JOIN students
            ON attendance.student_id = students.id
        WHERE 1=1
    """

    values = []

    if date:
        sql += " AND attendance.date = %s"
        values.append(date)

    if subject:
        sql += """
            AND LOWER(TRIM(attendance.subject))
                = LOWER(TRIM(%s))
        """
        values.append(subject.strip())

    sql += """
        ORDER BY attendance.date DESC, attendance.time DESC
    """

    # Debugging information
    print("DATABASE:", connection.database)
    print("SQL:", sql)
    print("VALUES:", values)

    cursor.execute(sql, values)
    records = cursor.fetchall()

    print("RECORDS FOUND:", len(records))
    print("RECORDS:", records)

    cursor.close()

    return records


@app.get("/attendance")
def get_attendance(date: str = None, subject: str = None):

    cursor = connection.cursor(dictionary=True)

    sql = """
    SELECT
        attendance.id AS attendance_id,
        students.roll_number,
        students.name,
        students.class,
        students.section,
        attendance.date,
        TIME_FORMAT(attendance.time, '%H:%i:%s') AS time,
        attendance.subject,
        attendance.status
    FROM attendance
    JOIN students
    ON attendance.student_id = students.id
    WHERE 1=1
    """

    values = []

    if date:
        sql += " AND attendance.date = %s"
        values.append(date)

    if subject:
        sql += " AND LOWER(TRIM(attendance.subject)) = LOWER(TRIM(%s))"
        values.append(subject)

    sql += " ORDER BY attendance.date DESC, attendance.time DESC"

    cursor.execute(sql, values)
    print("SQL:", sql)
    print("VALUES:", values)    
    records = cursor.fetchall()

    for record in records:
      if record["time"] is not None:
        record["time"] = str(record["time"])

    cursor.close()

    return records

    print("DATABASE:", connection.database)
    print("SQL:", sql)
    print("VALUES:", values)

    cursor.execute(sql, values)
    records = cursor.fetchall()

    print("RECORDS FOUND:", len(records))
    print("RECORDS:", records)

    cursor.close()
    return records

