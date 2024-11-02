from flask import Flask, request, jsonify, render_template
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
    return render_template('view.html')

@app.route('/api/check_user_id', methods=['POST'])
def check_user_id():
    data = request.json
    user_id = data['user_id']
    user = query_db('SELECT * FROM User WHERE user_id = ?', [user_id], one=True)
    if user:
        return jsonify({'status': 'exists', 'user': user})
    else:
        return jsonify({'status': 'not_exists'})

@app.route('/api/view_schedule', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)