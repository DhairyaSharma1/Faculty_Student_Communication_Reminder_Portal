from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user
from models import db, Teacher, Assignment, Message, DiscussionThread, DiscussionPost, User, Student
from forms import AssignmentForm, MessageForm, DiscussionPostForm
from routes import teacher_bp
from datetime import datetime

# ... (keep existing routes) ...
@teacher_bp.route('/assignments/create', methods=['GET', 'POST'])
@login_required
def create_assignment():
    """Create a new assignment"""
    # Ensure the user is a teacher
    if not current_user.is_teacher:
        abort(403)  # Forbidden
    
    # Get teacher profile
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        return redirect(url_for('auth.complete_profile'))
    
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            section=form.section.data,
            due_date=form.due_date.data,
            teacher_id=teacher.id
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('teacher.dashboard'))
    
    return render_template('teacher/assignments.html', 
                          title='Create Assignment',
                          form=form,
                          action="Create")

@teacher_bp.route('/assignments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_assignment(id):
    """Edit an existing assignment"""
    # Ensure the user is a teacher
    if not current_user.is_teacher:
        abort(403)  # Forbidden
    
    # Get teacher profile
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        return redirect(url_for('auth.complete_profile'))
    
    # Get the assignment
    assignment = Assignment.query.get_or_404(id)
    
    # Ensure the assignment belongs to this teacher
    if assignment.teacher_id != teacher.id:
        abort(403)  # Forbidden
    
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment.title = form.title.data
        assignment.description = form.description.data
        assignment.section = form.section.data
        assignment.due_date = form.due_date.data
        
        db.session.commit()
        flash('Assignment updated successfully!', 'success')
        return redirect(url_for('teacher.dashboard'))
    elif request.method == 'GET':
        # Populate form with current assignment data
        form.title.data = assignment.title
        form.description.data = assignment.description
        form.section.data = assignment.section
        form.due_date.data = assignment.due_date
    
    return render_template('teacher/assignments.html', 
                          title='Edit Assignment',
                          form=form,
                          action="Update")

@teacher_bp.route('/assignments/<int:id>/delete', methods=['POST'])
@login_required
def delete_assignment(id):
    """Delete an assignment"""
    if not current_user.is_teacher:
        abort(403)
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        return redirect(url_for('auth.complete_profile'))
    
    assignment = Assignment.query.get_or_404(id)
    if assignment.teacher_id != teacher.id:
        abort(403)
    
    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment deleted successfully!', 'success')
    return redirect(url_for('teacher.dashboard'))

# In both teacher.py and student.py, add this route:
@teacher_bp.route('/messages')  # or @student_bp.route('/messages')
@login_required
def messages():
    if current_user.is_teacher:
        teacher = Teacher.query.filter_by(user_id=current_user.id).first_or_404()
        students = Student.query.all()
        return render_template('chat/chat.html', students=students)
    else:
        student = Student.query.filter_by(user_id=current_user.id).first_or_404()
        teachers = Teacher.query.all()
        return render_template('chat/chat.html', teachers=teachers)
    # Get all users for new message modal
    all_users = User.query.filter(User.id != current_user.id).all()
    
    return render_template('chat/inbox.html', 
                         title='Messages',
                         chat_partners=chat_partners.values(),
                         all_users=all_users,
                         teacher=teacher)
@teacher_bp.route('/messages/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    """View and send messages to a specific user"""
    if not current_user.is_teacher:
        abort(403)
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        return redirect(url_for('auth.complete_profile'))
    
    other_user = User.query.get_or_404(user_id)
    form = MessageForm()
    
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=user_id,
            content=form.content.data
        )
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('teacher.chat', user_id=user_id))
    
    Message.query.filter_by(sender_id=user_id, recipient_id=current_user.id, read=False).update({'read': True})
    db.session.commit()
    
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    
    return render_template('chat/chat.html', 
                         title=f'Chat with {other_user.username}',
                         messages=messages,
                         other_user=other_user,
                         form=form,
                         teacher=teacher)

@teacher_bp.route('/discussions')
@login_required
def discussions():
    """View all discussion threads"""
    if not current_user.is_teacher:
        abort(403)
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        return redirect(url_for('auth.complete_profile'))
    
    threads = DiscussionThread.query.order_by(DiscussionThread.created_at.desc()).all()
    
    return render_template('chat/discussion_forum.html', 
                         title='Discussion Forum',
                         threads=threads,
                         teacher=teacher)

