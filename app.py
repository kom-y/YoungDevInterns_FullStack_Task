from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Function to connect to database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route for homepage
@app.route('/')
def home():
    conn = get_db_connection()
    courses = conn.execute('SELECT * FROM courses').fetchall()
    conn.close()
    return render_template('index.html', courses=courses)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '1234':
            session['admin'] = True
            return redirect('/admin')
        else:
            return "Invalid credentials! Try again."
    
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO students (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        conn.commit()
        conn.close()

        return "Registration Successful! <a href='/login'>Go to Login</a>"

    return render_template('register.html')

# Student login route
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print(f"🔎 Login Attempt - Email: {email}, Password: {password}")  

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM students WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user:
            print(f" User Found: {user}") 
        else:
            print(" No user found with this email.")

        if user and password == user['password']:
            session['student'] = email
            print(" Login Successful!")  
            return redirect('/dashboard')
        else:
            print(" Invalid email or password!")
            return " Invalid email or password! <a href='/student_login'>Try again</a>"

    return render_template('student_login.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'student' not in session:
        return redirect('/student_login')

    conn = get_db_connection()
    
    # Fetch student details
    student = conn.execute('SELECT * FROM students WHERE email = ?', (session['student'],)).fetchone()
    
    conn.close()

    return render_template('dashboard.html', student=student)

# Edit profile route
@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if 'student' not in session:
        return redirect('/student_login')

    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    conn = get_db_connection()
    
    if password:  # Only update password if provided
        conn.execute('UPDATE students SET name = ?, email = ?, password = ? WHERE email = ?',
                     (name, email, password, session['student']))
    else:  # Update only name and email
        conn.execute('UPDATE students SET name = ?, email = ? WHERE email = ?',
                     (name, email, session['student']))
    
    conn.commit()
    conn.close()

    # Update session email if changed
    session['student'] = email

    return redirect('/dashboard')

# Logout route
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

# Protect admin route
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin' not in session:
        return redirect('/login')

    conn = get_db_connection()

    # Handle form submission (Adding a course)
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        if course_name:  # Ensure course name is not empty
            conn.execute('INSERT INTO courses (name) VALUES (?)', (course_name,))
            conn.commit()
            print(f"✅ Course Added: {course_name}")  # Debugging message
            return redirect('/admin')  # Refresh the page to update the list

    # Fetch courses and students
    courses = conn.execute('SELECT * FROM courses').fetchall()
    students = conn.execute('SELECT * FROM students').fetchall()

    conn.close()
    return render_template('admin.html', courses=courses, students=students)

# Route to delete a course
@app.route('/delete/<int:id>', methods=['POST'])
def delete_course(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM courses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    def init_db():
        conn = get_db_connection()
        conn.execute('''CREATE TABLE IF NOT EXISTS courses (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS students (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           email TEXT NOT NULL,
                           password TEXT NOT NULL)''')
        conn.commit()
        conn.close()

    init_db()
    app.run(debug=True)
