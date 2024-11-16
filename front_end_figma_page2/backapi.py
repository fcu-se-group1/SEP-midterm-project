from flask import Flask, request, jsonify, render_template, redirect, url_for
import datetime
import sqlite3
import os

app = Flask(__name__)

def query_db(query, args=(), one=False):
    db_path = os.path.join(os.path.dirname(__file__), '../db/database.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()  # Create the cursor object
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/chooseFunction')
def chooseFunction():
    return render_template('chooseFunction.html')

@app.route('/setTime')
def setTime():
    return render_template('setTime.html')

@app.route('/enterID')
def enterID():
    return render_template('enterID.html')

@app.route('/enterCourseID')
def enterCourseID():
    return render_template('enterCourseID.html')

@app.route('/courseSelectionResult')
def courseSelectionResult():
    return render_template('courseSelectionResult.html')

@app.route('/studentCurriculum')
def studentCurriculum():
    return render_template('/studentCurriculum.html')

@app.route('/adminCurriculum')
def adminCurriculum():
    return render_template('/adminCurriculum.html')

@app.route('/recordCourseInfo')
def recordCourseInfo():
    return render_template('recordCourseInfo.html')

@app.route('/fillOutSyllabus')
def fillOutSyllabus():
    return render_template('fillOutSyllabus.html')

@app.route('/searchCourseInfo')
def searchCourseInfo():
    return render_template('searchCourseInfo.html')

@app.route('/courseInfoResult')
def courseInfoResult():
    return render_template('courseInfoResult.html')

@app.route('/syllabusResult')   
def syllabusResult():
    return render_template('syllabusResult.html')

@app.route('/check_user_id', methods=['POST'])
def check_user_id():
    data = request.json
    user_id = data['user_id']
    user = query_db('SELECT * FROM User WHERE user_id = ?', [user_id], one=True)
    if user:
        return jsonify({'status': 'exists', 'user': user})
    else:
        return jsonify({'status': 'not_exists'})
    
@app.route('/get_user_ids', methods=['GET'])
def get_user_ids():
    user_ids = query_db('SELECT user_id FROM User')
    return jsonify(user_ids)

@app.route('/schedule/view_schedule', methods=['POST'])
def view_schedule():
    data = request.json
    user_id = data['user_id']
    actor = data['actor']
    
    user = query_db('SELECT * FROM User WHERE user_id = ?', [user_id], one=True)
    if not user:
        return jsonify({'status': 'not_exists'})

    selected_courses = query_db('SELECT Course_Schedule.course_code, weekday, time_slot FROM Enrollment JOIN Course_Schedule ON Enrollment.course_code = Course_Schedule.course_code WHERE user_id = ? AND status = ?', [user_id, '已選'])
    registered_courses = query_db('SELECT Course_Schedule.course_code, weekday, time_slot FROM Enrollment JOIN Course_Schedule ON Enrollment.course_code = Course_Schedule.course_code WHERE user_id = ? AND status = ?', [user_id, '已登記'])
    interested_courses = query_db('SELECT Course_Schedule.course_code, weekday, time_slot FROM Enrollment JOIN Course_Schedule ON Enrollment.course_code = Course_Schedule.course_code WHERE user_id = ? AND status = ?', [user_id, '已關注'])

    current_credits = query_db('SELECT SUM(credits) FROM Enrollment JOIN Course ON Enrollment.course_code = Course.course_code WHERE user_id = ?', [user_id], one=True)[0]
    min_credits = 12  # 假設最低學分
    max_credits = 25  # 假設最高學分

    schedule = {
        'selected': [{'code': course[0], 'schedule': [{'day': course[1], 'period': course[2]}]} for course in selected_courses],
        'registered': [{'code': course[0], 'schedule': [{'day': course[1], 'period': course[2]}]} for course in registered_courses],
        'interested': [{'code': course[0], 'schedule': [{'day': course[1], 'period': course[2]}]} for course in interested_courses]
    }

    if actor == 'admin':
        schedule.pop('registered')
        schedule.pop('interested')

    return jsonify({
        'status': 'success',
        'schedule': schedule,
        'current_credits': current_credits,
        'min_credits': min_credits,
        'max_credits': max_credits
    })
    
@app.route('/set_enrollment_period', methods=['POST'])
def set_enrollment_period():
    data = request.json   
    period_type = data['period_type']
    start_time = data['start_time']
    end_time = data['end_time']
    period=query_db('SELECT * FROM EnrollmentPeriod WHERE period_type=?', [period_type], one=True)
    if period:
        query_db('DELETE FROM EnrollmentPeriod WHERE period_type=?', [period_type])
    query_db('INSERT INTO EnrollmentPeriod(period_type, start_time, end_time) VALUES (?, ?, ?)',
                 [period_type, start_time, end_time])
    
    return jsonify({'status': 'success'})

@app.route('/registration/check_enrollment_period', methods=['GET'])
def registration_check_enrollment_period():
    now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8)))
    settime = query_db('SELECT * FROM EnrollmentPeriod WHERE period_type=\"加選\"', one=True)
    starttime = datetime.datetime.strptime(settime[1], "%Y-%m-%dT%H:%M")
    starttime = starttime.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
    endtime = datetime.datetime.strptime(settime[2], "%Y-%m-%dT%H:%M")
    endtime = endtime.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
    if starttime<=now<=endtime:
        return jsonify({'status': 'open', 'start time': starttime, 'end time': endtime, 'now': now})
    else:
        return jsonify({'status': 'closed'})

