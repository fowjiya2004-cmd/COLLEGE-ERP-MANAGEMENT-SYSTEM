import mysql.connector
from werkzeug.security import check_password_hash

def check_database_status():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='6604',
            database='college_erp2'
        )
        
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 Checking database status...")
        
        # Check users table
        cursor.execute("SELECT username, password, role, LENGTH(password) as pwd_length FROM users")
        users = cursor.fetchall()
        
        print("\n📋 Current Users in Database:")
        for user in users:
            print(f"   👤 {user['username']} ({user['role']})")
            print(f"   🔑 Password: {user['password']}")
            print(f"   📏 Length: {user['pwd_length']} characters")
            
            # Test password verification
            test_passwords = ['admin123', 'prof123', 'stu123']
            for test_pwd in test_passwords:
                if user['password'].startswith('pbkdf2:sha256:'):
                    # Hashed password
                    if check_password_hash(user['password'], test_pwd):
                        print(f"   ✅ Password matches: {test_pwd}")
                        break
                else:
                    # Plain text password
                    if user['password'] == test_pwd:
                        print(f"   ✅ Password matches: {test_pwd}")
                        break
            else:
                print("   ❌ No password match found")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    check_database_status()