@teacher_bp.route('/discussions/create', methods=['GET', 'POST'])
@login_required
def create_thread():
    """Create a new discussion thread"""
    if not current_user.is_teacher:
        abort(403)
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        return redirect(url_for('auth.complete_profile'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        section = request.form.get('section')
        if not title or not section:
            flash('Title and section are required', 'error')
        else:
            thread = DiscussionThread(
                title=title,
                section=section,
                creator_id=current_user.id
            )
            db.session.add(thread)
            db.session.commit()
            return redirect(url_for('teacher.discussions'))
    
    return render_template('chat/create_thread.html', 
                         title='Create Discussion',
                         teacher=teacher)

@teacher_bp.route('/discussions/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def view_thread(thread_id):
    """View and post in a discussion thread"""
    if not current_user.is_teacher:
        abort(403)
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        return redirect(url_for('auth.complete_profile'))
    
    thread = DiscussionThread.query.get_or_404(thread_id)
    form = DiscussionPostForm()
    
    if form.validate_on_submit():
        post = DiscussionPost(
            content=form.content.data,
            thread_id=thread_id,
            author_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('teacher.view_thread', thread_id=thread_id))
    
    posts = thread.posts.order_by(DiscussionPost.timestamp.asc()).all()
    
    return render_template('chat/thread.html', 
                         title=thread.title,
                         thread=thread,
                         posts=posts,
                         form=form,
                         teacher=teacher)
@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    """Teacher dashboard view"""
    if not current_user.is_teacher:
        abort(403)
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        return redirect(url_for('auth.complete_profile'))
    
    # Get teacher's assignments grouped by section
    assignments_by_section = {}
    assignments = Assignment.query.filter_by(teacher_id=teacher.id)\
                                .order_by(Assignment.due_date.desc()).all()
    
    for assignment in assignments:
        if assignment.section not in assignments_by_section:
            assignments_by_section[assignment.section] = []
        assignments_by_section[assignment.section].append(assignment)
    
    return render_template('teacher/dashboard.html',
                         title='Teacher Dashboard',
                         teacher=teacher,
                         assignments_by_section=assignments_by_section)

@teacher_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    recipient_id = request.form.get('recipient_id')
    content = request.form.get('content')
    
    if not recipient_id or not content:
        flash('Recipient and message content are required', 'danger')
        return redirect(url_for('teacher.messages'))
    
    message = Message(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        content=content
    )
    
    db.session.add(message)
    db.session.commit()
    
    flash('Message sent!', 'success')
    return redirect(url_for('teacher.chat', user_id=recipient_id))

@teacher_bp.route('/assignments/<int:assignment_id>/submissions')
@login_required
def view_submissions(assignment_id):
    if not current_user.is_teacher:
        abort(403)
    
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != current_user.id:
        abort(403)
    
    submissions = Submission.query.filter_by(assignment_id=assignment_id)\
                                .order_by(Submission.submission_time).all()
    
    # Mark late submissions
    for submission in submissions:
        if submission.submission_time > assignment.due_date and not submission.is_late:
            submission.is_late = True
            submission.status = 'Late'
            db.session.commit()
    
    return render_template('teacher/submission_list.html',
                         title='Submissions',
                         assignment=assignment,
                         submissions=submissions)

@teacher_bp.route('/submissions/<int:submission_id>/grade', methods=['GET', 'POST'])
@login_required
def grade_submission(submission_id):
    if not current_user.is_teacher:
        abort(403)
    
    submission = Submission.query.get_or_404(submission_id)
    assignment = Assignment.query.get(submission.assignment_id)
    
    if assignment.teacher_id != current_user.id:
        abort(403)
    
    form = GradeSubmissionForm()
    if form.validate_on_submit():
        submission.grade = form.grade.data
        submission.feedback = form.feedback.data
        submission.status = 'Graded'
        db.session.commit()
        flash('Grade submitted successfully!', 'success')
        return redirect(url_for('teacher.view_submissions', assignment_id=assignment.id))
    
    return render_template('teacher/grade_submission.html',
                         title='Grade Submission',
                         submission=submission,
                         assignment=assignment,
                         form=form)

