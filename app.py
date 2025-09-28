from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, g
import sqlite3
from database import db_manager
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'skill-exchange-secret-key-2025'

# In-memory store for active user tracking
active_users = {}

def get_db_connection():
    return db_manager.get_connection()

@app.before_request
def track_user_activity():
    if 'user_id' in session:
        active_users[session['user_id']] = datetime.utcnow()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Please fill in all fields!', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id, name, password FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if user and user[2] == hash_password(password):
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                flash(f'Welcome back, {user[1]}!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Invalid email or password!', 'error')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        division = request.form.get('division', '').strip()
        teach_skills = request.form.getlist('teach_skills')
        learn_skills = request.form.getlist('learn_skills')
        available_time = request.form.get('available_time', 'Flexible')
        
        if not all([name, email, password, division]):
            flash('Please fill in all required fields!', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return redirect(url_for('register'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = hash_password(password)
            cursor.execute(
                'INSERT INTO users (name, email, password, division) VALUES (?, ?, ?, ?)',
                (name, email, hashed_password, division)
            )
            user_id = cursor.lastrowid
            
            for skill_id in teach_skills:
                cursor.execute(
                    'INSERT INTO user_teaches (user_id, skill_id, available_time) VALUES (?, ?, ?)',
                    (user_id, skill_id, available_time)
                )
            
            for skill_id in learn_skills:
                cursor.execute(
                    'INSERT INTO user_learns (user_id, skill_id) VALUES (?, ?)',
                    (user_id, skill_id)
                )
            
            conn.commit()
            
            session['user_id'] = user_id
            session['user_name'] = name
            flash('Registration successful! Welcome to Skill Exchange Network!', 'success')
            return redirect(url_for('profile'))
        except sqlite3.IntegrityError:
            flash('Email already exists! Please try logging in instead.', 'error')
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
        finally:
            conn.close()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM skills ORDER BY name')
    skills = cursor.fetchall()
    conn.close()
    
    return render_template('register.html', skills=skills)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile!', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, name, email, division, created_at FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            session.clear()
            flash('User not found!', 'error')
            return redirect(url_for('login'))
        
        cursor.execute('''
            SELECT s.name, ut.available_time 
            FROM skills s 
            JOIN user_teaches ut ON s.id = ut.skill_id 
            WHERE ut.user_id = ?
        ''', (user_id,))
        teaching_skills = cursor.fetchall()
        
        cursor.execute('''
            SELECT s.name 
            FROM skills s 
            JOIN user_learns ul ON s.id = ul.skill_id 
            WHERE ul.user_id = ?
        ''', (user_id,))
        learning_skills = cursor.fetchall()
        
        cursor.execute('''
            SELECT 
                e.id, e.status, e.session_time, e.created_at,
                s.name as skill_name,
                CASE 
                    WHEN e.teacher_id = ? THEN u2.name 
                    ELSE u1.name 
                END as partner_name,
                CASE 
                    WHEN e.teacher_id = ? THEN 'Teaching' 
                    ELSE 'Learning' 
                END as role
            FROM exchanges e
            JOIN skills s ON e.skill_id = s.id
            JOIN users u1 ON e.teacher_id = u1.id
            JOIN users u2 ON e.learner_id = u2.id
            WHERE e.teacher_id = ? OR e.learner_id = ?
            ORDER BY e.created_at DESC
        ''', (user_id, user_id, user_id, user_id))
        exchanges = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        return redirect(url_for('index'))
    finally:
        conn.close()
    
    return render_template('profile.html', 
                         user=user, 
                         teaching_skills=teaching_skills, 
                         learning_skills=learning_skills,
                         exchanges=exchanges)

@app.route('/browse')
def browse():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if search_query:
            cursor.execute('''
                SELECT DISTINCT s.id, s.name, COUNT(ut.user_id) as teacher_count
                FROM skills s
                LEFT JOIN user_teaches ut ON s.id = ut.skill_id
                WHERE s.name LIKE ?
                GROUP BY s.id, s.name
                ORDER BY teacher_count DESC, s.name
            ''', (f'%{search_query}%',))
        else:
            cursor.execute('''
                SELECT s.id, s.name, COUNT(ut.user_id) as teacher_count
                FROM skills s
                LEFT JOIN user_teaches ut ON s.id = ut.skill_id
                GROUP BY s.id, s.name
                ORDER BY teacher_count DESC, s.name
            ''')
        skills = cursor.fetchall()
    except Exception as e:
        flash(f'Error browsing skills: {str(e)}', 'error')
        skills = []
    finally:
        conn.close()
    
    return render_template('browse.html', skills=skills, search_query=search_query)

@app.route('/skill/<int:skill_id>')
def skill_teachers(skill_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT name FROM skills WHERE id = ?', (skill_id,))
        skill = cursor.fetchone()
        
        if not skill:
            flash('Skill not found!', 'error')
            return redirect(url_for('browse'))
        
        if 'user_id' in session:
            cursor.execute('''
                SELECT u.id, u.name, u.division, ut.available_time
                FROM users u
                JOIN user_teaches ut ON u.id = ut.user_id
                WHERE ut.skill_id = ? AND u.id != ?
                ORDER BY u.name
            ''', (skill_id, session['user_id']))
        else:
            cursor.execute('''
                SELECT u.id, u.name, u.division, ut.available_time
                FROM users u
                JOIN user_teaches ut ON u.id = ut.user_id
                WHERE ut.skill_id = ?
                ORDER BY u.name
            ''', (skill_id,))
        teachers = cursor.fetchall()
    except Exception as e:
        flash(f'Error loading teachers: {str(e)}', 'error')
        return redirect(url_for('browse'))
    finally:
        conn.close()
    
    return render_template('match.html', skill=skill, teachers=teachers, skill_id=skill_id)

@app.route('/request_exchange', methods=['POST'])
def request_exchange():
    if 'user_id' not in session:
        flash('Please log in to request exchanges!', 'warning')
        return redirect(url_for('login'))
    
    teacher_id = request.form.get('teacher_id')
    skill_id = request.form.get('skill_id')
    learner_id = session['user_id']
    
    if not teacher_id or not skill_id:
        flash('Invalid request!', 'error')
        return redirect(url_for('browse'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id FROM exchanges 
            WHERE teacher_id = ? AND learner_id = ? AND skill_id = ?
        ''', (teacher_id, learner_id, skill_id))
        
        if cursor.fetchone():
            flash('You have already requested this exchange!', 'warning')
        else:
            cursor.execute('''
                INSERT INTO exchanges (teacher_id, learner_id, skill_id, status)
                VALUES (?, ?, ?, 'pending')
            ''', (teacher_id, learner_id, skill_id))
            conn.commit()
            flash('Exchange request sent successfully!', 'success')
    except Exception as e:
        flash(f'Error sending request: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('profile'))

@app.route('/accept_exchange/<int:exchange_id>')
def accept_exchange(exchange_id):
    if 'user_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE exchanges 
            SET status = 'accepted' 
            WHERE id = ? AND teacher_id = ?
        ''', (exchange_id, session['user_id']))
        
        if cursor.rowcount > 0:
            conn.commit()
            flash('Exchange request accepted!', 'success')
        else:
            flash('Exchange not found or unauthorized!', 'error')
    except Exception as e:
        flash(f'Error accepting exchange: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('profile'))

@app.route('/sessions')
def sessions():
    if 'user_id' not in session:
        flash('Please log in to view sessions!', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                e.id, e.session_time, s.name as skill_name,
                CASE 
                    WHEN e.teacher_id = ? THEN u2.name 
                    ELSE u1.name 
                END as partner_name,
                CASE 
                    WHEN e.teacher_id = ? THEN 'Teaching' 
                    ELSE 'Learning' 
                END as role,
                CASE 
                    WHEN e.teacher_id = ? THEN u2.email 
                    ELSE u1.email 
                END as partner_email
            FROM exchanges e
            JOIN skills s ON e.skill_id = s.id
            JOIN users u1 ON e.teacher_id = u1.id
            JOIN users u2 ON e.learner_id = u2.id
            WHERE (e.teacher_id = ? OR e.learner_id = ?) AND e.status = 'accepted'
            ORDER BY e.created_at DESC
        ''', (user_id, user_id, user_id, user_id, user_id))
        sessions = cursor.fetchall()
    except Exception as e:
        flash(f'Error loading sessions: {str(e)}', 'error')
        sessions = []
    finally:
        conn.close()
    
    return render_template('sessions.html', sessions=sessions)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'info')
    return redirect(url_for('index'))

@app.route('/api/stats')
def api_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM skills")
        skill_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM exchanges")
        exchange_count = cursor.fetchone()[0]
        conn.close()
        return jsonify({
            'user_count': user_count,
            'skill_count': skill_count,
            'exchange_count': exchange_count
        })
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/live-users')
def api_live_users():
    # A user is "live" if they made a request in the last 5 minutes
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    
    # Filter out users who haven't been seen recently
    live_user_ids = [uid for uid, last_seen in active_users.items() if last_seen > five_minutes_ago]
    
    # Add 1 for the current user if they aren't logged in (as a guest)
    live_count = len(live_user_ids) + (1 if 'user_id' not in session else 0)
    return jsonify(live_users=max(1, live_count)) # Always show at least 1

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
