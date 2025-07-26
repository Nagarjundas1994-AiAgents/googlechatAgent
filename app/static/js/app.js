// Main application JavaScript

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize session management
    initSessionManagement();
    
    // Initialize UI components
    initUIComponents();
    
    // Initialize event listeners
    initEventListeners();
});

/**
 * Initialize session management
 */
function initSessionManagement() {
    // Generate a session ID if one doesn't exist
    if (!localStorage.getItem('sessionId')) {
        localStorage.setItem('sessionId', uuidv4());
    }
    
    // Log session information
    console.log('Session ID:', localStorage.getItem('sessionId'));
}

/**
 * Initialize UI components
 */
function initUIComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Initialize event listeners
 */
function initEventListeners() {
    // Add drag and drop support for file uploads
    const fileUploadArea = document.querySelector('.file-upload-area');
    if (fileUploadArea) {
        fileUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.add('dragover');
        });
        
        fileUploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.remove('dragover');
        });
        
        fileUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                document.getElementById('documentFile').files = files;
            }
        });
    }
    
    // Add keyboard shortcut for sending messages (Ctrl+Enter)
    const questionInput = document.getElementById('questionInput');
    if (questionInput) {
        questionInput.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                document.getElementById('questionForm').dispatchEvent(new Event('submit'));
            }
        });
    }
}

/**
 * Format a message for display in the chat
 * @param {string} content - The message content
 * @returns {string} - Formatted HTML content
 */
function formatMessage(content) {
    // Convert URLs to links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    content = content.replace(urlRegex, url => `<a href="${url}" target="_blank">${url}</a>`);
    
    // Convert markdown-style links [text](url)
    const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    content = content.replace(markdownLinkRegex, (match, text, url) => `<a href="${url}" target="_blank">${text}</a>`);
    
    // Convert markdown-style bold **text**
    const boldRegex = /\*\*([^*]+)\*\*/g;
    content = content.replace(boldRegex, (match, text) => `<strong>${text}</strong>`);
    
    // Convert markdown-style italic *text*
    const italicRegex = /\*([^*]+)\*/g;
    content = content.replace(italicRegex, (match, text) => `<em>${text}</em>`);
    
    // Convert line breaks to <br>
    content = content.replace(/\n/g, '<br>');
    
    return content;
}

/**
 * Check the processing status of document/URL uploads
 */
function checkProcessingStatus() {
    const sessionId = localStorage.getItem('sessionId');
    const statusCheckInterval = setInterval(() => {
        fetch(`/status/${sessionId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'completed') {
                    clearInterval(statusCheckInterval);
                    
                    // Update status messages
                    const uploadStatus = document.getElementById('uploadStatus');
                    const urlStatus = document.getElementById('urlStatus');
                    
                    if (uploadStatus && uploadStatus.style.display !== 'none') {
                        uploadStatus.textContent = 'Document processed successfully! You can now ask questions about it.';
                        uploadStatus.className = 'alert alert-success';
                        setTimeout(() => {
                            // Switch to chat tab
                            document.getElementById('chat-tab').click();
                        }, 2000);
                    }
                    
                    if (urlStatus && urlStatus.style.display !== 'none') {
                        urlStatus.textContent = 'URL crawled and processed successfully! You can now ask questions about it.';
                        urlStatus.className = 'alert alert-success';
                        setTimeout(() => {
                            // Switch to chat tab
                            document.getElementById('chat-tab').click();
                        }, 2000);
                    }
                }
            })
            .catch(error => {
                console.error('Error checking status:', error);
                clearInterval(statusCheckInterval);
            });
    }, 5000); // Check every 5 seconds
}

/**
 * Add a message to the chat
 * @param {string} role - 'user' or 'assistant'
 * @param {string} content - The message content
 * @param {Array} sources - Optional array of sources
 */
function addMessageToChat(role, content, sources = []) {
    const chatContainer = document.getElementById('chatMessages');
    if (!chatContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-container';
    
    const messageContent = document.createElement('div');
    messageContent.className = role === 'user' ? 'user-message' : 'assistant-message';
    messageContent.innerHTML = formatMessage(content);
    
    messageDiv.appendChild(messageContent);
    
    // Add sources if available
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'source-citation';
        
        let sourcesHtml = '<strong>Sources:</strong><ul>';
        sources.forEach(source => {
            let sourceText = source.source;
            if (source.title) {
                sourceText = source.title;
            }
            if (source.page) {
                sourceText += ` (Page ${source.page})`;
            }
            sourcesHtml += `<li>${sourceText}</li>`;
        });
        sourcesHtml += '</ul>';
        
        sourcesDiv.innerHTML = sourcesHtml;
        messageDiv.appendChild(sourcesDiv);
    }
    
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}