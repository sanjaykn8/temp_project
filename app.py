from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session handling

# Database setup
DB_PATH = "database.db"

def create_database():
    """Initialize database and create users table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

create_database()  # Ensure DB is created when app starts


# **HOME PAGE (Only accessible after login)**
@app.route('/')
def home():
    if "user" in session:
        return render_template('index.html')  # Load main page
    else:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))


# **LOGIN PAGE**
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = email  # Store user session
            flash("Login successful!", "success")
            return redirect(url_for('home'))  # Redirect to main page
        else:
            flash("Invalid email or password. Try again.", "danger")

    return render_template('login.html')


# **REGISTER PAGE**
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            conn.close()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already exists. Try a different one.", "danger")

    return render_template('register.html')


# **LOGOUT**
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
