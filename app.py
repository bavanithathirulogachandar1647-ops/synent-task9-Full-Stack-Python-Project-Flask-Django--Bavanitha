from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Home
@app.route('/')
def home():
    return redirect(url_for('login'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return "Username already exists!"

        new_user = User(
            username=username,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            session['user_id'] = user.id
            session['username'] = user.username

            return redirect(url_for('dashboard'))

        return "Invalid Username or Password"

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    tasks = Task.query.filter_by(
        user_id=session['user_id']
    ).all()

    return render_template(
        'dashboard.html',
        tasks=tasks,
        username=session['username']
    )

# Add Task
@app.route('/add_task', methods=['POST'])
def add_task():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form['title']

    new_task = Task(
        title=title,
        user_id=session['user_id']
    )

    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('dashboard'))

# Delete Task
@app.route('/delete/<int:id>')
def delete_task(id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = Task.query.get(id)

    if task:
        db.session.delete(task)
        db.session.commit()

    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))

# Create Database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)