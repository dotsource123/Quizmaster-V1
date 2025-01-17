from flask import Flask, render_template, redirect,jsonify, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.sql import text
from models import db, Admin, User, Subject, Chapter, Quiz, Question, Score

# Initialize Flask app
app = Flask(__name__)

# Set the SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database URI
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure random key

# Initialize the SQLAlchemy object with the app
db.init_app(app)

# Function to create the tables
# Function to create the tables
def create_tables():
    with app.app_context():
        db.create_all()
        # Add default admin if it doesn't exist
        if not Admin.query.filter_by(id="101").first():
            admin = Admin(
                id="101",
                username="default",
                password=generate_password_hash("123456", method='pbkdf2:sha256'),  # Use 'pbkdf2:sha256'
                full_name="First Admin",
                email="admin@adminmail.com"
            )
            db.session.add(admin)
            db.session.commit()


# Call the create_tables function
create_tables()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login failed. Check username and/or password', 'danger')
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('admin_login'))
    admin = Admin.query.get(session['admin_id'])
    chapters = Chapter.query.all()
    return render_template('admin_dashboard.html', chapters=chapters,admin=admin)

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard', user_id=user.id))
        else:
            flash('Login failed. Check username and/or password', 'danger')
    return render_template('user_login.html')

@app.route('/user_dashboard/<int:user_id>')
def user_dashboard(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('user_login'))
    user = User.query.get_or_404(user_id)
    return render_template('user_dashboard.html', user=user)

@app.route('/scores/<int:user_id>')
def scores(user_id):
    user = User.query.get_or_404(user_id)
    scores = Score.query.filter_by(user_id=user_id).all()
    return render_template('scores.html', user=user, scores=scores)

@app.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    if request.method == 'POST':
        
        date_of_quiz = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        remarks = request.form['remarks']
        chapter_id = request.form['chapter_id']

        
        quiz_date = datetime.strptime(date_of_quiz, '%Y-%m-%d')

        
        new_quiz = Quiz(
            date_of_quiz=quiz_date,
            time_duration=time_duration,
            remarks=remarks,
            chapter_id=chapter_id
        )

        
        db.session.add(new_quiz)
        db.session.commit()

    
        return redirect(url_for('quiz_list'))

    
    chapters = Chapter.query.all()

    
    return render_template('create_quiz.html', chapters=chapters)


@app.route('/run_query', methods=['GET'])

def run_query():
    try:
        # SQL query wrapped inside text() function
        #query = text("INSERT INTO scores (id, total_scored, time_stamp_of_attempt, quiz_id, user_id) "
                     #"VALUES (5, 85, '2024-01-08 14:30:00', 101, 2)")

        query = text("Select * from admins")
        
        # Execute the query
        db.session.execute(query)
        
        # Commit the transaction
        db.session.commit()
        
        return "Query executed successfully!"
        
    except Exception as e:
        # Handle exceptions and return the error message
        return f"An error occurred: {str(e)}"

@app.route('/create_subject', methods=['GET', 'POST'])
def create_subject():
    if request.method == 'POST':
        # Get form data
        subject_id = request.form['subject_id']
        name = request.form['name']
        description = request.form['description']
        
        # Create a new Subject instance
        new_subject = Subject(id=subject_id, name=name, description=description)
        
        # Insert into the database
        try:
            db.session.add(new_subject)
            db.session.commit()
            flash('Subject created successfully!', 'success')  # Flash success message
            return redirect(url_for('create_subject'))
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')  # Flash error message
    
    # Render the form for creating a subject
    return render_template('create_subject.html')


@app.route('/user_registration', methods=['GET', 'POST'])
def user_registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = request.form['dob']
        admin_id = request.form['admin_id']
        admin = Admin.query.get(admin_id)
        if not admin:
            flash('Invalid Admin ID.', 'danger')
            return redirect(url_for('user_registration'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(
            username=username,
            password=hashed_password,
            full_name=full_name,
            qualification=qualification,
            dob=datetime.strptime(dob, '%Y-%m-%d'),
            admin_id=admin_id
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('user_login'))
    return render_template('user_registration.html')

@app.route('/add_chapter', methods=['GET', 'POST'])
def add_chapter():
    if request.method == 'POST':
        chapter_name = request.form.get('name', '').strip()
        chapter_description = request.form.get('description', '').strip()
        subject_id = request.form.get('subject_id')

        if not chapter_name or not subject_id:
            flash("Chapter name and subject ID are required fields.", "error")
            return redirect(url_for('add_chapter'))

        try:
            new_chapter = Chapter(
                name=chapter_name,
                description=chapter_description,
                subject_id=int(subject_id)
            )
            db.session.add(new_chapter)
            db.session.commit()
            flash("Chapter added successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while adding the chapter: {str(e)}", "error")

        return redirect(url_for('admin_dashboard'))

    subjects = Subject.query.all()
    return render_template('add_chapter.html', subjects=subjects)

@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form.get('description', '')
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_chapter.html', chapter=chapter)

@app.route('/delete_chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form.get('option3', '')  
        option4 = request.form.get('option4', '')  
        correct_option = request.form['correct_option']
        quiz_id = request.form['quiz_id']  

        
        new_question = Question(
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option,
            quiz_id=quiz_id
        )

        
        db.session.add(new_question)
        db.session.commit()

        
        flash('The question has been successfully added!', 'success')

        
        return render_template('add_question.html')

    
    return render_template('add_question.html')



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user_login'))



if __name__ == '__main__':
    app.run(debug=True)
