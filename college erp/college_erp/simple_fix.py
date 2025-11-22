import mysql.connector

def simple_password_fix():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='6604',
            database='college_erp2'
        )
        
        cursor = conn.cursor()
        
        print("🔄 Setting plain text passwords for quick testing...")
        
        # Update passwords to plain text
        passwords = [
            ('admin123', 'admin'),
            ('prof123', 'prof1'),
            ('stu123', 'student1')
        ]
        
        for password, username in passwords:
            cursor.execute(
                "UPDATE users SET password = %s WHERE username = %s",
                (password, username)
            )
            print(f"✅ Set {username} password to: {password}")
        
        conn.commit()
        print("\n🎉 All passwords updated to plain text!")
        
        # Verify
        cursor.execute("SELECT username, password FROM users")
        users = cursor.fetchall()
        print("\n📋 Final passwords:")
        for user in users:
            print(f"   👤 {user[0]}: {user[1]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    simple_password_fix()