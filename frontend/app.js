/**
 * Smart Customer Support System - Frontend JavaScript
 * 
 * This file handles:
 * - Real-time Trie-based suggestions
 * - Sending messages to the backend
 * - Displaying responses with data structure labels
 * 
 * NO EXTERNAL LIBRARIES USED - Pure vanilla JavaScript
 */

// ============ Configuration ============
const CONFIG = {
    API_BASE: '',  // Same origin
    DEBOUNCE_MS: 150,  // Debounce for suggestions
    USER_ID: 'user_' + Math.random().toString(36).substr(2, 9)
};

// ============ State ============
const state = {
    isLoading: false,
    lastPrefix: ''
};

// ============ DOM Elements ============
const elements = {
    chatMessages: document.getElementById('chat-messages'),
    userInput: document.getElementById('user-input'),
    sendButton: document.getElementById('send-button'),
    resetButton: document.getElementById('reset-button'),
    suggestionsDropdown: document.getElementById('suggestions-dropdown'),
    suggestionsList: document.getElementById('suggestions-list'),

    // Data structure sidebar items
    dsTrie: document.getElementById('ds-trie'),
    dsHashmap: document.getElementById('ds-hashmap'),
    dsQueue: document.getElementById('ds-queue'),
    dsPriority: document.getElementById('ds-priority'),
    dsTree: document.getElementById('ds-tree'),
    dsDeque: document.getElementById('ds-deque')
};

// ============ Utility Functions ============

/**
 * Debounce function to limit API calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Make an API request
 * @param {string} endpoint - API endpoint
 * @param {object} options - Fetch options
 */
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json'
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Highlight the matching prefix in a suggestion
 * @param {string} word - Full word
 * @param {string} prefix - Prefix to highlight
 */
function highlightPrefix(word, prefix) {
    const prefixLower = prefix.toLowerCase();
    const wordLower = word.toLowerCase();

    if (wordLower.startsWith(prefixLower)) {
        return `<span class="highlight">${escapeHtml(word.substring(0, prefix.length))}</span>${escapeHtml(word.substring(prefix.length))}`;
    }
    return escapeHtml(word);
}

// ============ UI Functions ============

/**
 * Add a message to the chat
 * @param {string} text - Message text
 * @param {boolean} isUser - If true, this is a user message
 * @param {object} meta - Message metadata (module, data_structure, etc.)
 */
function addMessage(text, isUser = false, meta = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    const content = document.createElement('div');
    content.className = 'message-content';

    // Label
    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = isUser ? 'You' : 'System';

    // Message Bubble Wrapper
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // Text Content
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    const paragraphs = escapeHtml(text).split('\n');
    textDiv.innerHTML = paragraphs.map(p => `<p>${p || '&nbsp;'}</p>`).join('');

    bubble.appendChild(textDiv);

    // Metadata Badges (Bot Only)
    if (!isUser && (meta.data_structure || meta.priority_label)) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';

        if (meta.data_structure) {
            const dsBadge = document.createElement('span');
            dsBadge.className = 'ds-badge';
            dsBadge.textContent = `Used: ${meta.data_structure}`;
            metaDiv.appendChild(dsBadge);

            // Highlight the used data structure in sidebar
            highlightDataStructure(meta.data_structure);
        }

        if (meta.priority_label && meta.priority_label !== 'NORMAL') {
            const priorityBadge = document.createElement('span');
            priorityBadge.className = 'ds-badge';
            priorityBadge.textContent = `Priority: ${meta.priority_label}`;
            priorityBadge.style.borderColor = '#ffab91';
            priorityBadge.style.background = '#fbe9e7';
            metaDiv.appendChild(priorityBadge);
        }

        bubble.appendChild(metaDiv);
    }

    // Assemble
    content.appendChild(label);
    content.appendChild(bubble);

    messageDiv.appendChild(content);

    elements.chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

/**
 * Add a typing indicator
 */
function addTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'message bot-message';
    indicator.id = 'typing-indicator';

    indicator.innerHTML = `
        <div class="message-content">
            <div class="message-label">System</div>
            <div class="message-bubble">
                <div class="message-text">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        </div>
    `;

    elements.chatMessages.appendChild(indicator);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Highlight a data structure in the sidebar
 * @param {string} dsName - Data structure name
 */
function highlightDataStructure(dsName) {
    if (!dsName) return;

    // Remove all highlights first
    document.querySelectorAll('.ds-item').forEach(item => {
        item.classList.remove('active');
    });

    // Add highlight to the matching DS
    const dsLower = dsName.toLowerCase();

    if (dsLower.includes('trie')) {
        elements.dsTrie?.classList.add('active');
    } else if (dsLower.includes('hashmap') || dsLower.includes('dictionary')) {
        elements.dsHashmap?.classList.add('active');
    } else if (dsLower.includes('priority')) {
        elements.dsPriority?.classList.add('active');
    } else if (dsLower.includes('queue') || dsLower.includes('deque')) {
        // Distinguish Deque vs Queue
        if (dsLower.includes('deque') || dsLower.includes('cache')) {
            elements.dsDeque?.classList.add('active');
        } else {
            elements.dsQueue?.classList.add('active');
        }
    } else if (dsLower.includes('tree')) {
        elements.dsTree?.classList.add('active');
    }
}

