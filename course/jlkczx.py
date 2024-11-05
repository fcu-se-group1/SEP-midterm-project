from flask import Flask, request, jsonify, render_template, redirect, url_for
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
    return render_template('course_code.html')

@app.route('/course_code', methods=['GET', 'POST'])
def course_code():
    if request.method == 'POST':
        course_code = request.form['course_code']
        existing_course = query_db('SELECT * FROM Course WHERE course_code = ?', [course_code], one=True)
        if existing_course:
            return render_template('course_code.html', warning='Course code already exists.', course_code=course_code)
        else:
            return redirect(url_for('course_info', course_code=course_code))
    return render_template('course_code.html')

@app.route('/course_info/<course_code>', methods=['GET', 'POST'])
def course_info(course_code):
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

if __name__ == '__main__':
    app.run(debug=True)