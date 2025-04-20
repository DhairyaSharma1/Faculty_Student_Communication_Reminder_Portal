from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User, Teacher, Student
from forms import LoginForm, RegistrationForm, TeacherProfileForm, StudentProfileForm
from routes import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    
    # Redirect if user is already authenticated
    if current_user.is_authenticated:
        if current_user.is_teacher:
            return redirect(url_for('teacher.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Find the user by email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            
            # Get the next page from request or default based on user type
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                if user.is_teacher:
                    next_page = url_for('teacher.dashboard')
                else:
                    next_page = url_for('student.dashboard')
            return redirect(next_page)
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        if current_user.is_teacher:
            return redirect(url_for('teacher.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = User(username=form.username.data, email=form.email.data, is_teacher=form.is_teacher.data)
        user.set_password(form.password.data)
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        # Flash success message
        flash(f'Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='Register', form=form)

@auth_bp.route('/complete_profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    """Complete user profile after registration"""
    if current_user.is_teacher:
        # Check if teacher profile already exists
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        if teacher:
            return redirect(url_for('teacher.dashboard'))
        
        form = TeacherProfileForm()
        if form.validate_on_submit():
            teacher = Teacher(
                user_id=current_user.id,
                name=form.name.data,
                subject=form.subject.data
            )
            db.session.add(teacher)
            db.session.commit()
            flash('Teacher profile completed!', 'success')
            return redirect(url_for('teacher.dashboard'))
        
        return render_template('complete_profile.html', title='Complete Teacher Profile', form=form)
    else:
        # Check if student profile already exists
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            return redirect(url_for('student.dashboard'))
        
        form = StudentProfileForm()
        if form.validate_on_submit():
            student = Student(
                user_id=current_user.id,
                name=form.name.data,
                section=form.section.data,
                roll_number=form.roll_number.data
            )
            db.session.add(student)
            db.session.commit()
            flash('Student profile completed!', 'success')
            return redirect(url_for('student.dashboard'))
        
        return render_template('complete_profile.html', title='Complete Student Profile', form=form)