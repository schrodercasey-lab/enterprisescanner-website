"""
Quick database verification script
"""
import sqlite3
import os

db_path = os.path.join('backend', 'enterprise_scanner.db')

if os.path.exists(db_path):
    print("✅ DATABASE FOUND!")
    print(f"📁 Location: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table count
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n📊 Tables created: {len(tables)}")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Get Fortune 500 count
    cursor.execute("SELECT COUNT(*) FROM companies WHERE is_fortune_500=1")
    fortune_count = cursor.fetchone()[0]
    print(f"\n🏢 Fortune 500 companies: {fortune_count}")
    
    # Get company names
    cursor.execute("SELECT name FROM companies WHERE is_fortune_500=1")
    companies = cursor.fetchall()
    for company in companies:
        print(f"   - {company[0]}")
    
    # Check admin user
    cursor.execute("SELECT email, full_name, role FROM users WHERE role='admin'")
    admin = cursor.fetchone()
    if admin:
        print(f"\n👤 Admin user: {admin[0]}")
        print(f"   Name: {admin[1]}")
        print(f"   Role: {admin[2]}")
        print(f"   Password: Admin123!")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ DATABASE READY FOR USE!")
    print("="*60)
    print("\n🚀 Next step: Start the backend server")
    print("   Run: python backend/app.py")
    
else:
    print("❌ Database not found!")
    print("   Run: python backend/setup_sqlite.py")
