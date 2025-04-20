from flask import render_template, redirect, url_for, abort, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from models import Student, Assignment, Teacher, Message, DiscussionThread, DiscussionPost, User
from routes import student_bp
from forms import MessageForm, DiscussionPostForm, LoginForm, RegistrationForm, StudentProfileForm
from datetime import datetime
from app import db
from sqlalchemy import or_, and_

# Auth Routes
@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and not user.is_teacher:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('student.dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', title='Sign In', form=form)

@student_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('student.login'))

@student_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_teacher=False  # Students register with is_teacher=False
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please complete your profile.', 'success')
        return redirect(url_for('auth.complete_profile'))
    return render_template('register.html', title='Register', form=form)

@student_bp.route('/complete_profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    if current_user.is_teacher:
        return redirect(url_for('teacher.dashboard'))
    
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
        flash('Profile completed!', 'success')
        return redirect(url_for('student.dashboard'))
    return render_template('complete_profile.html', title='Complete Profile', form=form)

# Dashboard and Assignments
@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_teacher:
        abort(403)
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return redirect(url_for('student.complete_profile'))
    
    assignments = Assignment.query.filter_by(section=student.section)\
                                .order_by(Assignment.due_date).all()
    
    assignment_details = []
    for assignment in assignments:
        teacher = Teacher.query.get(assignment.teacher_id)
        assignment_details.append({
            'assignment': assignment,
            'teacher_name': teacher.name,
            'subject': teacher.subject
        })
    
    return render_template('student/dashboard.html',
                         title='Student Dashboard',
                         student=student,
                         assignment_details=assignment_details)

@student_bp.route('/assignments/<int:id>')
@login_required
def view_assignment(id):
    if current_user.is_teacher:
        abort(403)
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return redirect(url_for('student.complete_profile'))
    
    assignment = Assignment.query.get_or_404(id)
    if assignment.section != student.section:
        abort(403)
    
    teacher = Teacher.query.get(assignment.teacher_id)
    return render_template('student/assignment_detail.html',
                         title='View Assignment',
                         assignment=assignment,
                         teacher=teacher)

# Messaging System
@student_bp.route('/messages')
@login_required
def messages():
    if current_user.is_teacher:
        abort(403)
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return redirect(url_for('student.complete_profile'))
    
    # Get distinct conversations
    sent_messages = Message.query.filter_by(sender_id=current_user.id).all()
    received_messages = Message.query.filter_by(recipient_id=current_user.id).all()
    all_messages = sent_messages + received_messages
    
    # Organize by other user
    partners = {}
    for msg in all_messages:
        other_id = msg.sender_id if msg.sender_id != current_user.id else msg.recipient_id
        if other_id not in partners:
            user = User.query.get(other_id)
            if user:
                partners[other_id] = {
                    'user': user,
                    'last_message': msg,
                    'unread': msg.recipient_id == current_user.id and not msg.read
                }
    
    # Get all teachers for new message modal
    teachers = User.query.filter_by(is_teacher=True).all()
    
    return render_template('chat/inbox.html',
                         chat_partners=partners.values(),
                         all_users=teachers,
                         student=student)

@student_bp.route('/messages/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    if current_user.is_teacher:
        abort(403)
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return redirect(url_for('student.complete_profile'))
    
    other_user = User.query.get_or_404(user_id)
    if not other_user.is_teacher:
        abort(403, description="Students can only message teachers")
    
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=user_id,
            content=form.content.data
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('student.chat', user_id=user_id))
    
    # Mark messages as read
    Message.query.filter_by(
        sender_id=user_id,
        recipient_id=current_user.id,
        read=False
    ).update({'read': True})
    db.session.commit()
    
    # Get conversation
    messages = Message.query.filter(
        or_(
            and_(
                Message.sender_id == current_user.id,
                Message.recipient_id == user_id
            ),
            and_(
                Message.sender_id == user_id,
                Message.recipient_id == current_user.id
            )
        )
    ).order_by(Message.timestamp.asc()).all()
    
    return render_template('chat/chat.html',
                         messages=messages,
                         other_user=other_user,
                         form=form,
                         student=student)

@student_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    if current_user.is_teacher:
        abort(403)
    
    recipient_id = request.form.get('recipient_id')
    content = request.form.get('content')
    
    if not recipient_id or not content:
        flash('Recipient and message content are required', 'danger')
        return redirect(url_for('student.messages'))
    
    recipient = User.query.get(recipient_id)
    if not recipient or not recipient.is_teacher:
        flash('Invalid recipient', 'danger')
        return redirect(url_for('student.messages'))
    
    message = Message(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    flash('Message sent!', 'success')
    return redirect(url_for('student.chat', user_id=recipient_id))

# Discussion Forum
@student_bp.route('/discussions')
@login_required
def discussions():
    if current_user.is_teacher:
        abort(403)
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return redirect(url_for('student.complete_profile'))
    
    threads = DiscussionThread.query.filter_by(section=student.section)\
                                   .order_by(DiscussionThread.created_at.desc()).all()
    return render_template('chat/discussion_forum.html',
                         threads=threads,
                         student=student)

@student_bp.route('/discussions/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def view_thread(thread_id):
    if current_user.is_teacher:
        abort(403)
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return redirect(url_for('student.complete_profile'))
    
    thread = DiscussionThread.query.get_or_404(thread_id)
    if thread.section != student.section:
        abort(403)
    
    form = DiscussionPostForm()
    if form.validate_on_submit():
        post = DiscussionPost(
            content=form.content.data,
            thread_id=thread_id,
            author_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('student.view_thread', thread_id=thread_id))
    
    posts = thread.posts.order_by(DiscussionPost.timestamp.asc()).all()
    return render_template('chat/thread.html',
                         thread=thread,
                         posts=posts,
                         form=form,
                         student=student)