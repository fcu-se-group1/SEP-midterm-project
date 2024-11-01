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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settime')
def settime():
    return render_template('settime.html')

@app.route('/set_enrollment_period', methods=['POST'])
def set_enrollment_period():
    data = request.json   
    # period_type = data['period_type']
    start_time = data['start_time']
    end_time = data['end_time']
    query_db('UPDATE EnrollmentPeriod SET start_time=?, end_time=? WHERE period_type=\"加選\"',
             [start_time, end_time])
    return jsonify({'status': 'success'})

@app.route('/check_enrollment_period', methods=['GET'])
def check_enrollment_period():
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

@app.route('/check_user_id', methods=['POST'])
def check_user_id():
    data = request.json
    user_id = data['user_id']
    user = query_db('SELECT * FROM User WHERE user_id = ?', [user_id], one=True)
    if user:
        return jsonify({'status': 'exists', 'user': user})
    else:
        return jsonify({'status': 'not_exists'})

@app.route('/check_course_code', methods=['POST'])
def check_course_code():
    data = request.json
    course_code = data['course_code']
    course = query_db('SELECT * FROM Course WHERE course_code = ?', [course_code], one=True)
    if course:
        return jsonify({'status': 'exists', 'course': course})
    else:
        return jsonify({'status': 'not_exists'})

@app.route('/check_course_availability', methods=['POST'])
def check_course_availability():
    data = request.json
    course_code = data['course_code']
    course = query_db('SELECT * FROM Course WHERE course_code = ?', [course_code], one=True)
    if course and course['max_students'] > 0:
        return jsonify({'status': 'available'})
    else:
        return jsonify({'status': 'full'})

@app.route('/check_user_credits', methods=['POST'])
def check_user_credits():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    user = query_db('SELECT * FROM User WHERE user_id = ?', [user_id], one=True)
    course = query_db('SELECT * FROM Course WHERE course_code = ?', [course_code], one=True)
    if user and course:
        current_credits = query_db('SELECT SUM(credits) FROM Enrollment JOIN Course ON Enrollment.course_code = Course.course_code WHERE user_id = ?', [user_id], one=True)[0]
        if current_credits + course['credits'] <= 20:  # Assuming 20 is the credit limit
            return jsonify({'status': 'within_limit'})
        else:
            return jsonify({'status': 'exceeds_limit'})
    return jsonify({'status': 'error'})

@app.route('/check_class_restrictions', methods=['POST'])
def check_class_restrictions():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    user = query_db('SELECT * FROM User WHERE user_id = ?', [user_id], one=True)
    restriction = query_db('SELECT * FROM Course_Class_Restriction WHERE course_code = ? AND class_name = ?', [course_code, user['class']], one=True)
    if restriction:
        return jsonify({'status': 'allowed'})
    else:
        return jsonify({'status': 'restricted'})

@app.route('/check_schedule_conflicts', methods=['POST'])
def check_schedule_conflicts():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    new_schedule = query_db('SELECT * FROM Course_Schedule WHERE course_code = ?', [course_code])
    current_schedules = query_db('SELECT * FROM Course_Schedule JOIN Enrollment ON Course_Schedule.course_code = Enrollment.course_code WHERE user_id = ?', [user_id])
    for new in new_schedule:
        for current in current_schedules:
            if new['weekday'] == current['weekday'] and new['time_slot'] == current['time_slot']:
                return jsonify({'status': 'conflict'})
    return jsonify({'status': 'no_conflict'})

@app.route('/enroll_course', methods=['POST'])
def enroll_course():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    query_db('INSERT INTO Enrollment (course_code, user_id, status) VALUES (?, ?, ?)', [course_code, user_id, '已選'])
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)