/**
 * Smart Customer Support System - Frontend JavaScript
 * 
 * This file handles:
 * - Real-time Trie-based suggestions
 * - Sending messages to the backend
 * - Displaying responses with data structure labels
 * - Managing recent context display
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
    recentContext: document.getElementById('recent-context'),
    
    // Stats elements
    statTrie: document.getElementById('stat-trie'),
    statFaq: document.getElementById('stat-faq'),
    statQueue: document.getElementById('stat-queue'),
    statPriority: document.getElementById('stat-priority'),
    
    // Data structure indicators
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
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = isUser ? '👤' : '🤖';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // Handle newlines in text
    const paragraphs = escapeHtml(text).split('\n');
    textDiv.innerHTML = paragraphs.map(p => `<p>${p || '&nbsp;'}</p>`).join('');
    
    content.appendChild(textDiv);
    
    // Add metadata badges for bot messages
    if (!isUser && (meta.module || meta.data_structure)) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        
        if (meta.module) {
            const moduleBadge = document.createElement('span');
            moduleBadge.className = 'module-badge';
            moduleBadge.textContent = `Module: ${meta.module}`;
            metaDiv.appendChild(moduleBadge);
        }
        
        if (meta.data_structure) {
            const dsBadge = document.createElement('span');
            dsBadge.className = 'ds-badge';
            dsBadge.textContent = `Data Structure: ${meta.data_structure}`;
            metaDiv.appendChild(dsBadge);
            
            // Highlight the used data structure in sidebar
            highlightDataStructure(meta.data_structure);
        }
        
        if (meta.priority_label && meta.priority_label !== 'NORMAL') {
            const priorityBadge = document.createElement('span');
            priorityBadge.className = 'priority-badge';
            if (meta.priority_label === 'CRITICAL') {
                priorityBadge.classList.add('critical');
            }
            priorityBadge.textContent = `Priority: ${meta.priority_label}`;
            metaDiv.appendChild(priorityBadge);
        }
        
        if (meta.secondary_ds) {
            const secondaryBadge = document.createElement('span');
            secondaryBadge.className = 'ds-badge';
            secondaryBadge.textContent = `Also: ${meta.secondary_ds}`;
            metaDiv.appendChild(secondaryBadge);
        }
        
        content.appendChild(metaDiv);
    }
    
    messageDiv.appendChild(avatar);
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
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="message-text">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
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
        if (dsLower.includes('maxlen') || dsLower.includes('cache')) {
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
        li.innerHTML = `💡 ${highlightPrefix(word, prefix)}`;
        li.addEventListener('click', () => {
            elements.userInput.value = word;
            hideSuggestions();
            elements.userInput.focus();
        });
        elements.suggestionsList.appendChild(li);
    });
    
    elements.suggestionsDropdown.classList.remove('hidden');
    
    // Highlight Trie in sidebar
    highlightDataStructure('Trie');
}

/**
 * Hide suggestions dropdown
 */
function hideSuggestions() {
    elements.suggestionsDropdown.classList.add('hidden');
}

/**
 * Update the recent context display
 * @param {array} interactions - Recent interactions
 */
function updateRecentContext(interactions) {
    if (!interactions || interactions.length === 0) {
        elements.recentContext.innerHTML = '<p class="no-context">No recent interactions</p>';
        return;
    }
    
    elements.recentContext.innerHTML = interactions.map((item, idx) => `
        <div class="context-item">
            <span class="user-text">${idx + 1}. ${escapeHtml(item.user.substring(0, 30))}${item.user.length > 30 ? '...' : ''}</span>
        </div>
    `).join('');
    
    // Highlight Deque in sidebar
    highlightDataStructure('Deque');
}

/**
 * Update system stats display
 * @param {object} stats - System statistics
 */
function updateStats(stats) {
    if (stats.trie_words !== undefined) {
        elements.statTrie.textContent = stats.trie_words;
    }
    if (stats.faq_entries !== undefined) {
        elements.statFaq.textContent = stats.faq_entries;
    }
    if (stats.regular_queue_size !== undefined) {
        elements.statQueue.textContent = stats.regular_queue_size;
    }
    if (stats.priority_queue_size !== undefined) {
        elements.statPriority.textContent = stats.priority_queue_size;
    }
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
        
        // Update recent context
        fetchRecentContext();
        
        // Update stats
        fetchStats();
        
    } catch (error) {
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', false, {
            module: 'Error Handler',
            data_structure: 'None'
        });
    } finally {
        state.isLoading = false;
    }
}

/**
 * Fetch recent context from backend
 */
async function fetchRecentContext() {
    try {
        const data = await apiRequest('/api/context');
        updateRecentContext(data.interactions);
    } catch (error) {
        console.error('Failed to fetch context:', error);
    }
}

/**
 * Fetch system stats
 */
async function fetchStats() {
    try {
        const data = await apiRequest('/api/stats');
        updateStats(data);
    } catch (error) {
        console.error('Failed to fetch stats:', error);
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
        messages.forEach((msg, idx) => {
            if (idx > 0) msg.remove();
        });
        
        // Add reset confirmation
        addMessage('Conversation has been reset. How can I help you today?', false, {
            module: 'Conversation Flow Module',
            data_structure: 'Tree'
        });
        
        // Refresh context and stats
        fetchRecentContext();
        fetchStats();
        
    } catch (error) {
        console.error('Failed to reset conversation:', error);
    }
}

// ============ Event Listeners ============

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
    
    // Fetch initial stats
    fetchStats();
    
    // Focus input
    elements.userInput.focus();
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
