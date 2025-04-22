// Add CSRF token handling at the top
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.content : '';
}

document.addEventListener('DOMContentLoaded', function() {
    let currentRecipient = null;
    let pollInterval = null;
    let currentRecipientName = null;
    let lastMessageCount = 0;
    let retryCount = 0;
    const MAX_RETRIES = 3;

    // Get current user ID from hidden input
    const currentUserId = document.getElementById('current-user-id').value;

    // Load conversations
    function loadConversations() {
        const conversationsContainer = document.querySelector('.conversations');

        // Show loading indicator
        conversationsContainer.innerHTML = '<p class="p-3 text-center"><i>Loading conversations...</i></p>';

        fetch('/chat/conversations', {
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            conversationsContainer.innerHTML = '';

            if (!data.success) {
                throw new Error(data.error || 'Unknown error');
            }

            if (data.conversations.length === 0) {
                conversationsContainer.innerHTML = '<p class="p-3 text-center">No conversations yet</p>';
                return;
            }

            // Sort conversations by last message time (newest first)
            data.conversations.sort((a, b) => {
                if (!a.last_message_time) return 1;
                if (!b.last_message_time) return -1;
                return new Date(b.last_message_time) - new Date(a.last_message_time);
            });

            data.conversations.forEach(conv => {
                const convEl = document.createElement('div');
                convEl.className = `conversation ${conv.unread_count > 0 ? 'unread' : ''}`;
                if (currentRecipient && conv.user_id == currentRecipient) {
                    convEl.className += ' active';
                }
                convEl.dataset.userId = conv.user_id;

                const timeStr = conv.last_message_time ?
                    formatTimestamp(conv.last_message_time) : '';

                convEl.innerHTML = `
                    <div class="user-info">
                        <h5>${conv.username} ${conv.is_teacher ? '(Teacher)' : '(Student)'}</h5>
                        <p class="role-info">${conv.role_info || ''}</p>
                        <p class="last-message">${conv.last_message || 'No messages yet'}</p>
                    </div>
                    <div class="message-info">
                        <span class="time">${timeStr}</span>
                        ${conv.unread_count > 0 ? `<span class="badge bg-danger">${conv.unread_count}</span>` : ''}
                    </div>
                `;
                convEl.addEventListener('click', () => {
                    // Remove active class from all conversations
                    document.querySelectorAll('.conversation').forEach(el => {
                        el.classList.remove('active');
                    });
                    // Add active class to this conversation
                    convEl.classList.add('active');
                    // Remove unread class
                    convEl.classList.remove('unread');

                    openChat(conv.user_id, conv.username);

                    // Mark as read
                    if (conv.unread_count > 0) {
                        fetch(`/chat/mark_as_read/${conv.user_id}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken()
                            }
                        }).catch(error => {
                            console.error('Error marking messages as read:', error);
                        });
                    }
                });
                conversationsContainer.appendChild(convEl);
            });

            // Reset retry count on success
            retryCount = 0;
        })
        .catch(error => {
            console.error('Error loading conversations:', error);

            if (retryCount < MAX_RETRIES) {
                retryCount++;
                conversationsContainer.innerHTML =
                    `<p class="p-3 text-center text-danger">Failed to load conversations. Retrying (${retryCount}/${MAX_RETRIES})...</p>`;

                // Retry after a delay
                setTimeout(loadConversations, 2000);
            } else {
                conversationsContainer.innerHTML =
                    '<p class="p-3 text-center text-danger">Failed to load conversations. Please refresh the page.</p>';
            }
        });
    }

    // Format timestamp in a user-friendly way
    function formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = (now - date) / 1000; // Difference in seconds

        if (diff < 60) {
            return 'Just now';
        } else if (diff < 3600) {
            const mins = Math.floor(diff / 60);
            return `${mins}m ago`;
        } else if (diff < 86400 && date.getDate() === now.getDate()) {
            // Today, show time
            return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        } else if (diff < 172800 && date.getDate() === now.getDate() - 1) {
            // Yesterday
            return 'Yesterday';
        } else {
            // Other days, show date
            return date.toLocaleDateString();
        }
    }

    // Open chat with a user
    function openChat(userId, username) {
        currentRecipient = userId;
        currentRecipientName = username;
        document.getElementById('chat-with').textContent = `Chat with ${username}`;
        document.getElementById('recipient-id').value = userId;

        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = '<p class="text-center"><i>Loading messages...</i></p>';

        // Reset retry count
        retryCount = 0;

        // Load messages
        loadMessages(userId, true);

        // Start polling for new messages
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(() => {
            if (!currentRecipient) return;
            loadMessages(currentRecipient, false);
        }, 5000);

        // Enable message input
        const messageInput = document.getElementById('message-content');
        messageInput.disabled = false;
        messageInput.placeholder = "Type your message...";
        messageInput.focus();
    }

    // Load messages for a specific user
    function loadMessages(userId, scrollToBottom = false) {
        fetch(`/chat/messages/${userId}`, {
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                throw new Error(data.error || 'Unknown error');
            }

            // If first load or new messages, update the view
            if (scrollToBottom || data.messages.length !== lastMessageCount) {
                lastMessageCount = data.messages.length;
                const messagesContainer = document.getElementById('messages');
                messagesContainer.innerHTML = '';

                if (data.messages.length === 0) {
                    messagesContainer.innerHTML = '<p class="text-center">No messages yet. Start the conversation!</p>';
                    return;
                }

                let lastDate = null;

                data.messages.forEach(msg => {
                    // Check if we need to add a date separator
                    const msgDate = new Date(msg.timestamp).toLocaleDateString();
                    if (lastDate !== msgDate) {
                        const dateDiv = document.createElement('div');
                        dateDiv.className = 'date-separator';
                        dateDiv.textContent = msgDate;
                        messagesContainer.appendChild(dateDiv);
                        lastDate = msgDate;
                    }

                    const isCurrentUser = msg.sender_id == currentUserId;
                    const messageEl = document.createElement('div');
                    messageEl.className = `message ${isCurrentUser ? 'sent' : 'received'}`;
                    messageEl.innerHTML = `
                        <div class="message-content">${msg.content}</div>
                        <div class="message-time">
                            ${new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            ${msg.is_read && isCurrentUser ? '<span class="read-indicator">✓✓</span>' : ''}
                        </div>
                    `;
                    messagesContainer.appendChild(messageEl);
                });

                // Scroll to bottom if requested or if it's the first load
                if (scrollToBottom) {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }

                // Reset retry count on success
                retryCount = 0;
            }
        })
        .catch(error => {
            console.error('Error loading messages:', error);

            if (retryCount < MAX_RETRIES) {
                retryCount++;
                document.getElementById('messages').innerHTML =
                    `<p class="text-center text-danger">Failed to load messages. Retrying (${retryCount}/${MAX_RETRIES})...</p>`;

                // Retry after a delay
                setTimeout(() => loadMessages(userId, scrollToBottom), 2000);
            } else {
                document.getElementById('messages').innerHTML =
                    '<p class="text-center text-danger">Failed to load messages. Please try refreshing the page.</p>';
            }
        });
    }

    // Send message
    document.getElementById('message-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const input = document.getElementById('message-content');
        const content = input.value; // Trimming removed
        const recipientId = document.getElementById('recipient-id').value;

        if (!content) {
            alert('Please enter a message');
            return;
        }

        if (!recipientId) {
            alert('Please select a recipient first');
            return;
        }

        // Disable the input while sending
        input.disabled = true;

        // Add pending message to UI immediately
        const messagesContainer = document.getElementById('messages');
        const tempId = 'pending-' + Date.now();
        const pendingMsgEl = document.createElement('div');
        pendingMsgEl.id = tempId;
        pendingMsgEl.className = 'message sent pending';
        pendingMsgEl.innerHTML = `
            <div class="message-content">${content}</div>
            <div class="message-time">
                <span class="sending-indicator">Sending...</span>
            </div>
        `;
        messagesContainer.appendChild(pendingMsgEl);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Clear input field immediately
        const originalContent = content;
        input.value = '';

        fetch('/chat/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken() // Included CSRF token here
            },
            body: JSON.stringify({
                recipient_id: recipientId,
                content: originalContent
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Message send response:', data); // Debugging
            // Remove pending message
            const pendingMsg = document.getElementById(tempId);
            if (pendingMsg) {
                pendingMsg.remove();
            }

            if (data.success) {
                // Re-enable the input
                input.disabled = false;
                input.focus();

                // Reload messages to show the sent message properly
                loadMessages(recipientId, true);

                // Reload conversations to update last message
                loadConversations();
            } else {
                throw new Error(data.error || 'Failed to send message');
            }
        })
        .catch(error => {
            console.log('Sending message:', { recipientId, originalContent });

            console.error('Error sending message:', error);

            // Update the pending message to show error
            const pendingMsg = document.getElementById(tempId);
            if (pendingMsg) {
                pendingMsg.className = 'message sent error';
                pendingMsg.querySelector('.message-time').innerHTML =
                    `<span class="error-indicator">Failed to send - ${error.message}</span>`;
            }

            alert('Failed to send message. Please try again.');

            // Re-enable the input and restore the message text for re-sending
            input.disabled = false;
            input.value = originalContent;
            input.focus();
        });
    });

    // New message modal
    document.getElementById('start-chat').addEventListener('click', function() {
        const select = document.getElementById('recipient-select');
        const recipientId = select.value;

        if (!recipientId) {
            alert('Please select a recipient');
            return;
        }

        const recipientName = select.selectedOptions[0].text;

        // Close the modal
        const modalElement = document.getElementById('newMessageModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        } else {
            // Fallback if bootstrap's modal object isn't available
            modalElement.style.display = 'none';
            modalElement.classList.remove('show');
            document.body.classList.remove('modal-open');
            // Remove modal backdrop
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) backdrop.remove();
        }

        // Open the chat
        openChat(recipientId, recipientName);
    });

    // Search functionality
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const conversations = document.querySelectorAll('.conversations .conversation');

            let visibleCount = 0;
            conversations.forEach(conv => {
                const username = conv.querySelector('h5').textContent.toLowerCase();
                const lastMessage = conv.querySelector('.last-message').textContent.toLowerCase();
                const roleInfo = conv.querySelector('.role-info')?.textContent.toLowerCase() || '';

                if (username.includes(searchTerm) || lastMessage.includes(searchTerm) || roleInfo.includes(searchTerm)) {
                    conv.style.display = '';
                    visibleCount++;
                } else {
                    conv.style.display = 'none';
                }
            });

            // Show a message if no results
            const noResultsEl = document.querySelector('.no-search-results');
            if (visibleCount === 0 && searchTerm) {
                if (!noResultsEl) {
                    const container = document.querySelector('.conversations');
                    const noResults = document.createElement('div');
                    noResults.className = 'no-search-results p-3 text-center';
                    noResults.textContent = 'No conversations match your search';
                    container.appendChild(noResults);
                }
            } else if (noResultsEl) {
                noResultsEl.remove();
            }
        });
    }

    // Initial state of message input (disabled until a chat is selected)
    const messageInput = document.getElementById('message-content');
    if (messageInput) {
        messageInput.disabled = true;
        messageInput.placeholder = "Select a conversation first...";
    }

    // Handle the "New Message" button
    const newMessageBtn = document.querySelector('button[data-bs-toggle="modal"]');
    if (newMessageBtn) {
        newMessageBtn.addEventListener('click', function() {
            // Make sure the modal is properly initialized
            const modalElement = document.getElementById('newMessageModal');
            if (!bootstrap.Modal.getInstance(modalElement)) {
                new bootstrap.Modal(modalElement);
            }
        });
    }

    // Initial load
    loadConversations();
});