/**
 * Show suggestions dropdown
 * @param {array} suggestions - List of suggestion words
 * @param {string} prefix - The prefix used
 */
function showSuggestions(suggestions, prefix) {
    if (!suggestions || suggestions.length === 0) {
        hideSuggestions();
        return;
    }

    elements.suggestionsList.innerHTML = '';

    suggestions.forEach(word => {
        const li = document.createElement('li');
        li.className = 'suggestion-item';
        // Removed explicit emoji. CSS can add an icon or just plain text.
        li.innerHTML = highlightPrefix(word, prefix);
        li.addEventListener('click', () => {
            elements.userInput.value = word;
            hideSuggestions();
            elements.userInput.focus();
        });
        elements.suggestionsList.appendChild(li);
    });

    elements.suggestionsDropdown.classList.remove('hidden');

    // Highlight Trie in sidebar as we are actively using it
    highlightDataStructure('Trie');
}

/**
 * Hide suggestions dropdown
 */
function hideSuggestions() {
    elements.suggestionsDropdown.classList.add('hidden');
}

// ============ API Functions ============

/**
 * Fetch suggestions from the backend (Trie)
 * @param {string} prefix - The prefix to get suggestions for
 */
const fetchSuggestions = debounce(async (prefix) => {
    if (!prefix || prefix.length < 2) {
        hideSuggestions();
        return;
    }

    if (prefix === state.lastPrefix) {
        return;
    }
    state.lastPrefix = prefix;

    try {
        const data = await apiRequest(`/api/suggestions?prefix=${encodeURIComponent(prefix)}`);
        showSuggestions(data.suggestions, prefix);
    } catch (error) {
        console.error('Failed to fetch suggestions:', error);
        hideSuggestions();
    }
}, CONFIG.DEBOUNCE_MS);

/**
 * Send a message to the backend
 * @param {string} message - The message to send
 */
async function sendMessage(message) {
    if (state.isLoading || !message.trim()) {
        return;
    }

    state.isLoading = true;
    hideSuggestions();

    // Add user message to chat
    addMessage(message, true);

    // Clear input
    elements.userInput.value = '';
    state.lastPrefix = '';

    // Show typing indicator
    addTypingIndicator();

    try {
        const data = await apiRequest('/api/message', {
            method: 'POST',
            body: JSON.stringify({
                message: message,
                user_id: CONFIG.USER_ID
            })
        });

        removeTypingIndicator();

        // Add bot response
        addMessage(data.response, false, {
            module: data.module,
            data_structure: data.data_structure,
            priority_label: data.priority_label,
            secondary_ds: data.secondary_ds
        });

    } catch (error) {
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', false);
    } finally {
        state.isLoading = false;
    }
}

/**
 * Reset the conversation
 */
async function resetConversation() {
    try {
        await apiRequest('/api/reset', {
            method: 'POST',
            body: JSON.stringify({ user_id: CONFIG.USER_ID })
        });

        // Clear chat except welcome message
        const messages = elements.chatMessages.querySelectorAll('.message');
        // Keep the first static welcome message? No, simpler to just clear all dynamic ones
        // but our HTML has a hardcoded welcome message.
        // Let's remove all added messages and add a "System Reset" message.

        elements.chatMessages.innerHTML = '';

        // Add reset confirmation
        addMessage('System reset complete. Ready for new queries.', false, {
            data_structure: 'System'
        });

        // Reset sidebar highlight
        document.querySelectorAll('.active').forEach(el => el.classList.remove('active'));

    } catch (error) {
        console.error('Failed to reset conversation:', error);
    }
}

// ============ Event Listeners ============

// Sidebar Interaction - DS Guides
document.querySelectorAll('.ds-item').forEach(item => {
    item.addEventListener('click', () => {
        // Close others
        document.querySelectorAll('.ds-item').forEach(other => {
            if (other !== item) {
                other.classList.remove('expanded');
            }
        });

        // Toggle current
        item.classList.toggle('expanded');
    });
});

// Input typing - trigger suggestions
elements.userInput.addEventListener('input', (e) => {
    const value = e.target.value.trim();
    fetchSuggestions(value);
});

// Input keydown - handle Enter key
elements.userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(elements.userInput.value);
    } else if (e.key === 'Escape') {
        hideSuggestions();
    }
});

// Send button click
elements.sendButton.addEventListener('click', () => {
    sendMessage(elements.userInput.value);
});

// Reset button click
elements.resetButton.addEventListener('click', () => {
    resetConversation();
});

// Hide suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!elements.suggestionsDropdown.contains(e.target) &&
        e.target !== elements.userInput) {
        hideSuggestions();
    }
});

// ============ Initialization ============

/**
 * Initialize the application
 */
function init() {
    console.log('Smart Customer Support System initialized');
    console.log('User ID:', CONFIG.USER_ID);

    // Focus input
    elements.userInput.focus();
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
