from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)