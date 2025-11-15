from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.controllers.auth_routes import get_db_session
from src.data_access.message_dal import MessageDAL
from src.data_access.user_dal import UserDAL
from src.forms.resource_forms import MessageForm

message_bp = Blueprint('messages', __name__)


@message_bp.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def view_thread(thread_id: int):
    """View and participate in a message thread."""
    form = MessageForm()

    with get_db_session() as session:
        message_dal = MessageDAL(session)
        messages = message_dal.get_thread_messages(thread_id)

        if not messages:
            flash('Thread not found.', 'error')
            return redirect(url_for('messages.inbox'))

        # Determine the other user in the conversation
        first_message = messages[0]
        other_user_id = first_message.receiver_id if first_message.sender_id == current_user.user_id else first_message.sender_id
        
        # Get other user's name
        user_dal = UserDAL(session)
        other_user = user_dal.get_user_by_id(other_user_id)
        other_user_name = other_user.name if other_user else 'Unknown User'
        
        # Format timestamps for template
        from datetime import datetime
        formatted_messages = []
        for msg in messages:
            msg_dict = {
                'message_id': msg.message_id,
                'thread_id': msg.thread_id,
                'sender_id': msg.sender_id,
                'receiver_id': msg.receiver_id,
                'content': msg.content,
                'timestamp': msg.timestamp,
                'timestamp_formatted': msg.timestamp.strftime('%b %d, %Y at %I:%M %p') if msg.timestamp and isinstance(msg.timestamp, datetime) else (str(msg.timestamp) if msg.timestamp else 'N/A')
            }
            formatted_messages.append(msg_dict)

        if request.method == 'POST' and form.validate_on_submit():
            message_dal.create_message(
                sender_id=current_user.user_id,
                receiver_id=other_user_id,
                content=form.content.data,
                thread_id=thread_id,
            )
            flash('Message sent.', 'success')
            return redirect(url_for('messages.view_thread', thread_id=thread_id))

    return render_template('messages/thread.html', 
                         messages=formatted_messages, 
                         form=form, 
                         thread_id=thread_id,
                         other_user_name=other_user_name)


@message_bp.route('/inbox')
@login_required
def inbox():
    """Display user's message inbox."""
    from datetime import datetime
    
    with get_db_session() as session:
        message_dal = MessageDAL(session)
        conversations = message_dal.get_user_conversations(current_user.user_id)
        
        # Format timestamps for template
        formatted_conversations = []
        for conv in conversations:
            conv_dict = dict(conv)
            if conv.get('last_message_time'):
                if isinstance(conv['last_message_time'], datetime):
                    conv_dict['last_message_time_formatted'] = conv['last_message_time'].strftime('%b %d, %Y at %I:%M %p')
                else:
                    conv_dict['last_message_time_formatted'] = str(conv['last_message_time'])
            else:
                conv_dict['last_message_time_formatted'] = None
            formatted_conversations.append(conv_dict)

    return render_template('messages/inbox.html', conversations=formatted_conversations)


@message_bp.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def message_user(user_id: int):
    """Start a conversation or send a message to a specific user."""
    if user_id == current_user.user_id:
        flash('You cannot message yourself.', 'error')
        return redirect(url_for('resources.list_resources'))
    
    form = MessageForm()
    
    with get_db_session() as session:
        user_dal = UserDAL(session)
        recipient = user_dal.get_user_by_id(user_id)
        
        if not recipient:
            flash('User not found.', 'error')
            return redirect(url_for('resources.list_resources'))
        
        message_dal = MessageDAL(session)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Find or create a thread between current user and recipient
            thread_id = message_dal.find_or_create_thread(current_user.user_id, user_id)
            
            # Create the message
            message_dal.create_message(
                sender_id=current_user.user_id,
                receiver_id=user_id,
                content=form.content.data,
                thread_id=thread_id,
            )
            flash('Message sent successfully!', 'success')
            return redirect(url_for('messages.view_thread', thread_id=thread_id))
        
        # Check if there's an existing conversation
        existing_thread = None
        try:
            thread_id = message_dal.find_or_create_thread(current_user.user_id, user_id)
            # Check if thread has messages
            messages = message_dal.get_thread_messages(thread_id)
            if messages:
                existing_thread = thread_id
        except Exception:
            pass
    
    # Support pre-filled message from query parameter (e.g., from booking conflict)
    prefill_message = request.args.get('prefill_message', '')
    if prefill_message and not form.content.data:
        form.content.data = prefill_message
    
    return render_template('messages/message_user.html', 
                         form=form, 
                         recipient=recipient,
                         existing_thread=existing_thread,
                         prefill_message=prefill_message)

