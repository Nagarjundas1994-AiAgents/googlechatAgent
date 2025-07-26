// Main JavaScript file for the Google Chat Agent

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips and popovers
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize session ID
    initSession();
    
    // Setup event listeners
    setupEventListeners();
    
    // Add animation classes
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('animate__animated', 'animate__fadeIn');
    });
    
    // Show welcome message
    setTimeout(() => {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages && chatMessages.children.length === 0) {
            const welcomeMessage = document.querySelector('.assistant-message');
            if (welcomeMessage) {
                welcomeMessage.classList.add('animate__animated', 'animate__fadeIn');
            }
        }
    }, 500);
});

// Initialize session
function initSession() {
    if (!localStorage.getItem('sessionId')) {
        localStorage.setItem('sessionId', uuidv4());
    }
    
    // Clear session button
    document.getElementById('clearSessionBtn').addEventListener('click', function(e) {
        e.preventDefault();
        if (confirm('This will clear your current chat session. Are you sure?')) {
            localStorage.removeItem('sessionId');
            localStorage.setItem('sessionId', uuidv4());
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.innerHTML = `
                    <div class="assistant-message animate__animated animate__fadeIn">
                        <p>👋 Hello! I'm your AI assistant. Upload a document or crawl a URL to get started.</p>
                        <p>I can help you:</p>
                        <ul>
                            <li>Answer questions about your documents</li>
                            <li>Extract information from PDFs, Word docs, and web pages</li>
                            <li>Summarize content and provide insights</li>
                        </ul>
                    </div>
                `;
            }
            showAlert('Session cleared successfully!', 'success');
        }
    });
}

// Setup all event listeners
function setupEventListeners() {
    // File upload form
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFileUpload);
    }
    
    // URL crawl form
    const urlForm = document.getElementById('urlForm');
    if (urlForm) {
        urlForm.addEventListener('submit', handleUrlCrawl);
    }
    
    // Question form
    const questionForm = document.getElementById('questionForm');
    if (questionForm) {
        questionForm.addEventListener('submit', handleQuestionSubmit);
    }
    
    // Display selected filename for file input
    const fileInput = document.getElementById('documentFile');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'No file selected';
            this.nextElementSibling = fileName;
        });
    }
}

// Handle file upload
async function handleFileUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('documentFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select a file to upload', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', localStorage.getItem('sessionId'));
    
    try {
        showLoading('uploadLoading');
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(`File uploaded and processed successfully! ${result.message || ''}`, 'success');
            // Switch to chat tab after successful upload
            setTimeout(() => {
                const chatTab = document.querySelector('.nav-link[data-bs-target="#chat"]');
                if (chatTab) {
                    const tabInstance = new bootstrap.Tab(chatTab);
                    tabInstance.show();
                }
            }, 1500);
        } else {
            showAlert(`Error: ${result.detail || 'Failed to upload file'}`, 'danger');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showAlert('An error occurred during upload. Please try again.', 'danger');
    } finally {
        hideLoading('uploadLoading');
    }
}

// Handle URL crawl
async function handleUrlCrawl(e) {
    e.preventDefault();
    
    const urlInput = document.getElementById('urlInput');
    const maxDepth = document.getElementById('maxDepth');
    
    const url = urlInput.value.trim();
    const depth = parseInt(maxDepth.value) || 1;
    
    if (!url) {
        showAlert('Please enter a valid URL', 'warning');
        return;
    }
    
    try {
        showLoading('urlLoading');
        
        const response = await fetch('/api/crawl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                max_depth: depth,
                session_id: localStorage.getItem('sessionId')
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(`URL crawled successfully! ${result.message || ''}`, 'success');
            // Switch to chat tab after successful crawl
            setTimeout(() => {
                const chatTab = document.querySelector('.nav-link[data-bs-target="#chat"]');
                if (chatTab) {
                    const tabInstance = new bootstrap.Tab(chatTab);
                    tabInstance.show();
                }
            }, 1500);
        } else {
            showAlert(`Error: ${result.detail || 'Failed to crawl URL'}`, 'danger');
        }
    } catch (error) {
        console.error('Crawl error:', error);
        showAlert('An error occurred during crawling. Please try again.', 'danger');
    } finally {
        hideLoading('urlLoading');
    }
}

// Handle question submit
async function handleQuestionSubmit(e) {
    e.preventDefault();
    
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();
    
    if (!question) {
        return;
    }
    
    // Add user message to chat
    addMessage('user', question);
    
    // Clear input
    questionInput.value = '';
    
    try {
        showLoading('chatLoading');
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                session_id: localStorage.getItem('sessionId')
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Add AI response to chat
            addMessage('assistant', result.answer, result.sources);
        } else {
            showAlert(`Error: ${result.detail || 'Failed to get response'}`, 'danger');
        }
    } catch (error) {
        console.error('Chat error:', error);
        showAlert('An error occurred. Please try again.', 'danger');
    } finally {
        hideLoading('chatLoading');
    }
}

// Add message to chat
function addMessage(type, content, sources = []) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `${type}-message animate__animated`;
    messageDiv.classList.add(type === 'user' ? 'animate__fadeInRight' : 'animate__fadeInLeft');
    
    // Use marked.js to render markdown in assistant messages
    if (type === 'assistant') {
        messageDiv.innerHTML = marked.parse(content);
        
        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'source-citation';
            sourcesDiv.innerHTML = '<strong>Sources:</strong>';
            
            const sourcesList = document.createElement('ul');
            sources.forEach(source => {
                const sourceItem = document.createElement('li');
                sourceItem.textContent = source;
                sourcesList.appendChild(sourceItem);
            });
            
            sourcesDiv.appendChild(sourcesList);
            messageDiv.appendChild(sourcesDiv);
        }
    } else {
        messageDiv.textContent = content;
    }
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show loading indicator
function showLoading(id) {
    const loadingIndicator = document.getElementById(id);
    if (loadingIndicator) {
        loadingIndicator.classList.add('animate__animated', 'animate__fadeIn');
        loadingIndicator.style.display = 'inline-block';
    }
}

// Hide loading indicator
function hideLoading(id) {
    const loadingIndicator = document.getElementById(id);
    if (loadingIndicator) {
        loadingIndicator.classList.remove('animate__fadeIn');
        loadingIndicator.classList.add('animate__fadeOut');
        setTimeout(() => {
            loadingIndicator.style.display = 'none';
            loadingIndicator.classList.remove('animate__fadeOut');
        }, 500);
    }
}

// Show loading container
function showLoadingContainer(id) {
    const container = document.getElementById(id);
    if (container) {
        container.classList.add('animate__animated', 'animate__fadeIn');
        container.style.display = 'block';
    }
}

// Hide loading container
function hideLoadingContainer(id) {
    const container = document.getElementById(id);
    if (container) {
        container.classList.remove('animate__fadeIn');
        container.classList.add('animate__fadeOut');
        setTimeout(() => {
            container.style.display = 'none';
            container.classList.remove('animate__fadeOut');
        }, 500);
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show animate__animated animate__fadeInDown`;
    alertDiv.setAttribute('role', 'alert');
    
    // Add message
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Find a good place to show the alert
    const container = document.querySelector('.container.content');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('animate__fadeInDown');
            alertDiv.classList.add('animate__fadeOutUp');
            setTimeout(() => {
                alertDiv.remove();
            }, 500);
        }, 5000);
    }
}