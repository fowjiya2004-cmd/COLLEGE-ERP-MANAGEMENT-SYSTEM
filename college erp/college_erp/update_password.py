import mysql.connector
from werkzeug.security import generate_password_hash

def update_existing_users():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='6604',
            database='college_erp2'
        )
        
        cursor = conn.cursor(dictionary=True)
        
        print("🔄 Updating existing user passwords...")
        
        # Get existing users
        cursor.execute("SELECT id, username, password FROM users")
        existing_users = cursor.fetchall()
        
        print(f"📋 Found {len(existing_users)} existing users")
        
        # Update passwords for existing users
        password_map = {
            'admin': 'admin123',
            'prof1': 'prof123', 
            'student1': 'stu123'
        }
        
        updated_count = 0
        for user in existing_users:
            username = user['username']
            if username in password_map:
                new_password = password_map[username]
                hashed_password = generate_password_hash(new_password)
                
                cursor.execute(
                    "UPDATE users SET password = %s WHERE id = %s",
                    (hashed_password, user['id'])
                )
                print(f"✅ Updated {username} password to: {new_password}")
                updated_count += 1
            else:
                print(f"⚠️  Unknown user: {username}, skipping...")
        
        conn.commit()
        print(f"\n🎉 Updated {updated_count} user passwords!")
        
        # Verify updates
        cursor.execute("SELECT username, role, LENGTH(password) as pwd_length FROM users")
        users = cursor.fetchall()
        print("\n📋 Final user status:")
        for user in users:
            status = "✅" if user['pwd_length'] > 20 else "❌"
            print(f"   {status} {user['username']} ({user['role']}) - Password: {'HASHED' if user['pwd_length'] > 20 else 'PLAIN TEXT'}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    update_existing_users()