@app.route('/withdraw/check_enrollment_period', methods=['GET'])
def withdraw_check_enrollment_period():
    now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8)))
    settime = query_db('SELECT * FROM EnrollmentPeriod WHERE period_type="退選"', one=True)
    starttime = datetime.datetime.strptime(settime[1], "%Y-%m-%dT%H:%M")
    starttime = starttime.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
    endtime = datetime.datetime.strptime(settime[2], "%Y-%m-%dT%H:%M")
    endtime = endtime.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
    if starttime <= now <= endtime:
        return jsonify({'status': 'open', 'start_time': starttime, 'end_time': endtime, 'now': now})
    else:
        return jsonify({'status': 'closed'})

@app.route('/enterCourseID/check_addcourse_code', methods=['POST']) #檢查資料庫是否有該課程代碼可以加選
def check_addcourse_code():
    data = request.json
    course_code = data['course_code']
    course = query_db('SELECT * FROM Enrollment WHERE course_code = ?', [course_code], one=True)
    if course:
        return jsonify({'status': 'exists', 'course': course})
    else:
        return jsonify({'status': 'not_exists'})

@app.route('/enterCourseID/check_dropcourse_code', methods=['POST']) #檢查該生課表是否有該課程可以退選
def check_dropcourse_code():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    course = query_db('SELECT * FROM Enrollment WHERE course_code = ? AND user_id = ? AND status = ?', [course_code, user_id, '已選'], one=True)
    if course:
        return jsonify({'status': 'exists', 'message': '該課程已選'})
    else:
        return jsonify({'status': 'not_exists', 'message': '該課程未選'})

@app.route('/enterCourseID/get_user_courses', methods=['POST'])#抓該生選的課程
def get_user_courses():
    data = request.json
    user_id = data['user_id']
    courses = query_db('SELECT course_code FROM Enrollment WHERE user_id = ?', [user_id])
    if courses:
        return jsonify({'status': 'success', 'courses': [course[0] for course in courses]})
    else:
        return jsonify({'status': 'not_exists', 'message': '該用戶沒有選擇任何課程'})

@app.route('/enterCourseID/get_course_code', methods=['GET']) #抓課程代碼到console
def get_course_code():
    course_ids = query_db('SELECT course_code FROM Enrollment')
    return jsonify(course_ids)

@app.route('/withdraw/check_course_code', methods=['POST']) #退選
def withdraw_check_course_code():
    data = request.json
    course_code = data['course_code']
    user_id = data['user_id']
    course = query_db('SELECT * FROM Enrollment WHERE course_code = ? AND user_id =? AND status =?', [course_code,user_id,"已選"], one=True)
    if course:
        return jsonify({'status': 'exists', 'course': course})
    else:
        return jsonify({'status': 'not_exists'})

@app.route('/registration/check_course_code', methods=['POST']) #加選
def registration_check_course_code():
    data = request.json
    course_code = data['course_code']
    course = query_db('SELECT * FROM Course WHERE course_code = ?', [course_code], one=True)
    if course:
        return jsonify({'status': 'exists', 'course': course})
    else:
        return jsonify({'status': 'not_exists'})
    
@app.route('/registration/check_course_availability', methods=['POST'])
def registration_check_course_availability():
    data = request.json
    course_code = data['course_code']
    course = query_db('SELECT max_students FROM Course WHERE course_code = ?', [course_code], one=True)
    nowstudent = query_db("SELECT count(*) from Enrollment where course_code=? and status=?", [course_code, '已選'], one=True)
    print(course[0], nowstudent[0])
    if course[0]- nowstudent[0] > 0:
        return jsonify({'status': 'available'})
    else:
        return jsonify({'status': 'full'})

