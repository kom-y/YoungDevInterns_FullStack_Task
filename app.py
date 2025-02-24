from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'school'

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
  
# Initialize Database
with app.app_context():
    db.create_all()

# Index Route
@app.route('/')
def index():
    return render_template('index.html')

# Admin Login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = User.query.filter_by(username=username, password=password, role='admin').first()
        if admin:
            session['user'] = username
            return redirect(url_for('admin_dashboard'))
        return "Invalid Admin Credentials! <a href='/admin_login'>Try again</a>"
    return render_template('admin_login.html')

# School Registration
@app.route('/school_register', methods=['GET', 'POST'])
def school_register():
    if request.method == 'POST':
        school_name = request.form['school_name']
        username = request.form['username']
        password = request.form['password']

        new_school = School(school_name=school_name, username=username, password=password)
        db.session.add(new_school)
        db.session.commit()
        return redirect(url_for('school_login'))
    return render_template('school_register.html')

# School Login
@app.route('/school_login', methods=['GET', 'POST'])
def school_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        school = School.query.filter_by(username=username, password=password).first()
        if school:
            session['school'] = username
            return redirect(url_for('school_dashboard'))
        return "Invalid School Credentials! <a href='/school_login'>Try again</a>"
    return render_template('school_login.html')

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session:
        return redirect(url_for('admin_login'))
    
    schools = School.query.all()
    users = User.query.filter_by(role='school').all()  # Fetch all school users
    total_schools = len(schools)
    total_users = len(users)

    return render_template('admin_dashboard.html', schools=schools, users=users, total_schools=total_schools, total_users=total_users)

# School Dashboard
@app.route('/school_dashboard')
def school_dashboard():
    if 'school' not in session:
        return redirect(url_for('school_login'))
    
    # Fetch the school details from the database
    school = School.query.filter_by(username=session['school']).first()

    if not school:
        return redirect(url_for('school_login'))  # Safety check if school not found

    return render_template('school_dashboard.html', school_name=school.school_name)

# Manage Students
@app.route('/school_dashboard/students', methods=['GET', 'POST'])
def manage_students():
    if 'school' not in session:
        return redirect(url_for('school_login'))
    
    school = School.query.filter_by(username=session['school']).first()
    
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']

        new_student = Student(name=name, age=age, grade=grade, school_id=school.id)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('manage_students'))

    students = Student.query.filter_by(school_id=school.id).all()
    return render_template('manage_students.html', students=students)

# Delete Student
@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    student = Student.query.get(id)
    if student:
        db.session.delete(student)
        db.session.commit()
    return redirect(url_for('manage_students'))

# Delete School
@app.route('/delete_school/<int:id>', methods=['POST'])
def delete_school(id):
    if 'user' not in session:
        return redirect(url_for('admin_login'))
    
    school = School.query.get(id)
    if school:
        db.session.delete(school)
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

# Delete User
@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    if 'user' not in session:
        return redirect(url_for('admin_login'))
    
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

# Edit School
@app.route('/edit_school/<int:id>', methods=['GET', 'POST'])
def edit_school(id):
    if 'user' not in session:
        return redirect(url_for('admin_login'))
    
    school = School.query.get(id)
    
    if request.method == 'POST':
        school.school_name = request.form['school_name']
        school.username = request.form['username']
        school.password = request.form['password']
        db.session.commit()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_school.html', school=school)

# Edit User
@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if 'user' not in session:
        return redirect(url_for('admin_login'))
    
    user = User.query.get(id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.password = request.form['password']
        db.session.commit()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_user.html', user=user)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('school', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)