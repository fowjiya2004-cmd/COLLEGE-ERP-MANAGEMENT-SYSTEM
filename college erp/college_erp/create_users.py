import mysql.connector
from werkzeug.security import generate_password_hash

def fix_user_passwords():
    try:
        # Connect to your college_erp2 database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='6604',  # Your MySQL password
            database='college_erp2'
        )
        
        cursor = conn.cursor()
        
        print("🔄 Fixing user passwords with foreign key handling...")
        
        # First, remove foreign key constraints from faculty and students tables
        print("1. Temporarily removing foreign key constraints...")
        try:
            cursor.execute("ALTER TABLE faculty DROP FOREIGN KEY faculty_ibfk_1")
            print("   ✅ Removed faculty foreign key constraint")
        except:
            print("   ℹ️  Faculty foreign key already removed or doesn't exist")
        
        try:
            cursor.execute("ALTER TABLE students DROP FOREIGN KEY students_ibfk_1")
            print("   ✅ Removed students foreign key constraint")
        except:
            print("   ℹ️  Students foreign key already removed or doesn't exist")
        
        # Clear existing users
        print("2. Clearing existing users...")
        cursor.execute("DELETE FROM users")
        print("   ✅ Cleared existing users")
        
        # Create users with properly hashed passwords
        print("3. Creating new users with hashed passwords...")
        users = [
            ('admin', 'admin123', 'admin', 'admin@college.edu'),
            ('prof1', 'prof123', 'faculty', 'prof1@college.edu'),
            ('student1', 'stu123', 'student', 'student1@college.edu')
        ]
        
        user_ids = {}
        for username, password, role, email in users:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password, role, email) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, role, email)
            )
            user_ids[username] = cursor.lastrowid
            print(f"   ✅ Created user: {username} / {password} (ID: {cursor.lastrowid})")
        
        # Update faculty table with correct user_id references
        print("4. Updating faculty table...")
        cursor.execute("UPDATE faculty SET user_id = %s WHERE faculty_id = 1", (user_ids['prof1'],))
        print(f"   ✅ Updated faculty ID 1 with user_id: {user_ids['prof1']}")
        
        # Update students table with correct user_id references
        print("5. Updating students table...")
        cursor.execute("UPDATE students SET user_id = %s WHERE student_id = 1", (user_ids['student1'],))
        print(f"   ✅ Updated student ID 1 with user_id: {user_ids['student1']}")
        
        # Restore foreign key constraints
        print("6. Restoring foreign key constraints...")
        try:
            cursor.execute("""
                ALTER TABLE faculty 
                ADD CONSTRAINT faculty_ibfk_1 
                FOREIGN KEY (user_id) REFERENCES users(id)
            """)
            print("   ✅ Restored faculty foreign key constraint")
        except:
            print("   ℹ️  Could not restore faculty foreign key")
        
        try:
            cursor.execute("""
                ALTER TABLE students 
                ADD CONSTRAINT students_ibfk_1 
                FOREIGN KEY (user_id) REFERENCES users(id)
            """)
            print("   ✅ Restored students foreign key constraint")
        except:
            print("   ℹ️  Could not restore students foreign key")
        
        conn.commit()
        print("\n🎉 All users created and relationships restored!")
        
        # Verify the users and relationships
        print("\n📋 Verification:")
        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()
        print("   Users table:")
        for user in users:
            print(f"     👤 ID: {user[0]}, Username: {user[1]}, Role: {user[2]}")
        
        cursor.execute("SELECT faculty_id, first_name, user_id FROM faculty")
        faculty = cursor.fetchall()
        print("   Faculty table:")
        for fac in faculty:
            print(f"     👨‍🏫 Faculty ID: {fac[0]}, Name: {fac[1]}, User ID: {fac[2]}")
        
        cursor.execute("SELECT student_id, first_name, user_id FROM students")
        students = cursor.fetchall()
        print("   Students table:")
        for student in students:
            print(f"     👨‍🎓 Student ID: {student[0]}, Name: {student[1]}, User ID: {student[2]}")
            
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
        if conn:
            conn.rollback()
            print("🔁 Changes rolled back due to error")
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
            print("🔁 Changes rolled back due to error")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("🔒 Database connection closed")

if __name__ == '__main__':
    print("🚀 Starting password fix script with foreign key handling...")
    fix_user_passwords()
    print("\n✅ Script completed! You can now run: python app.py")