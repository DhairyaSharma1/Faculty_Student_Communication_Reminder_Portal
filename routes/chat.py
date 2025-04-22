# chat_routes.py
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Message, User, Teacher, Student
from datetime import datetime
from routes import chat_bp
import traceback
from sqlalchemy.exc import SQLAlchemyError

@chat_bp.route('/')
@login_required
def chat_index():
    """Render the chat page"""
    if current_user.is_teacher:
        students = Student.query.all()
        return render_template('chat/chat.html', students=students, teachers=[])
    else:
        teachers = Teacher.query.all()
        return render_template('chat/chat.html', teachers=teachers, students=[])

@chat_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """API endpoint to send a message"""
    try:
        data = request.get_json()

        # Sanitize and validate inputs
        raw_recipient_id = data.get('recipient_id')
        content = data.get('content', '').strip()  # Strip whitespace

        try:
            recipient_id = int(raw_recipient_id)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'Invalid recipient ID'}), 400

        if not recipient_id or not content:
            return jsonify({'success': False, 'error': 'Missing recipient or content'}), 400

        # Lookup recipient
        recipient = User.query.get(recipient_id)
        if not recipient:
            return jsonify({'success': False, 'error': 'Recipient not found'}), 404

        # Restriction: students can't message other students
        if not current_user.is_teacher and not recipient.is_teacher:
            return jsonify({'success': False, 'error': 'Students can only message teachers'}), 403

        # Create and save message
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=content
        )
        db.session.add(message)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'sender_name': current_user.username
            }
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error in send_message: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error occurred'}), 500

    except Exception as e:
        print(f"Unexpected error in send_message: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500

@chat_bp.route('/messages/<int:user_id>')
@login_required
def get_messages(user_id):
    """API endpoint to get messages for a conversation"""
    try:
        # Verify the other user exists
        other_user = User.query.get_or_404(user_id)
        
        # Mark received messages as read
        unread_messages = Message.query.filter_by(
            sender_id=user_id,
            recipient_id=current_user.id,
            read=False
        ).all()
        
        for message in unread_messages:
            message.read = True
            message.read_at = datetime.utcnow()
        
        db.session.commit()
        
        # Get all messages between the two users
        messages = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
            ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
        ).order_by(Message.timestamp.asc()).all()
        
        return jsonify({
            'success': True,
            'messages': [{
                'id': m.id,
                'content': m.content,
                'timestamp': m.timestamp.isoformat(),
                'sender_id': m.sender_id,
                'sender_name': m.sender.username,
                'is_read': m.read,
                'read_at': m.read_at.isoformat() if m.read_at else None
            } for m in messages]
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error in get_messages: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error occurred'}), 500
    except Exception as e:
        print(f"Unexpected error in get_messages: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500

@chat_bp.route('/conversations')
@login_required
def get_conversations():
    """API endpoint to get all conversations for the current user"""
    try:
        # Get all unique users the current user has messaged or received messages from
        sent = db.session.query(Message.recipient_id).filter_by(sender_id=current_user.id).distinct()
        received = db.session.query(Message.sender_id).filter_by(recipient_id=current_user.id).distinct()
        user_ids = {id for (id,) in sent.union_all(received)}
        
        conversations = []
        for user_id in user_ids:
            user = User.query.get(user_id)
            if not user:
                continue  # Skip if user doesn't exist
                
            last_message = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
                ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
            ).order_by(Message.timestamp.desc()).first()
            
            unread_count = Message.query.filter_by(
                sender_id=user_id,
                recipient_id=current_user.id,
                read=False
            ).count()
            
            # Get additional user info based on role
            display_name = user.username
            role_info = ""
            
            if user.is_teacher:
                teacher = Teacher.query.filter_by(user_id=user.id).first()
                if teacher:
                    display_name = teacher.name
                    role_info = teacher.subject
            else:
                student = Student.query.filter_by(user_id=user.id).first()
                if student:
                    display_name = student.name
                    role_info = student.section
            
            conversations.append({
                'user_id': user_id,
                'username': display_name,
                'role_info': role_info,
                'is_teacher': user.is_teacher,
                'last_message': last_message.content if last_message else '',
                'last_message_time': last_message.timestamp.isoformat() if last_message else '',
                'unread_count': unread_count
            })
        
        return jsonify({'success': True, 'conversations': conversations})
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error in get_conversations: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error occurred'}), 500
    except Exception as e:
        print(f"Unexpected error in get_conversations: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500

@chat_bp.route('/mark_as_read/<int:user_id>', methods=['POST'])
@login_required
def mark_as_read(user_id):
    """API endpoint to mark all messages from a user as read"""
    try:
        # Mark all messages from this user as read
        unread_messages = Message.query.filter_by(
            sender_id=user_id,
            recipient_id=current_user.id,
            read=False
        ).all()
        
        for message in unread_messages:
            message.read = True
            message.read_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True})
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error in mark_as_read: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error occurred'}), 500
    except Exception as e:
        print(f"Unexpected error in mark_as_read: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500