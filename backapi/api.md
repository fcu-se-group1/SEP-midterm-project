### Check User ID
- **URL:** `/check_user_id`
- **Method:** `POST`
- **Description:** Checks if a user ID exists in the database.
- **Request Body:**
  ```json
  {
    "user_id": "D0000001"
  }
  ```
- **Response:**
  ```json
  {
    "status": "exists",
    "user": {...}
  }
  ```
  or
  ```json
  {
    "status": "not_exists"
  }
  ```

### View Schedule
- **URL:** `/schedule/view_schedule`
- **Method:** `POST`
- **Description:** Retrieves the schedule for a user.
- **Request Body:**
  ```json
  {
    "user_id": "D0000001",
    "actor": "student"
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "schedule": {...},
    "current_credits": 15,
    "min_credits": 12,
    "max_credits": 25
  }
  ```

### Set Enrollment Period
- **URL:** `/set_enrollment_period`
- **Method:** `POST`
- **Description:** Sets the enrollment period for adding or dropping courses.
- **Request Body:**
  ```json
  {
    "period_type": "加選",
    "start_time": "2023-01-01T08:00",
    "end_time": "2023-01-15T17:00"
  }
  ```
- **Response:**
  ```json
  {
    "status": "success"
  }
  ```

### Check Enrollment Period (Registration)
- **URL:** `/registration/check_enrollment_period`
- **Method:** `GET`
- **Description:** Checks if the current time is within the registration period.
- **Response:**
  ```json
  {
    "status": "open",
    "start_time": "2023-01-01T08:00",
    "end_time": "2023-01-15T17:00",
    "now": "2023-01-10T10:00"
  }
  ```
  or
  ```json
  {
    "status": "closed"
  }
  ```

### Check Enrollment Period (Withdrawal)
- **URL:** `/withdraw/check_enrollment_period`
- **Method:** `GET`
- **Description:** Checks if the current time is within the withdrawal period.
- **Response:**
  ```json
  {
    "status": "open",
    "start_time": "2023-01-01T08:00",
    "end_time": "2023-01-15T17:00",
    "now": "2023-01-10T10:00"
  }
  ```
  or
  ```json
  {
    "status": "closed"
  }
  ```

### Check Course Code (Withdrawal)
- **URL:** `/withdraw/check_course_code`
- **Method:** `POST`
- **Description:** Checks if a course code exists for a user in the enrollment table with status "已選".
- **Request Body:**
  ```json
  {
    "course_code": "101",
    "user_id": "D0000001"
  }
  ```
- **Response:**
  ```json
  {
    "status": "exists",
    "course": {...}
  }
  ```
  or
  ```json
  {
    "status": "not_exists"
  }
  ```

### Check Course Code (Registration)
- **URL:** `/registration/check_course_code`
- **Method:** `POST`
- **Description:** Checks if a course code exists in the course table.
- **Request Body:**
  ```json
  {
    "course_code": "101"
  }
  ```
- **Response:**
  ```json
  {
    "status": "exists",
    "course": {...}
  }
  ```
  or
  ```json
  {
    "status": "not_exists"
  }
  ```

### Check Course Availability
- **URL:** `/registration/check_course_availability`
- **Method:** `POST`
- **Description:** Checks if there are available seats in a course.
- **Request Body:**
  ```json
  {
    "course_code": "101"
  }
  ```
- **Response:**
  ```json
  {
    "status": "available"
  }
  ```
  or
  ```json
  {
    "status": "full"
  }
  ```

### Check User Credits (Registration)
- **URL:** `/registration/check_user_credits`
- **Method:** `POST`
- **Description:** Checks if a user can enroll in a course without exceeding the credit limit.
- **Request Body:**
  ```json
  {
    "user_id": "D0000001",
    "course_code": "101",
    "actor": "student"
  }
  ```
- **Response:**
  ```json
  {
    "status": "within_limit"
  }
  ```
  or
  ```json
  {
    "status": "exceeds_limit"
  }
  ```

### Check User Credits (Withdrawal)
- **URL:** `/withdraw/check_user_credits`
- **Method:** `POST`
- **Description:** Checks if a user can withdraw from a course without falling below the credit limit.
- **Request Body:**
  ```json
  {
    "user_id": "D0000001",
    "course_code": "101",
    "actor": "student"
  }
  ```
- **Response:**
  ```json
  {
    "status": "within_limit"
  }
  ```
  or
  ```json
  {
    "status": "exceeds_limit"
  }
  ```

### Check Class Restrictions (Withdrawal)
- **URL:** `/withdraw/check_class_restrictions`
- **Method:** `POST`
- **Description:** Checks if a user can withdraw from a course based on class restrictions.
- **Request Body:**
  ```json
  {
    "user_id": "D0000001",
    "course_code": "101",
    "actor": "student"
  }
  ```
- **Response:**
  ```json
  {
    "status": "restricted"
  }
  ```
  or
  ```json
  {
    "status": "allowed"
  }
  ```

### Check Class Restrictions (Registration)
- **URL:** `/registration/check_class_restrictions`
- **Method:** `POST`
- **Description:** Checks if a user can enroll in a course based on class restrictions.
- **Request Body:**
  ```json
  {
    "user_id": "D0000001",
    "course_code": "101",
    "actor": "student"
  }
  ```
- **Response:**
  ```json
  {
    "status": "restricted"
  }
  ```
  or
  ```json
  {
    "status": "allowed"
  }
  ```

### Check Schedule Conflicts
- **URL:** `/registration/check_schedule_conflicts`
- **Method:** `POST`
- **Description:** Checks if a user's schedule conflicts with a new course.
- **Request Body:**
  ```json
  {
    "user_id": "D0000001",
    "course_code": "101"
  }
  ```
- **Response:**
  ```json
  {
    "status": "conflict"
  }
  ```
  or
  ```json
  {
    "status": "no_conflict"
  }
  ```

### Enroll Course
- **URL:** `/registration/enroll_course`
- **Method:** `POST`
- **Description:** Enrolls a user in a course.
- **Request Body:**
  ```json
  {
    "user_id": "D0000001",
    "course_code": "101"
  }
  ```
- **Response:**
  ```json
  {
    "status

":

 "success"
  }
  ```

### Drop Course
- **URL:** `/withdraw/drop_course`
- **Method:** `POST`
- **Description:** Withdraws a user from a course.
- **Request Body:**
  ```json
  {
    "user_id": "D0000001",
    "course_code": "101"
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "message": "退選成功"
  }
  ```

### Add or Update Course
- **URL:** `/course/add_or_update`
- **Method:** `POST`
- **Description:** Adds or updates a course in the database.
- **Request Body:**
  ```json
  {
    "course_code": "101",
    "course_name": "Mathematics",
    "credits": 3,
    "max_students": 30,
    "instructor_name": "Dr. Smith",
    "location": "Room 101",
    "is_mandatory": true,
    "weekdays": ["Monday", "Wednesday"],
    "time_slots": ["1-2", "1-2"],
    "class_names": ["ClassA", "ClassB"]
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "message": "課程已成功添加或更新"
  }
  ```
  or
  ```json
  {
    "status": "error",
    "message": "該授課教師此時段已有課程，請重新輸入"
  }
  ```
  or
  ```json
  {
    "status": "error",
    "message": "該開課班級不存在，請重新輸入"
  }
  ```

## Running the Application
To run the Flask application, use the following command:
```bash
python backapi.py
```
Make sure you have the necessary dependencies installed and the SQLite database properly set up.
