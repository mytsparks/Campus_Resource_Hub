from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.controllers.auth_routes import get_db_session
from src.data_access.message_dal import MessageDAL
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

        if request.method == 'POST' and form.validate_on_submit():
            message_dal.create_message(
                sender_id=current_user.user_id,
                receiver_id=other_user_id,
                content=form.content.data,
                thread_id=thread_id,
            )
            flash('Message sent.', 'success')
            return redirect(url_for('messages.view_thread', thread_id=thread_id))

    return render_template('messages/thread.html', messages=messages, form=form, thread_id=thread_id)


@message_bp.route('/inbox')
@login_required
def inbox():
    """Display user's message inbox."""
    with get_db_session() as session:
        message_dal = MessageDAL(session)
        conversations = message_dal.get_user_conversations(current_user.user_id)

    return render_template('messages/inbox.html', conversations=conversations)

