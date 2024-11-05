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
    period_type = data['period_type']
    start_time = data['start_time']
    end_time = data['end_time']
    period=query_db('SELECT * FROM EnrollmentPeriod WHERE period_type=?', [period_type], one=True)
    if period:
        query_db('DELETE FROM EnrollmentPeriod WHERE period_type=?', [period_type])
    query_db('INSERT INTO EnrollmentPeriod(period_type, start_time, end_time) VALUES (?, ?, ?)',
                 [period_type, start_time, end_time])
    
    return jsonify({'status': 'success'})

@app.route('/check_enrollment_period', methods=['GET'])
def check_enrollment_period():
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
    user_id = data['user_id']
    course = query_db('SELECT * FROM Enrollment WHERE course_code = ? AND user_id =? AND status =?', [course_code,user_id,"已選"], one=True)
    if course:
        return jsonify({'status': 'exists', 'course': course})
    else:
        return jsonify({'status': 'not_exists'})

@app.route('/check_class_restrictions', methods=['POST'])
def check_class_restrictions():
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

@app.route('/check_user_credits', methods=['POST'])
def check_user_credits():
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

@app.route('/drop_course', methods=['POST'])
def drop_course():
    data = request.json
    user_id = data['user_id']
    course_code = data['course_code']
    query_db('DELETE FROM Enrollment WHERE course_code = ? AND user_id = ?', [course_code, user_id])
    return jsonify({'status': 'success', 'message': '退選成功'})

if __name__ == '__main__':
    app.run(debug=True)