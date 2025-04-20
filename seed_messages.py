from app import create_app
from models import db, Message, User
from datetime import datetime, timedelta

app = create_app()
app.app_context().push()

def seed_messages():
    # Get users
    teacher = User.query.filter_by(is_teacher=True).first()
    student = User.query.filter_by(is_teacher=False).first()
    
    if not teacher or not student:
        print("Error: Need at least one teacher and one student")
        return

    # Sample messages
    messages = [
        {
            'sender': teacher,
            'recipient': student,
            'content': "Welcome to our class! Check the new assignment.",
            'days_ago': 2
        },
        {
            'sender': student,
            'recipient': teacher,
            'content': "Thank you! When is the deadline?",
            'days_ago': 1
        },
        {
            'sender': teacher,
            'recipient': student,
            'content': "The deadline is Friday at 5 PM.",
            'days_ago': 1
        }
    ]

    # Create messages
    for msg in messages:
        message = Message(
            sender_id=msg['sender'].id,
            recipient_id=msg['recipient'].id,
            content=msg['content'],
            timestamp=datetime.utcnow() - timedelta(days=msg['days_ago'])
        )
        db.session.add(message)
    
    db.session.commit()
    print(f"Added {len(messages)} test messages")

if __name__ == '__main__':
    seed_messages()