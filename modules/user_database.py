import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from pathlib import Path

class UserDatabase:
    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT,
                    experience_years INTEGER,
                    current_role TEXT,
                    target_role TEXT,
                    skills TEXT,
                    interests TEXT,
                    location TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Career progress table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS career_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    career_path TEXT,
                    current_level TEXT,
                    milestones_completed TEXT,
                    skills_acquired TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Job applications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    job_title TEXT,
                    company TEXT,
                    job_url TEXT,
                    match_score REAL,
                    status TEXT,
                    applied_date TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Saved jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    job_title TEXT,
                    company TEXT,
                    job_url TEXT,
                    match_score REAL,
                    saved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    job_data TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
    
    def create_user(self, username: str, email: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email) VALUES (?, ?)",
                (username, email)
            )
            return cursor.lastrowid
    
    def get_user(self, user_id: int = None, username: str = None, email: str = None) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            elif username:
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            elif email:
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            else:
                return None
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'created_at': row[3],
                    'updated_at': row[4]
                }
            return None
    
    def update_profile(self, user_id: int, profile_data: Dict) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if profile exists
            cursor.execute("SELECT user_id FROM profiles WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone() is not None
            
            skills = json.dumps(profile_data.get('skills', []))
            interests = json.dumps(profile_data.get('interests', []))
            
            if exists:
                cursor.execute('''
                    UPDATE profiles 
                    SET name = ?, experience_years = ?, current_role = ?, 
                        target_role = ?, skills = ?, interests = ?, location = ?
                    WHERE user_id = ?
                ''', (
                    profile_data.get('name'),
                    profile_data.get('experience_years'),
                    profile_data.get('current_role'),
                    profile_data.get('target_role'),
                    skills,
                    interests,
                    profile_data.get('location'),
                    user_id
                ))
            else:
                cursor.execute('''
                    INSERT INTO profiles 
                    (user_id, name, experience_years, current_role, target_role, skills, interests, location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    profile_data.get('name'),
                    profile_data.get('experience_years'),
                    profile_data.get('current_role'),
                    profile_data.get('target_role'),
                    skills,
                    interests,
                    profile_data.get('location')
                ))
            
            return True
    
    def get_profile(self, user_id: int) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'user_id': row[0],
                    'name': row[1],
                    'experience_years': row[2],
                    'current_role': row[3],
                    'target_role': row[4],
                    'skills': json.loads(row[5]) if row[5] else [],
                    'interests': json.loads(row[6]) if row[6] else [],
                    'location': row[7]
                }
            return None
    
    def save_career_progress(self, user_id: int, progress_data: Dict) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            milestones = json.dumps(progress_data.get('milestones_completed', []))
            skills = json.dumps(progress_data.get('skills_acquired', []))
            
            cursor.execute('''
                INSERT INTO career_progress 
                (user_id, career_path, current_level, milestones_completed, skills_acquired)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                progress_data.get('career_path'),
                progress_data.get('current_level'),
                milestones,
                skills
            ))
            
            return True
    
    def get_career_progress(self, user_id: int) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM career_progress WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1",
                (user_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'user_id': row[1],
                    'career_path': row[2],
                    'current_level': row[3],
                    'milestones_completed': json.loads(row[4]) if row[4] else [],
                    'skills_acquired': json.loads(row[5]) if row[5] else [],
                    'updated_at': row[6]
                }
            return None
    
    def save_job_application(self, user_id: int, job_data: Dict) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO job_applications 
                (user_id, job_title, company, job_url, match_score, status, applied_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                job_data.get('job_title'),
                job_data.get('company'),
                job_data.get('job_url'),
                job_data.get('match_score'),
                job_data.get('status', 'applied'),
                job_data.get('applied_date', datetime.now()),
                job_data.get('notes')
            ))
            return cursor.lastrowid
    
    def get_job_applications(self, user_id: int, status: str = None) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute(
                    "SELECT * FROM job_applications WHERE user_id = ? AND status = ? ORDER BY applied_date DESC",
                    (user_id, status)
                )
            else:
                cursor.execute(
                    "SELECT * FROM job_applications WHERE user_id = ? ORDER BY applied_date DESC",
                    (user_id,)
                )
            
            rows = cursor.fetchall()
            applications = []
            for row in rows:
                applications.append({
                    'id': row[0],
                    'user_id': row[1],
                    'job_title': row[2],
                    'company': row[3],
                    'job_url': row[4],
                    'match_score': row[5],
                    'status': row[6],
                    'applied_date': row[7],
                    'notes': row[8]
                })
            
            return applications
    
    def save_job(self, user_id: int, job_data: Dict) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO saved_jobs 
                (user_id, job_title, company, job_url, match_score, job_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                job_data.get('job_title'),
                job_data.get('company'),
                job_data.get('job_url'),
                job_data.get('match_score'),
                json.dumps(job_data)
            ))
            return cursor.lastrowid
    
    def get_saved_jobs(self, user_id: int) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM saved_jobs WHERE user_id = ? ORDER BY saved_date DESC",
                (user_id,)
            )
            
            rows = cursor.fetchall()
            jobs = []
            for row in rows:
                jobs.append({
                    'id': row[0],
                    'user_id': row[1],
                    'job_title': row[2],
                    'company': row[3],
                    'job_url': row[4],
                    'match_score': row[5],
                    'saved_date': row[6],
                    'job_data': json.loads(row[7]) if row[7] else {}
                })
            
            return jobs