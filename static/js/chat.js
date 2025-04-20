document.addEventListener('DOMContentLoaded', function() {
    // Auto-scroll to bottom of chat
    function scrollToBottom() {
        const container = document.querySelector('.chat-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    // Initialize scroll position
    scrollToBottom();

    // Auto-refresh chat every 5 seconds
    setInterval(function() {
        const container = document.querySelector('.chat-container');
        if (container) {
            const scrollPos = container.scrollTop;
            const scrollHeight = container.scrollHeight;
            const containerHeight = container.clientHeight;
            
            fetch(window.location.href)
                .then(response => response.text())
                .then(text => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(text, 'text/html');
                    const newContent = doc.querySelector('.chat-container').innerHTML;
                    container.innerHTML = newContent;
                    
                    // Only auto-scroll if user was near bottom
                    if (scrollPos + containerHeight >= scrollHeight - 50) {
                        scrollToBottom();
                    }
                });
        }
    }, 5000);

    // Handle message form submission
    const messageForm = document.getElementById('message-form');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.reset();
                    scrollToBottom();
                }
            });
        });
    }
});