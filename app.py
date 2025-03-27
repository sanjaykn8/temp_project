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
        print("✅ User is logged in:", session["user"])  # Debugging
        return render_template('index.html')  # Load main page
    else:
        flash("⚠️ Please login first!", "warning")
        print("🔴 No user found in session")  # Debugging
        return redirect(url_for('login'))


# **LOGIN PAGE**
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        print("🔄 Redirecting to home because user is already logged in")  # Debugging
        return redirect(url_for("home"))  # Redirect if already logged in

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = email  # Set session
            flash("✅ Login successful!", "success")
            print("✅ Login successful, redirecting to home")  # Debugging
            return redirect(url_for("home"))  
        else:
            flash("❌ Invalid credentials. Try again.", "danger")
            print("❌ Invalid login attempt")  # Debugging

    return render_template("login.html")


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

            flash("✅ Registration successful! Please login.", "success")
            print("✅ Registration successful")  # Debugging
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("⚠️ Email already exists. Try a different one.", "danger")
            print("⚠️ Email already exists")  # Debugging

    return render_template('register.html')


# **LOGOUT**
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("ℹ️ You have been logged out.", "info")
    print("🔴 User logged out, session cleared")  # Debugging
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
