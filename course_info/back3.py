from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__, static_folder='.', template_folder='.')

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('..\db\database.db')
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return render_template('course_info.html')

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

@app.route('/courseinfo/<course_code>', methods=['GET'])
def get_course_info(course_code):
    if not course_code:
        return "查無符合條件的課程"
    
    course_info = query_db('SELECT * FROM CourseInfo WHERE course_id = ?', [course_code], one=True)
    if not course_info:
        return "查無符合條件的課程"
    
    return render_template('showcourse_info.html', course_info=course_info)

if __name__ == '__main__':
    app.run(debug=True)