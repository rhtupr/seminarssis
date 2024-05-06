from flask import *
from flask import render_template, request, redirect, url_for
import re
from flask import flash
import psycopg2


def db_conn():
      conn = psycopg2.connect (database = "database", host = "localhost", user = "postgres", password = "1234", port = "5432")
      return conn 


students_bp = Blueprint('student', __name__)


@students_bp.route('/students/')
def students():
    students = studentread()
    courses = get_course()  # Fetch the list of courses from your data source
    course_code = None  # Provide the selected course_code or set it based on some logic

    return render_template('students.html', students=students, courses=courses, course_code=course_code)


@students_bp.route('/students/add', methods=['GET', 'POST'])
def add_students():
    if request.method == 'POST':
        student_id = request.form['id']
        first_name = request.form['firstname'].title()
        last_name = request.form['lastname'].title()
        course_code = request.form['coursecode'].upper()
        year_level = request.form['yearlevel']
        gender = request.form['gender'].capitalize()
        image_url = request.form['image_url']
        if not re.match(r'^\d{4}-\d{4}$', student_id):
            print("Invalid Student ID format.")
            flash('Invalid Student ID format. Follow YYYY-NNNN format.', 'error')
        elif check(student_id):
            print("Student ID already exists.")
            flash('Student ID already exists!', 'error')
        else:
            insert_student(student_id, first_name, last_name, course_code, year_level, gender, image_url)
            flash('Student added successfully!', 'success')
            return redirect('/students/') 
    courses = get_course_codes()
    return render_template('addstudents.html', courses=courses)



@students_bp.route('/students/search', methods=['GET', 'POST'])
def search_students():
    students = []
    if request.method == 'POST':
        search_query = request.form.get('search_student')
        if search_query:
            students = find_students(search_query)
    return render_template('students.html', students=students)

@students_bp.route('/students/delete/<string:stud_id>', methods=['DELETE'])
def remove_student(stud_id):
    if request.method == 'DELETE':
        print(stud_id)
        delete_student(stud_id)
        flash('Student deleted successfully!', 'success')
        return jsonify({'success': True})

@students_bp.route('/students/edit', methods=['GET', 'POST'])
def edit_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        new_first_name = request.form.get('first_name').title()
        new_last_name = request.form.get('last_name').title()
        new_course_code = request.form.get('course_code').upper()
        new_year_level = request.form.get('year_level')
        new_gender = request.form.get('gender').capitalize()
        new_image_url = request.form.get('image_url')
        update_student(student_id, new_first_name, new_last_name, new_course_code, new_year_level, new_gender, new_image_url)
        flash('Student edited successfully!', 'success')
        return redirect('/students')
    else:
        student_id = request.args.get('student_id')
        existing_student = get_existing_student(student_id)

        if existing_student:
            first_name = existing_student['firstname']
            last_name = existing_student['lastname']
            course_code = existing_student['coursecode']
            year_level = existing_student['yearlevel']
            gender = existing_student['gender']
            image_url = existing_student['image_url']

            courses = get_course_codes()  # Fetch the course codes

            return render_template('editstudent.html', student_id=student_id, first_name=first_name, last_name=last_name, course_code=course_code, year_level=year_level, gender=gender, image_url = image_url, courses=courses)
        else:
            return render_template('error.html', message="Student not found")


@students_bp.route('/upload/cloudinary/', methods=['POST'])
def upload_to_cloudinary():
    file = request.files.get('file')

    if file:
        upload_result = cloudinary_upload(
            file, folder=CLOUDINARY_FOLDER)

        return jsonify({
            'is_success': True,
            'url': upload_result['secure_url']
        })

    return jsonify({
        'is_success': False,
        'error': 'Missing file'
    })