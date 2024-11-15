from flask import Flask, request, jsonify, render_template
import datetime
import sqlite3

app = Flask(__name__, static_folder='.', template_folder='.')

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

app.route('/check_user_id', methods=['POST'])
def check_user_id():
    data = request.json
    user_id = data['user_id']
    user = query_db('SELECT * FROM User WHERE user_id = ?', [user_id], one=True)
    if user:
        return jsonify({'status': 'exists', 'user': user})
    else:
        return jsonify({'status': 'not_exists'})
    
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

@app.route('/withdraw/check_course_code', methods=['POST'])
def withdraw_check_course_code():
    data = request.json
    course_code = data['course_code']
    user_id = data['user_id']
    course = query_db('SELECT * FROM Enrollment WHERE course_code = ? AND user_id =? AND status =?', [course_code,user_id,"已選"], one=True)
    if course:
        return jsonify({'status': 'exists', 'course': course})
    else:
        return jsonify({'status': 'not_exists'})
    
@app.route('/registration/check_course_code', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)