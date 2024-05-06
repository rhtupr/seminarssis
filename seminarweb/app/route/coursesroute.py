from flask import Blueprint, render_template, redirect, flash, jsonify, request, url_for
import sys
import psycopg2

# Database connection

db_connection = psycopg2.connect(
        dbname='apiDB',
        user='postgres',
        password='1234',
        host='localhost',
    )

def spcall(qry, param, commit=False):
    try:
        cursor = db_connection.cursor()
        cursor.callproc(qry, param)
        res = cursor.fetchall()
        if commit:
            db_connection.commit()
        return res
    except:
        res = [("Error: " + str(sys.exc_info()[0]) +
                " " + str(sys.exc_info()[1]),)]
    return res

courses_bp = Blueprint('course', __name__)

@courses_bp.route('/courses/' , methods=['GET', 'POST'])
def courses():
    try:
        courses=spcall('get_courses', param=None)[0][0]
        return render_template('courses.html', courses=courses)
    except Exception as e:
        return f"An error occured: {str(e)}", 500



@courses_bp.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course_name = request.form['coursename'].title()
        
        try:
            if course_name:
                res=spcall('insert_course', (course_name ), commit=True)
                return redirect(url_for('course.courses'))
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        
    return render_template('addcourse.html')




@courses_bp.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    if request.method == 'POST':
        course_name = request.form['coourse_name'].title()

        res = spcall('update_course_by_id', (course_id, course_name), commit=True)
        return redirect(url_for('course.courses'))  
    
    course = spcall('get_course_by_id', (course_id, ))[0][0]
    return render_template('editcourse.html', course_id=course_id, course=course)
        

@courses_bp.route('/courses/search', methods=['GET', 'POST'])
def search_courses():
    courses = []
    if request.method == 'POST':
        search_query = request.form.get('search_course')
        if search_query:
            courses = find_courses(search_query)
            
    return render_template('courses.html', courses=courses)

@courses_bp.route('/courses/delete/<int:course_id>', methods=['DELETE'])
def remove_course(course_id):
    if request.method == 'DELETE':
        try:
            res = spcall('delete_course_by_id', (course_id, ), commit=True)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
