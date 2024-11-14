from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('../course/database.db')
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
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

@app.route('/set_enrollment_period', methods=['POST'])
def set_enrollment_period():
    data = request.json
    add_start_date = data['add_start_date']
    add_end_date = data['add_end_date']
    drop_start_date = data['drop_start_date']
    drop_end_date = data['drop_end_date']

    try:
        # 刪除已有的加選和退選時間設置
        execute_db('DELETE FROM EnrollmentPeriod WHERE period_type = ?', ('add',))
        execute_db('DELETE FROM EnrollmentPeriod WHERE period_type = ?', ('drop',))

        # 插入新的加選和退選時間設置
        execute_db('INSERT INTO EnrollmentPeriod (period_type, start_time, end_time) VALUES (?, ?, ?)',
                   ('add', add_start_date, add_end_date))
        execute_db('INSERT INTO EnrollmentPeriod (period_type, start_time, end_time) VALUES (?, ?, ?)',
                   ('drop', drop_start_date, drop_end_date))
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/get_enrollment_period', methods=['GET'])
def get_enrollment_period():
    add_period = query_db('SELECT start_time, end_time FROM EnrollmentPeriod WHERE period_type = ?', ('add',), one=True)
    drop_period = query_db('SELECT start_time, end_time FROM EnrollmentPeriod WHERE period_type = ?', ('drop',), one=True)
    
    if add_period and drop_period:
        return jsonify({
            'status': 'success',
            'add_start_date': add_period[0],
            'add_end_date': add_period[1],
            'drop_start_date': drop_period[0],
            'drop_end_date': drop_period[1]
        })
    else:
        return jsonify({'status': 'error', 'message': 'No enrollment periods found'})

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

@app.route('/get_course_ids', methods=['GET'])
def get_course_ids():
    course_ids = query_db('SELECT course_code FROM Course')
    return jsonify(course_ids)

if __name__ == '__main__':
    app.run(debug=True)