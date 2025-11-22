import mysql.connector
from werkzeug.security import generate_password_hash

def fix_user_passwords():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='college_erp2'
        )
        
        cursor = conn.cursor()
        
        # Clear existing users
        cursor.execute("DELETE FROM users")
        
        # Create users with properly hashed passwords
        users = [
            ('admin', 'admin123', 'admin', 'admin@college.edu'),
            ('prof1', 'prof123', 'faculty', 'prof1@college.edu'),
            ('student1', 'stu123', 'student', 'student1@college.edu')
        ]
        
        for username, password, role, email in users:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password, role, email) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, role, email)
            )
            print(f"✅ Created user: {username} / {password}")
        
        conn.commit()
        print("🎉 Users created with hashed passwords!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    fix_user_passwords()