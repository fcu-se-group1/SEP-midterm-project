from flask import Flask, request, render_template, redirect, url_for
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
    return render_template('course_query.html')

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

if __name__ == '__main__':
    app.run(debug=True)