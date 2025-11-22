from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import DatabaseConfig
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'college_erp_secret_key_2024'

# Helper function to get database connection
def get_db_connection():
    return DatabaseConfig.get_connection()

# Authentication routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"🔐 Login attempt: {username}")
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                
                if user:
                    print(f"✅ User found: {user['username']}")
                    print(f"🔑 Stored password: {user['password']}")
                    
                    # Check if password is hashed
                    if user['password'].startswith('pbkdf2:sha256:'):
                        # Password is hashed
                        if check_password_hash(user['password'], password):
                            session['user_id'] = user['id']
                            session['username'] = user['username']
                            session['role'] = user['role']
                            flash(f'🎉 Login successful! Welcome, {user["username"]}', 'success')
                            return redirect(url_for('dashboard'))
                        else:
                            print("❌ Hashed password mismatch")
                            flash('❌ Invalid password!', 'error')
                    else:
                        # Password is plain text
                        if user['password'] == password:
                            session['user_id'] = user['id']
                            session['username'] = user['username']
                            session['role'] = user['role']
                            flash(f'🎉 Login successful! Welcome, {user["username"]}', 'success')
                            return redirect(url_for('dashboard'))
                        else:
                            print(f"❌ Plain text password mismatch. Expected: {user['password']}, Got: {password}")
                            flash('❌ Invalid password!', 'error')
                else:
                    print("❌ User not found")
                    flash('❌ User not found!', 'error')
                    
            except Exception as e:
                print(f"❌ Database error: {e}")
                flash('❌ Database error occurred!', 'error')
            finally:
                cursor.close()
                conn.close()
        else:
            flash('❌ Cannot connect to database!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('👋 Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('⚠️ Please login first!', 'error')
        return redirect(url_for('login'))
    
    # Get basic stats for dashboard
    conn = get_db_connection()
    if not conn:
        flash('❌ Database connection failed!', 'error')
        return render_template('dashboard.html', 
                             student_count=0, faculty_count=0, course_count=0, 
                             recent_students=[], role=session.get('role'), username=session.get('username'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Count students, faculty, courses
        cursor.execute("SELECT COUNT(*) as count FROM students")
        student_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM faculty")
        faculty_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM courses")
        course_count = cursor.fetchone()['count']
        
        # Get recent students
        cursor.execute("SELECT * FROM students ORDER BY student_id DESC LIMIT 5")
        recent_students = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error in dashboard: {e}")
        student_count = faculty_count = course_count = 0
        recent_students = []
    
    return render_template('dashboard.html', 
                         student_count=student_count,
                         faculty_count=faculty_count,
                         course_count=course_count,
                         recent_students=recent_students,
                         role=session.get('role'),
                         username=session.get('username'))

# Student Management
@app.route('/students')
def students():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    students = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students ORDER BY student_id DESC")
            students = cursor.fetchall()
        except Exception as e:
            print(f"❌ Error: {e}")
            flash('❌ Error loading students!', 'error')
        finally:
            cursor.close()
            conn.close()
    
    show_form = request.args.get('show_form', 'false') == 'true'
    return render_template('students.html', students=students, show_form=show_form)

@app.route('/add_student', methods=['POST'])
def add_student():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        department = request.form['department']
        date_of_birth = request.form['date_of_birth']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO students (first_name, last_name, email, phone, address, department, date_of_birth, enrollment_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURDATE())
                """, (first_name, last_name, email, phone, address, department, date_of_birth))
                conn.commit()
                flash('✅ Student added successfully!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f'❌ Error adding student: {str(e)}', 'error')
            finally:
                cursor.close()
                conn.close()
        else:
            flash('❌ Database connection failed!', 'error')
    
    return redirect(url_for('students'))

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
            conn.commit()
            flash('✅ Student deleted successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'❌ Error deleting student: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    else:
        flash('❌ Database connection failed!', 'error')
    
    return redirect(url_for('students'))

# Faculty Management
@app.route('/faculty')
def faculty():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    faculty_list = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM faculty ORDER BY faculty_id DESC")
            faculty_list = cursor.fetchall()
        except Exception as e:
            print(f"❌ Error: {e}")
            flash('❌ Error loading faculty!', 'error')
        finally:
            cursor.close()
            conn.close()
    
    show_form = request.args.get('show_form', 'false') == 'true'
    return render_template('faculty.html', faculty_list=faculty_list, show_form=show_form)

@app.route('/add_faculty', methods=['POST'])
def add_faculty():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        department = request.form['department']
        designation = request.form['designation']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO faculty (first_name, last_name, email, phone, department, designation, hire_date)
                    VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
                """, (first_name, last_name, email, phone, department, designation))
                conn.commit()
                flash('✅ Faculty added successfully!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f'❌ Error adding faculty: {str(e)}', 'error')
            finally:
                cursor.close()
                conn.close()
        else:
            flash('❌ Database connection failed!', 'error')
    
    return redirect(url_for('faculty'))

# Course Management
@app.route('/courses')
def courses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    courses = []
    faculty_list = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.*, f.first_name, f.last_name 
                FROM courses c 
                LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
                ORDER BY c.course_id DESC
            """)
            courses = cursor.fetchall()
            
            # Get faculty for dropdown
            cursor.execute("SELECT faculty_id, first_name, last_name FROM faculty")
            faculty_list = cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            flash('❌ Error loading courses!', 'error')
        finally:
            cursor.close()
            conn.close()
    
    show_form = request.args.get('show_form', 'false') == 'true'
    return render_template('courses.html', courses=courses, faculty_list=faculty_list, show_form=show_form)

@app.route('/add_course', methods=['POST'])
def add_course():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        course_code = request.form['course_code']
        course_name = request.form['course_name']
        credits = request.form['credits']
        department = request.form['department']
        faculty_id = request.form['faculty_id']
        semester = request.form['semester']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO courses (course_code, course_name, credits, department, faculty_id, semester)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (course_code, course_name, credits, department, faculty_id, semester))
                conn.commit()
                flash('✅ Course added successfully!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f'❌ Error adding course: {str(e)}', 'error')
            finally:
                cursor.close()
                conn.close()
        else:
            flash('❌ Database connection failed!', 'error')
    
    return redirect(url_for('courses'))

# Attendance Management
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    courses = []
    students = []
    attendance_records = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            if request.method == 'POST':
                student_id = request.form['student_id']
                course_id = request.form['course_id']
                attendance_date = request.form['attendance_date']
                status = request.form['status']
                
                try:
                    cursor.execute("""
                        INSERT INTO attendance (student_id, course_id, attendance_date, status)
                        VALUES (%s, %s, %s, %s)
                    """, (student_id, course_id, attendance_date, status))
                    conn.commit()
                    flash('✅ Attendance marked successfully!', 'success')
                except Exception as e:
                    conn.rollback()
                    flash(f'❌ Error marking attendance: {str(e)}', 'error')
            
            # Get courses for dropdown
            cursor.execute("SELECT course_id, course_name FROM courses")
            courses = cursor.fetchall()
            
            # Get students for dropdown
            cursor.execute("SELECT student_id, first_name, last_name FROM students")
            students = cursor.fetchall()
            
            # Get attendance records
            cursor.execute("""
                SELECT a.*, s.first_name, s.last_name, c.course_name
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN courses c ON a.course_id = c.course_id
                ORDER BY a.attendance_date DESC
            """)
            attendance_records = cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            flash('❌ Error loading attendance data!', 'error')
        finally:
            cursor.close()
            conn.close()
    
    show_form = request.args.get('show_form', 'false') == 'true'
    return render_template('attendance.html', 
                         courses=courses, 
                         students=students,
                         attendance_records=attendance_records,
                         show_form=show_form)

# Debug route to check database status
@app.route('/debug')
def debug():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Check users
        cursor.execute("SELECT username, role, LENGTH(password) as pwd_len FROM users")
        users = cursor.fetchall()
        
        # Check counts
        cursor.execute("SELECT COUNT(*) as student_count FROM students")
        student_count = cursor.fetchone()['student_count']
        
        cursor.execute("SELECT COUNT(*) as faculty_count FROM faculty")
        faculty_count = cursor.fetchone()['faculty_count']
        
        cursor.execute("SELECT COUNT(*) as course_count FROM courses")
        course_count = cursor.fetchone()['course_count']
        
        cursor.close()
        conn.close()
        
        return f"""
        <h1>Database Debug Info</h1>
        <h2>Users ({len(users)}):</h2>
        <ul>
            {"".join([f'<li>{user["username"]} ({user["role"]}) - Password length: {user["pwd_len"]}</li>' for user in users])}
        </ul>
        <h2>Counts:</h2>
        <ul>
            <li>Students: {student_count}</li>
            <li>Faculty: {faculty_count}</li>
            <li>Courses: {course_count}</li>
        </ul>
        """
    else:
        return "❌ No database connection"

if __name__ == '__main__':
    print("🚀 Starting College ERP System...")
    print("📧 Demo accounts:")
    print("   👨‍💼 Admin: admin / admin123")
    print("   👨‍🏫 Faculty: prof1 / prof123")  
    print("   👨‍🎓 Student: student1 / stu123")
    print("🌐 Server running at: http://localhost:5000")
    print("🔧 Debug info at: http://localhost:5000/debug")
    app.run(debug=True)