from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# Database setup
DB_PATH = "database.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL,
                    course TEXT NOT NULL,
                    level TEXT NOT NULL,
                    age INTEGER,
                    time_spent REAL,
                    quiz_score INTEGER,
                    exam_score INTEGER,
                    proficiency TEXT)''')
    conn.commit()
    conn.close()

def migrate_database():
    """Add username column if missing"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'username' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN username TEXT DEFAULT 'User'")
            conn.commit()
            print("Added username column to existing database")
    except Exception as e:
        print(f"Migration error: {str(e)}")
    finally:
        conn.close()

# Initialize database
create_database()
migrate_database()

@app.route('/')
def home():
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))
    return redirect(url_for('select_course'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['username'] = user[1]
            session['email'] = email
            flash(f"Welcome back, {user[1]}!", "success")
            return redirect(url_for('select_course'))
        else:
            flash("Invalid email or password", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                         (username, email, password))
            conn.commit()
            conn.close()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already exists", "danger")

    return render_template('register.html')

@app.route('/select-course', methods=['GET', 'POST'])
def select_course():
    if "username" not in session:
        return redirect(url_for('login'))
    
    courses = ["Machine Learning", "Web Development", "Python Basics", 
               "Data Science", "Cybersecurity"]
    levels = ["Beginner", "Intermediate", "Advanced"]
    
    if request.method == 'POST':
        session['current_course'] = request.form['course']
        session['current_level'] = request.form['level']
        return redirect(url_for('assessment'))
    
    return render_template('select_course.html', 
                         username=session['username'],
                         courses=courses, 
                         levels=levels)

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if "username" not in session or "current_course" not in session:
        return redirect(url_for('select_course'))
    
    if request.method == 'POST':
        try:
            age = int(request.form.get('age', 0))
            time_spent = float(request.form.get('time_spent', 0))
            quiz_score = int(request.form.get('quiz_score', 0))
            exam_score = int(request.form.get('exam_score', 0))
            
            total_score = quiz_score * 0.3 + exam_score * 0.7
            if total_score >= 80:
                proficiency = "Advanced"
            elif total_score >= 50:
                proficiency = "Intermediate"
            else:
                proficiency = "Beginner"
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO user_progress 
                            (user_email, course, level, age, time_spent, quiz_score, exam_score, proficiency)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (session['email'], session['current_course'], session['current_level'],
                          age, time_spent, quiz_score, exam_score, proficiency))
            conn.commit()
            conn.close()
            
            flash(f"Your proficiency level: {proficiency}", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Error processing assessment: {str(e)}", "danger")
    
    return render_template('assessment.html',
                         username=session['username'],
                         course=session['current_course'],
                         level=session['current_level'])

@app.route('/dashboard')
def dashboard():
    if "username" not in session:
        return redirect(url_for('login'))
    
    hour = datetime.now().hour
    greeting = "Good morning" if 5 <= hour < 12 else "Good afternoon" if 12 <= hour < 18 else "Good evening"
    welcome_message = f"{greeting}, {session['username']}!"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT course, level, proficiency FROM user_progress 
                     WHERE user_email = ?''', (session['email'],))
    progress = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html',
                         username=session['username'],
                         welcome_message=welcome_message,
                         progress=progress)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
