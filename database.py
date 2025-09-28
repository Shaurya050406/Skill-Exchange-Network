import sqlite3
import hashlib
from datetime import datetime

class DatabaseManager:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    def __init__(self, db_name='skill_exchange.db'):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print("Initializing database if not exists...")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                division TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("Users table ready")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT DEFAULT 'General'
            )
        ''')
        print("✅ Skills table ready")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_teaches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                available_time TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (skill_id) REFERENCES skills (id)
            )
        ''')
        print("User_teaches table ready")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_learns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (skill_id) REFERENCES skills (id)
            )
        ''')
        print("User_learns table ready")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchanges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                learner_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                session_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users (id),
                FOREIGN KEY (learner_id) REFERENCES users (id),
                FOREIGN KEY (skill_id) REFERENCES skills (id)
            )
        ''')
        print("Exchanges table ready")
        
        sample_skills = [
            'Python Programming', 'Web Development', 'JavaScript', 'Database Design',
            'Graphic Design', 'Digital Marketing', 'Photography', 'Video Editing',
            'Music Production', 'Language Learning', 'Mathematics', 'Physics',
            'Data Science', 'Mobile App Development', 'UI/UX Design', 'Content Writing'
        ]
        
        for skill in sample_skills:
            try:
                cursor.execute('INSERT INTO skills (name) VALUES (?)', (skill,))
            except sqlite3.IntegrityError:
                pass  # Skill already exists
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
        self.verify_schema()
    
    def verify_schema(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        required_columns = ['id', 'name', 'email', 'password', 'division', 'created_at']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"❌ Missing columns in users table: {missing_columns}")
        else:
            print("✅ All required columns present in users table")
            print(f"📋 Users table columns: {columns}")
        
        conn.close()

db_manager = DatabaseManager()