@app.route('/registration/check_user_credits', methods=['POST'])
def registration_check_user_credits():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    actor = data['actor']
    print(actor)
    course = query_db('SELECT credits FROM Course WHERE course_code = ?', [course_code], one=True)[0]
    current_credits = query_db('SELECT SUM(credits) FROM Enrollment JOIN Course ON Enrollment.course_code = Course.course_code WHERE user_id = ?', [user_id], one=True)[0]
    if current_credits is None:
        current_credits = 0
    if current_credits + course <= 25 and actor=="student":  # Assuming 25 is the credit limit
        return jsonify({'status': 'within_limit'})
    elif current_credits + course <= 30 and actor=="admin":
        return jsonify({'status': 'within_limit'})
    else:
        return jsonify({'status': 'exceeds_limit'})
    
@app.route('/withdraw/check_user_credits', methods=['POST'])
def withdraw_check_user_credits():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    actor = data['actor']
    course_credits = query_db('SELECT credits FROM Course WHERE course_code = ?', [course_code], one=True)[0]
    current_credits = query_db('SELECT SUM(credits) FROM Enrollment JOIN Course ON Enrollment.course_code = Course.course_code WHERE user_id = ?', [user_id], one=True)[0]
    if current_credits is None:
        current_credits = 0
    if current_credits - course_credits >= 12 and actor == "student":  # Assuming 12 is the credit limit
        return jsonify({'status': 'within_limit'})
    elif current_credits - course_credits >= 9 and actor == "admin":
        return jsonify({'status': 'within_limit'})
    else:
        return jsonify({'status': 'exceeds_limit'})
    
@app.route('/withdraw/check_class_restrictions', methods=['POST'])
def withdraw_check_class_restrictions():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    actor = data['actor']
    user_class = query_db('SELECT class FROM User WHERE user_id = ?', [user_id], one=True)[0]
    restriction = query_db('SELECT * FROM Course_Class_Offering WHERE course_code = ? AND class_name = ?', [course_code, user_class], one=True)
    mandatory = query_db("SELECT is_mandatory FROM Course WHERE course_code = ?", [course_code], one=True)[0]
    if restriction and mandatory and actor == "student":
        return jsonify({'status': 'restricted'})
    elif actor == "admin":
        return jsonify({'status': 'allowed'})
    else:
        return jsonify({'status': 'allowed'})
    
@app.route('/registration/check_class_restrictions', methods=['POST'])
def registration_check_class_restrictions():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    atcor = data['actor']
    user = query_db('SELECT class FROM User WHERE user_id = ?', [user_id], one=True)[0]
    restriction = query_db('SELECT * FROM Course_Class_Restriction WHERE course_code = ? AND class_name = ?', [course_code, user], one=True)
    if restriction:
        return jsonify({'status': 'allowed'})
    elif atcor=="admin":
        return jsonify({'status': 'allowed'})
    else:
        return jsonify({'status': 'restricted'})
    
@app.route('/registration/check_schedule_conflicts', methods=['POST'])
def registration_check_schedule_conflicts():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    new_schedule = query_db('SELECT * FROM Course_Schedule WHERE course_code = ?', [course_code])
    current_schedules = query_db('SELECT * FROM Course_Schedule JOIN Enrollment ON Course_Schedule.course_code = Enrollment.course_code WHERE user_id = ?', [user_id])
    for new in new_schedule:
        for current in current_schedules:
            if new[2] == current[2] and new[1] == current[1]:
                return jsonify({'status': 'conflict'})
    return jsonify({'status': 'no_conflict'})

@app.route('/registration/enroll_course', methods=['POST'])
def registration_enroll_course():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    query_db('INSERT INTO Enrollment (course_code, user_id, status) VALUES (?, ?, ?)', [course_code, user_id, '已選'])
    return jsonify({'status': 'success'})

@app.route('/withdraw/drop_course', methods=['POST'])
def withdraw_drop_course():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    query_db('DELETE FROM Enrollment WHERE course_code = ? AND user_id = ?', [course_code, user_id])
    return jsonify({'status': 'success', 'message': '退選成功'})

@app.route('/write_course/check_course_code', methods=['GET', 'POST'])
def write_course_check_course_code():
    if request.method == 'POST':
        course_code = request.form['course_code']
        existing_course = query_db('SELECT * FROM Course WHERE course_code = ?', [course_code], one=True)
        if existing_course:
            return render_template('course_code.html', warning='課程代碼已存在', course_code=course_code)
        else:
            return redirect(url_for('write_course_course_info', course_code=course_code))
    return render_template('course_code.html')

