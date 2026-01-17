/**
 * E-Shop Customer Support - Frontend JavaScript
 * 
 * Demonstrates 6 Data Structures:
 * 1. Trie - Auto-complete suggestions
 * 2. HashMap - O(1) FAQ lookups
 * 3. Decision Tree - Conversation flow
 * 4. Stack - Go back navigation
 * 5. Union-Find - Synonym grouping
 * 6. Weighted Graph - Next best actions
 */

// ============ Configuration ============
const CONFIG = {
    API_BASE: '',
    DEBOUNCE_MS: 150,
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
    dsTree: document.getElementById('ds-tree'),
    dsStack: document.getElementById('ds-stack'),
    dsUnionFind: document.getElementById('ds-unionfind'),
    dsGraph: document.getElementById('ds-graph')
};

// ============ Utility Functions ============

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

async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}${endpoint}`, {
            headers: { 'Content-Type': 'application/json' },
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

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function highlightPrefix(word, prefix) {
    const prefixLower = prefix.toLowerCase();
    const wordLower = word.toLowerCase();

    if (wordLower.startsWith(prefixLower)) {
        return `<span class="highlight">${escapeHtml(word.substring(0, prefix.length))}</span>${escapeHtml(word.substring(prefix.length))}`;
    }
    return escapeHtml(word);
}

// ============ UI Functions ============

function addMessage(text, isUser = false, meta = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    const content = document.createElement('div');
    content.className = 'message-content';

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = isUser ? 'You' : 'System';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // Process text with markdown-like formatting
    let processedText = escapeHtml(text);
    // Bold: **text**
    processedText = processedText.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Split by newlines
    const paragraphs = processedText.split('\n');
    textDiv.innerHTML = paragraphs.map(p => `<p>${p || '&nbsp;'}</p>`).join('');

    bubble.appendChild(textDiv);

    // Metadata Badges (Bot Only)
    if (!isUser && meta.data_structure) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';

        // Data structure badge
        const dsBadge = document.createElement('span');
        dsBadge.className = 'ds-badge';
        dsBadge.textContent = `Used: ${meta.data_structure}`;
        metaDiv.appendChild(dsBadge);

        // Highlight the used data structures in sidebar
        highlightDataStructures(meta.data_structure);

        bubble.appendChild(metaDiv);
    }

    content.appendChild(label);
    content.appendChild(bubble);
    messageDiv.appendChild(content);
    elements.chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

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

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

/**
 * Highlight data structures in the sidebar
 * Handles multiple DS names separated by commas
 */
function highlightDataStructures(dsString) {
    if (!dsString) return;

    // Remove all highlights first
    document.querySelectorAll('.ds-item').forEach(item => {
        item.classList.remove('active');
    });

    const dsLower = dsString.toLowerCase();

    // Check each data structure
    if (dsLower.includes('trie')) {
        elements.dsTrie?.classList.add('active');
    }
    if (dsLower.includes('hashmap') || dsLower.includes('hash')) {
        elements.dsHashmap?.classList.add('active');
    }
    if (dsLower.includes('decision tree') || dsLower.includes('tree')) {
        elements.dsTree?.classList.add('active');
    }
    if (dsLower.includes('stack')) {
        elements.dsStack?.classList.add('active');
    }
    if (dsLower.includes('union-find') || dsLower.includes('union')) {
        elements.dsUnionFind?.classList.add('active');
    }
    if (dsLower.includes('graph') || dsLower.includes('weighted')) {
        elements.dsGraph?.classList.add('active');
    }
}

function showSuggestions(suggestions, prefix) {
    if (!suggestions || suggestions.length === 0) {
        hideSuggestions();
        return;
    }

    elements.suggestionsList.innerHTML = '';

    suggestions.forEach(word => {
        const li = document.createElement('li');
        li.className = 'suggestion-item';
        li.innerHTML = highlightPrefix(word, prefix);
        li.addEventListener('click', () => {
            elements.userInput.value = word;
            hideSuggestions();
            elements.userInput.focus();
        });
        elements.suggestionsList.appendChild(li);
    });

    elements.suggestionsDropdown.classList.remove('hidden');
    
    // Highlight Trie when showing suggestions
    highlightDataStructures('Trie');
}

function hideSuggestions() {
    elements.suggestionsDropdown.classList.add('hidden');
}

// ============ API Functions ============

const fetchSuggestions = debounce(async (prefix) => {
    if (!prefix || prefix.length < 2) {
        hideSuggestions();
        return;
    }

    if (prefix === state.lastPrefix) return;
    state.lastPrefix = prefix;

    try {
        const data = await apiRequest(`/api/suggestions?prefix=${encodeURIComponent(prefix)}`);
        showSuggestions(data.suggestions, prefix);
    } catch (error) {
        console.error('Failed to fetch suggestions:', error);
        hideSuggestions();
    }
}, CONFIG.DEBOUNCE_MS);

async function sendMessage(message) {
    if (state.isLoading || !message.trim()) return;

    state.isLoading = true;
    hideSuggestions();

    addMessage(message, true);
    elements.userInput.value = '';
    state.lastPrefix = '';

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

        addMessage(data.response, false, {
            module: data.module,
            data_structure: data.data_structure
        });

    } catch (error) {
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', false);
    } finally {
        state.isLoading = false;
    }
}

async function resetConversation() {
    try {
        await apiRequest('/api/reset', {
            method: 'POST',
            body: JSON.stringify({ user_id: CONFIG.USER_ID })
        });

        elements.chatMessages.innerHTML = '';

        addMessage('System reset complete. How can I help you today?', false, {
            data_structure: 'Stack, Decision Tree'
        });

        // Reset sidebar highlights
        document.querySelectorAll('.ds-item.active').forEach(el => el.classList.remove('active'));

    } catch (error) {
        console.error('Failed to reset conversation:', error);
    }
}

// ============ Event Listeners ============

// Sidebar expand/collapse
document.querySelectorAll('.ds-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.ds-item').forEach(other => {
            if (other !== item) other.classList.remove('expanded');
        });
        item.classList.toggle('expanded');
    });
});

// Input typing - trigger suggestions
elements.userInput.addEventListener('input', (e) => {
    const value = e.target.value.trim();
    fetchSuggestions(value);
});

// Input keydown
elements.userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(elements.userInput.value);
    } else if (e.key === 'Escape') {
        hideSuggestions();
    }
});

// Send button
elements.sendButton.addEventListener('click', () => {
    sendMessage(elements.userInput.value);
});

// Reset button
elements.resetButton.addEventListener('click', () => {
    resetConversation();
});

// Hide suggestions on outside click
document.addEventListener('click', (e) => {
    if (!elements.suggestionsDropdown.contains(e.target) &&
        e.target !== elements.userInput) {
        hideSuggestions();
    }
});

// ============ Initialization ============

function init() {
    console.log('E-Shop Customer Support initialized');
    console.log('User ID:', CONFIG.USER_ID);
    console.log('Data Structures: Trie, HashMap, Decision Tree, Stack, Union-Find, Weighted Graph');
    elements.userInput.focus();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