@app.route('/write_course/course_info/<course_code>', methods=['GET', 'POST'])
def write_course_course_info(course_code):
    if request.method == 'POST':
        course_name = request.form['course_name']
        credits = request.form['credits']
        weekdays = request.form.getlist('weekday[]')
        time_slots = request.form.getlist('time_slot[]')
        instructor = request.form['instructor']
        class_names = request.form.getlist('class_name[]')
        location = request.form['location']
        compulsory = request.form['compulsory']
        class_limits = request.form.getlist('class_limit[]')
        max_students = request.form['max_students']

        existing_course = query_db('SELECT * FROM Course WHERE course_code = ?', [course_code], one=True)
        if existing_course:
            query_db('''DELETE FROM Course WHERE course_code = ?''', [course_code])
            query_db('''DELETE FROM Course_Schedule WHERE course_code = ?''', [course_code])
            query_db('''DELETE FROM Course_Class_Offering WHERE course_code = ?''', [course_code])
            query_db('''DELETE FROM Course_Class_Restriction WHERE course_code = ?''', [course_code])
        
        # 檢查授課教師在相同的星期和時間段是否有其他課程
        for w, t in zip(weekdays, time_slots):
            instructor_course_time = query_db('''
                SELECT Course_Schedule.weekday, Course_Schedule.time_slot
                FROM Course
                JOIN Course_Schedule ON Course.course_code = Course_Schedule.course_code
                WHERE Course.instructor_name = ? AND Course_Schedule.weekday = ? AND Course_Schedule.time_slot = ?
            ''', [instructor, w, t])
            if instructor_course_time:
                return render_template('course_info.html', warning='該授課教師此時段已有課程，請重新輸入', course_code=course_code)

        # 檢查開課班級是否存在
        for class_name in class_names:
            is_class_exist = query_db('''SELECT * FROM Class WHERE class_name=?''', [class_name])
            if not is_class_exist:
                return render_template('course_info.html', warning='該開課班級不存在，請重新輸入', course_code=course_code)
            
        # 檢查上課地點
        same_location = query_db('''SELECT course_code FROM Course WHERE location=?''', [location])
        for weekday, time_slot in zip(weekdays, time_slots):
            same_time = query_db('''SELECT course_code FROM Course_Schedule WHERE weekday=? AND time_slot=?''', [weekday, time_slot])
            for sl in same_location:
                for st in same_time:
                    if sl == st:
                        return render_template('course_info.html', warning='該上課地點此時段已有課程，請重新輸入', course_code=course_code)
                
        # 檢查班級限制的班級是否存在
        for class_limit in class_limits:
            is_class_exist = query_db('''SELECT * FROM Class WHERE class_name=?''', [class_limit])
            if not is_class_exist:
                return render_template('course_info.html', warning='班級限制的班級不存在，請重新輸入', course_code=course_code)

        # 檢查最大修課人數
        location_max_students = query_db('''SELECT capacity FROM Location WHERE location_name=?''', [location])
        if int(max_students) > location_max_students[0][0]:
            return render_template('course_info.html', warning='該上課地點無法容納此課程的最大修課人數，請重新輸入', course_code=course_code)

        query_db('''
            INSERT INTO Course (course_code, course_name, credits, max_students, instructor_name, location, is_mandatory)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [course_code, course_name, credits, max_students, instructor, location, compulsory])
        
        for weekday, time_slot in zip(weekdays, time_slots):
            query_db('''
                INSERT INTO Course_Schedule (course_code, weekday, time_slot)
                VALUES (?, ?, ?)
            ''', [course_code, weekday, time_slot])
        
        for class_name in class_names:
            query_db('''
                INSERT INTO Course_Class_Offering (course_code, class_name)
                VALUES (?, ?)
            ''', [course_code, class_name])
        
        for class_limit in class_limits:
            query_db('''
                INSERT INTO Course_Class_Restriction (course_code, class_name)
                VALUES (?, ?)
            ''', [course_code, class_limit])

        return render_template('course_info.html', success='已成功紀錄課程資訊', course_code=course_code)

    return render_template('course_info.html', course_code=course_code)

@app.route('/course_query/check_course_query_input', methods=['GET', 'POST'])
def course_query_check_course_query_input():
    if request.method == 'POST':
        course_code = request.form.get('course_code')
        course_name = request.form.get('course_name')
        instructor = request.form.get('instructor')
        class_name = request.form.get('class_name')
        location = request.form.get('location')
        compulsory = request.form.get('compulsory')
        weekday = request.form.get('weekday')
        time_slot = request.form.get('time_slot')

        query_conditions = []
        query_params = []

        if course_code:
            query_conditions.append("Course.course_code = ?")
            query_params.append(course_code)
        if course_name:
            query_conditions.append("Course.course_name LIKE ?")
            query_params.append(f"%{course_name}%")
        if instructor:
            query_conditions.append("Course.instructor_name LIKE ?")
            query_params.append(f"%{instructor}%")
        if class_name:
            query_conditions.append("Course_Class_Offering.class_name LIKE ?")
            query_params.append(f"%{class_name}%")
        if location:
            query_conditions.append("Course.location LIKE ?")
            query_params.append(f"%{location}%")
        if compulsory:
            query_conditions.append("Course.is_mandatory = ?")
            query_params.append(compulsory)
        if weekday:
            query_conditions.append("Course_Schedule.weekday = ?")
            query_params.append(weekday)
        if time_slot:
            query_conditions.append("Course_Schedule.time_slot = ?")
            query_params.append(time_slot)

        if not query_conditions:
            return render_template('course_query.html', warning='請至少輸入一個查詢條件')

        query_string = """
            SELECT DISTINCT Course.course_code, Course.course_name, Course.credits, Course.max_students, 
                            Course.instructor_name, Course.location, Course.is_mandatory, 
                            GROUP_CONCAT(DISTINCT '星期' || Course_Schedule.weekday || ' 第' || Course_Schedule.time_slot || '節') as schedule,
                            GROUP_CONCAT(DISTINCT Course_Class_Offering.class_name) as class_names
            FROM Course
            LEFT JOIN Course_Schedule ON Course.course_code = Course_Schedule.course_code
            LEFT JOIN Course_Class_Offering ON Course.course_code = Course_Class_Offering.course_code
            WHERE """ + " AND ".join(query_conditions) + """
            GROUP BY Course.course_code
        """
        courses = query_db(query_string, query_params)

        if not courses:
            return render_template('course_query.html', warning='查無符合條件的課程')

        return render_template('course_results.html', courses=courses)
    return render_template('course_query.html')

@app.route('/course_query/course_syllabus/<course_code>')
def course_query_course_syllabus(course_code):
    course_info = query_db('SELECT * FROM CourseInfo WHERE course_id = ?', [course_code], one=True)
    if not course_info:
        return "尚無教學大綱"
    return render_template('showcourse_info.html', course_info=course_info)

@app.route('/course_syllabus/check_course_code', methods=['POST'])
def course_syllabus_check_course_code():
    data = request.json
    course_code = data['course_code']
    course = query_db('SELECT * FROM Course WHERE course_code = ?', [course_code], one=True)
    if course:
        return jsonify({'status': 'exists', 'course': course})
    else:
        return jsonify({'status': 'error', 'message': '課程代碼錯誤'})

@app.route('/course_syllabus/submit_course_info', methods=['POST'])
def course_syllabus_submit_course_info():
    data = request.json
    course_code = data['course_code']
    instructor_name = data['instructor_name']
    existing_instructor = query_db('SELECT instructor_name FROM Course WHERE course_code = ?', [course_code], one=True)
    if existing_instructor and existing_instructor[0] != instructor_name:
        return jsonify({'status': 'error', 'message': '此課程的授課教師錯誤'})
    
    existing_course_info = query_db('SELECT * FROM CourseInfo WHERE course_id = ?', [course_code], one=True)
    if existing_course_info:
        query_db('UPDATE CourseInfo SET course_description = ?, instructor_name = ?, instructor_office_hours = ?, instructor_office_location = ?, instructor_email = ?, instructor_extension = ?, ta_name = ?, ta_email = ?, course_materials = ?, schedule = ?, grading_rules = ?, class_rules = ? WHERE course_id = ?',
                 [data['course_description'], instructor_name, data['instructor_office_hours'], data['instructor_office_location'], data['instructor_email'], data['instructor_extension'], data['ta_name'], data['ta_email'], data['course_materials'], data['schedule'], data['grading_rules'], data['class_rules'], course_code])
        return jsonify({'status': 'success', 'message': '教學大綱更新成功'})
    else:
        query_db('INSERT INTO CourseInfo (course_id, course_description, instructor_name, instructor_office_hours, instructor_office_location, instructor_email, instructor_extension, ta_name, ta_email, course_materials, schedule, grading_rules, class_rules) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 [course_code, data['course_description'], instructor_name, data['instructor_office_hours'], data['instructor_office_location'], data['instructor_email'], data['instructor_extension'], data['ta_name'], data['ta_email'], data['course_materials'], data['schedule'], data['grading_rules'], data['class_rules']])
        return jsonify({'status': 'success', 'message': '教學大綱填寫成功'})

if __name__ == '__main__':
    app.run(debug=True)