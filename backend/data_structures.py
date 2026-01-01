"""
Data Structures Module for Smart Customer Support System

This module contains all core data structure implementations used in the system.
Each class is designed to demonstrate a specific data structure's practical application.

Data Structures Implemented:
1. Trie (Prefix Tree) - For auto-suggestions and keyword completion
2. QueryQueue - FIFO queue for fair query processing
3. PriorityQueue - For urgent query prioritization
4. FAQHashMap - Dictionary for O(1) response lookup
5. ConversationTree - Tree structure for conversation flow
6. RecentInteractionCache - Bounded deque for recent context

Author: Smart Customer Support System
"""

import heapq
from collections import deque
from typing import List, Dict, Tuple, Optional, Any


# =============================================================================
# FEATURE 6: TRIE (PREFIX TREE) - Auto-Suggestion & Keyword Completion
# =============================================================================

class TrieNode:
    """
    A node in the Trie data structure.
    
    WHY TRIE FOR PREFIX SEARCH:
    - Time Complexity: O(m) where m is the length of the prefix
    - Unlike list scanning which is O(n*m) where n is number of words
    - Trie allows us to traverse directly to the prefix and collect all words below
    - Memory efficient for words with common prefixes (shared nodes)
    - Perfect for real-time suggestions as user types character by character
    
    Attributes:
        children (dict): Maps characters to child TrieNode objects
        is_end_of_word (bool): Marks if this node completes a valid word
    """
    
    def __init__(self):
        # Dictionary to store child nodes - each key is a character
        # Using dict gives O(1) average case child lookup
        self.children: Dict[str, 'TrieNode'] = {}
        
        # Flag to mark end of a complete word
        self.is_end_of_word: bool = False


class Trie:
    """
    Trie (Prefix Tree) implementation for auto-suggestions.
    
    DATA STRUCTURE: Trie (Prefix Tree)
    
    WHY TRIE IS SUPERIOR FOR PREFIX SEARCH:
    1. O(m) lookup time where m = prefix length (independent of dictionary size)
    2. O(m) insertion time
    3. Natural prefix grouping - all words with same prefix share path
    4. Memory efficient for words with common prefixes
    5. Supports efficient prefix-based retrieval without scanning all words
    
    COMPARISON WITH ALTERNATIVES:
    - List/Array scan: O(n*m) - must check every word
    - HashMap: O(1) for exact match, but O(n) for prefix search
    - Binary Search: O(log n * m) - better but still not optimal for prefix
    - Trie: O(m) for prefix search - independent of dictionary size!
    
    Operations:
        insert(word): Add a word to the Trie - O(m)
        search(word): Check if exact word exists - O(m)
        get_suggestions(prefix): Get all words with given prefix - O(m + k)
                                 where k is number of matching words
    """
    
    def __init__(self):
        """Initialize the Trie with an empty root node."""
        self.root = TrieNode()
        self._word_count = 0
    
    def insert(self, word: str) -> None:
        """
        Insert a word into the Trie.
        
        Time Complexity: O(m) where m is the length of the word
        Space Complexity: O(m) in worst case (no shared prefixes)
        
        Args:
            word: The word to insert (converted to lowercase)
        """
        word = word.lower().strip()
        if not word:
            return
            
        node = self.root
        
        # Traverse/create path for each character
        for char in word:
            if char not in node.children:
                # Create new node if character path doesn't exist
                node.children[char] = TrieNode()
            node = node.children[char]
        
        # Mark end of word
        if not node.is_end_of_word:
            node.is_end_of_word = True
            self._word_count += 1
    
    def search(self, word: str) -> bool:
        """
        Search for an exact word in the Trie.
        
        Time Complexity: O(m) where m is the length of the word
        
        Args:
            word: The word to search for
            
        Returns:
            True if the word exists, False otherwise
        """
        word = word.lower().strip()
        node = self._find_node(word)
        return node is not None and node.is_end_of_word
    
    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        """
        Find the node corresponding to the given prefix.
        
        Args:
            prefix: The prefix to search for
            
        Returns:
            The TrieNode at the end of prefix path, or None if not found
        """
        node = self.root
        
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        
        return node
    
    def get_suggestions(self, prefix: str, max_suggestions: int = 10) -> List[str]:
        """
        Get all word suggestions that start with the given prefix.
        
        THIS IS THE KEY OPERATION DEMONSTRATING TRIE EFFICIENCY:
        - We traverse directly to the prefix node in O(m) time
        - Then collect all words below that node
        - No need to scan through entire word list!
        
        Time Complexity: O(m + k) where m = prefix length, k = number of matches
        
        Args:
            prefix: The prefix to find suggestions for
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of words that start with the given prefix
        """
        prefix = prefix.lower().strip()
        suggestions = []
        
        if not prefix:
            return suggestions
        
        # Find the node at end of prefix path
        node = self._find_node(prefix)
        
        if node is None:
            return suggestions
        
        # Use DFS to collect all words below this node
        self._collect_words(node, prefix, suggestions, max_suggestions)
        
        return suggestions
    
    def _collect_words(self, node: TrieNode, current_word: str, 
                       suggestions: List[str], max_suggestions: int) -> None:
        """
        Recursively collect all words starting from a node using DFS.
        
        Args:
            node: Current node in traversal
            current_word: Word built so far
            suggestions: List to append found words to
            max_suggestions: Maximum suggestions to collect
        """
        if len(suggestions) >= max_suggestions:
            return
        
        # If current node marks end of word, add to suggestions
        if node.is_end_of_word:
            suggestions.append(current_word)
        
        # Recursively explore all children (alphabetically sorted for consistency)
        for char in sorted(node.children.keys()):
            if len(suggestions) >= max_suggestions:
                return
            self._collect_words(node.children[char], current_word + char, 
                              suggestions, max_suggestions)
    
    def get_word_count(self) -> int:
        """Return the total number of words in the Trie."""
        return self._word_count


# =============================================================================
# FEATURE 1: QUERY QUEUE - FIFO Query Management
# =============================================================================

class QueryQueue:
    """
    FIFO Queue for managing customer queries.
    
    DATA STRUCTURE: Queue (collections.deque)
    
    WHY DEQUE FOR QUEUE:
    1. O(1) append and popleft operations (vs O(n) for list.pop(0))
    2. Thread-safe append and pop operations
    3. Optimized for operations at both ends
    4. Memory efficient with contiguous storage
    
    COMPARISON WITH LIST:
    - list.pop(0): O(n) - requires shifting all elements
    - deque.popleft(): O(1) - no shifting needed
    
    This ensures FAIRNESS: First query in = First query processed
    """
    
    def __init__(self):
        """Initialize an empty query queue using deque."""
        # Using deque for O(1) operations at both ends
        self._queue: deque = deque()
        self._query_counter = 0
    
    def enqueue(self, query: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Add a query to the end of the queue.
        
        Time Complexity: O(1)
        
        Args:
            query: The customer's query text
            user_id: Identifier for the customer
            
        Returns:
            Dictionary with query details and position in queue
        """
        self._query_counter += 1
        query_data = {
            "id": self._query_counter,
            "query": query,
            "user_id": user_id,
            "position": len(self._queue) + 1
        }
        self._queue.append(query_data)
        return query_data
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """
        Remove and return the first query from the queue.
        
        Time Complexity: O(1) - This is why we use deque!
        
        Returns:
            The query data dictionary, or None if queue is empty
        """
        if self._queue:
            return self._queue.popleft()
        return None
    
    def peek(self) -> Optional[Dict[str, Any]]:
        """
        View the first query without removing it.
        
        Returns:
            The first query data, or None if empty
        """
        if self._queue:
            return self._queue[0]
        return None
    
    def size(self) -> int:
        """Return the current number of queries in the queue."""
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._queue) == 0
    
    def get_all_queries(self) -> List[Dict[str, Any]]:
        """Return a list of all queries in queue order (for display)."""
        return list(self._queue)


# =============================================================================
# FEATURE 2: PRIORITY QUEUE - Urgent Query Handling
# =============================================================================

class PriorityQueue:
    """
    Priority Queue for handling urgent customer queries.
    
    DATA STRUCTURE: Min-Heap (heapq)
    
    WHY HEAPQ FOR PRIORITY QUEUE:
    1. O(log n) insertion - maintains heap property efficiently
    2. O(1) peek at highest priority element
    3. O(log n) extraction of highest priority element
    4. Built-in Python module, no external dependencies
    
    PRIORITY LEVELS (lower number = higher priority):
    1 - CRITICAL: System errors, security issues
    2 - URGENT: Payment problems, account locked
    3 - HIGH: Order issues, complaints
    4 - NORMAL: General queries
    5 - LOW: Feedback, suggestions
    
    COMPARISON WITH ALTERNATIVES:
    - Sorted list: O(n) insertion, O(1) extraction
    - Unsorted list: O(1) insertion, O(n) extraction
    - Heap: O(log n) for both - balanced performance!
    """
    
    # Priority level definitions
    PRIORITY_CRITICAL = 1
    PRIORITY_URGENT = 2
    PRIORITY_HIGH = 3
    PRIORITY_NORMAL = 4
    PRIORITY_LOW = 5
    
    # Keywords that indicate urgency
    URGENT_KEYWORDS = {
        "urgent": PRIORITY_URGENT,
        "emergency": PRIORITY_CRITICAL,
        "critical": PRIORITY_CRITICAL,
        "asap": PRIORITY_URGENT,
        "immediately": PRIORITY_URGENT,
        "help": PRIORITY_HIGH,
        "problem": PRIORITY_HIGH,
        "error": PRIORITY_HIGH,
        "failed": PRIORITY_URGENT,
        "locked": PRIORITY_URGENT,
        "hacked": PRIORITY_CRITICAL,
        "stolen": PRIORITY_CRITICAL,
        "payment failed": PRIORITY_URGENT,
        "not working": PRIORITY_HIGH,
        "broken": PRIORITY_HIGH,
    }
    
    def __init__(self):
        """Initialize an empty priority queue using a heap."""
        # Heap stores tuples: (priority, counter, query_data)
        # Counter ensures FIFO order for same-priority items
        self._heap: List[Tuple[int, int, Dict[str, Any]]] = []
        self._counter = 0
    
    def _detect_priority(self, query: str) -> int:
        """
        Automatically detect priority level based on keywords in the query.
        
        Args:
            query: The customer's query text
            
        Returns:
            Priority level (1-5, lower = more urgent)
        """
        query_lower = query.lower()
        detected_priority = self.PRIORITY_NORMAL
        
        for keyword, priority in self.URGENT_KEYWORDS.items():
            if keyword in query_lower:
                # Take the highest priority (lowest number) found
                detected_priority = min(detected_priority, priority)
        
        return detected_priority
    
    def enqueue(self, query: str, user_id: str = "anonymous", 
                priority: Optional[int] = None) -> Dict[str, Any]:
        """
        Add a query to the priority queue.
        
        Time Complexity: O(log n) - heap insertion
        
        Args:
            query: The customer's query text
            user_id: Identifier for the customer
            priority: Optional manual priority (auto-detected if not provided)
            
        Returns:
            Dictionary with query details including detected priority
        """
        # Auto-detect priority if not provided
        if priority is None:
            priority = self._detect_priority(query)
        
        self._counter += 1
        query_data = {
            "id": self._counter,
            "query": query,
            "user_id": user_id,
            "priority": priority,
            "priority_label": self._get_priority_label(priority)
        }
        
        # Push to heap: (priority, counter, data)
        # Counter ensures FIFO within same priority
        heapq.heappush(self._heap, (priority, self._counter, query_data))
        
        return query_data
    
    def _get_priority_label(self, priority: int) -> str:
        """Convert priority number to human-readable label."""
        labels = {
            1: "CRITICAL",
            2: "URGENT", 
            3: "HIGH",
            4: "NORMAL",
            5: "LOW"
        }
        return labels.get(priority, "UNKNOWN")
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """
        Remove and return the highest priority query.
        
        Time Complexity: O(log n) - heap extraction
        
        Returns:
            The highest priority query data, or None if empty
        """
        if self._heap:
            _, _, query_data = heapq.heappop(self._heap)
            return query_data
        return None
    
    def peek(self) -> Optional[Dict[str, Any]]:
        """
        View the highest priority query without removing it.
        
        Time Complexity: O(1) - heap property ensures min is at index 0
        
        Returns:
            The highest priority query data, or None if empty
        """
        if self._heap:
            return self._heap[0][2]
        return None
    
    def size(self) -> int:
        """Return the current number of queries in the priority queue."""
        return len(self._heap)
    
    def is_empty(self) -> bool:
        """Check if the priority queue is empty."""
        return len(self._heap) == 0
    
    def has_urgent_queries(self) -> bool:
        """Check if there are any high-priority queries (priority <= 2)."""
        if self._heap:
            return self._heap[0][0] <= self.PRIORITY_URGENT
        return False


# =============================================================================
# FEATURE 3: FAQ HASHMAP - Instant Response Lookup
# =============================================================================

class FAQHashMap:
    """
    HashMap (Dictionary) for FAQ response lookup.
    
    DATA STRUCTURE: HashMap (Python dict)
    
    WHY HASHMAP FOR FAQ:
    1. O(1) average case lookup time - instant responses!
    2. O(1) insertion time for adding new FAQs
    3. No need to scan through all FAQs to find a match
    4. Perfect for keyword → response mapping
    
    HOW IT WORKS:
    - Each keyword maps to a response
    - User query is tokenized into keywords
    - Keywords are looked up in O(1) time each
    - Best matching response is returned
    
    COMPARISON WITH ALTERNATIVES:
    - List scan: O(n) - must check every FAQ
    - Binary search: O(log n) - requires sorted data
    - HashMap: O(1) average - unbeatable for lookup!
    """
    
    def __init__(self):
        """Initialize the FAQ HashMap with predefined responses."""
        # Primary keyword → response mapping
        # Using dict for O(1) lookup
        self._faq_map: Dict[str, Dict[str, str]] = {}
        
        # Category mapping for organization
        self._categories: Dict[str, List[str]] = {}
        
        # Load default FAQs
        self._load_default_faqs()
    
    def _load_default_faqs(self) -> None:
        """Load predefined FAQ entries into the HashMap."""
        
        # Refund related FAQs
        self.add_faq(
            keywords=["refund", "money back", "return money"],
            response="To request a refund, please go to Orders → Select Order → Request Refund. "
                    "Refunds are typically processed within 5-7 business days.",
            category="refunds"
        )
        
        # Order status FAQs
        self.add_faq(
            keywords=["order status", "where is my order", "track order", "tracking"],
            response="You can track your order by going to Orders → Track Order. "
                    "Enter your order ID to see real-time shipping updates.",
            category="orders"
        )
        
        # Shipping FAQs
        self.add_faq(
            keywords=["shipping", "delivery", "ship time", "delivery time"],
            response="Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days. "
                    "Free shipping is available on orders over $50.",
            category="shipping"
        )
        
        # Account FAQs
        self.add_faq(
            keywords=["password", "reset password", "forgot password", "change password"],
            response="To reset your password, click 'Forgot Password' on the login page. "
                    "We'll send a reset link to your registered email address.",
            category="account"
        )
        
        self.add_faq(
            keywords=["account", "create account", "sign up", "register"],
            response="Creating an account is easy! Click 'Sign Up', enter your email and create a password. "
                    "You'll receive a confirmation email to verify your account.",
            category="account"
        )
        
        # Payment FAQs
        self.add_faq(
            keywords=["payment", "pay", "payment methods", "credit card", "debit card"],
            response="We accept Visa, MasterCard, American Express, PayPal, and Apple Pay. "
                    "All payments are encrypted and secure.",
            category="payment"
        )
        
        self.add_faq(
            keywords=["cancel order", "cancel", "cancellation"],
            response="You can cancel your order within 24 hours of placing it. "
                    "Go to Orders → Select Order → Cancel Order. After 24 hours, please contact support.",
            category="orders"
        )
        
        # Returns FAQs
        self.add_faq(
            keywords=["return", "return policy", "exchange", "swap"],
            response="We offer 30-day returns on most items. Items must be unused and in original packaging. "
                    "Go to Orders → Select Order → Initiate Return to start the process.",
            category="returns"
        )
        
        # Contact FAQs
        self.add_faq(
            keywords=["contact", "phone", "email", "reach", "talk to human", "agent"],
            response="You can reach us at support@example.com or call 1-800-SUPPORT (Mon-Fri, 9AM-6PM EST). "
                    "Live chat is available 24/7.",
            category="contact"
        )
        
        # General help
        self.add_faq(
            keywords=["help", "support", "assist", "assistance"],
            response="I'm here to help! You can ask me about orders, shipping, returns, refunds, "
                    "account issues, or payments. What do you need assistance with?",
            category="general"
        )
        
        # Greeting
        self.add_faq(
            keywords=["hello", "hi", "hey", "greetings", "good morning", "good afternoon"],
            response="Hello! Welcome to our customer support. How can I assist you today? "
                    "I can help with orders, shipping, returns, refunds, and more.",
            category="greeting"
        )
        
        # Thanks
        self.add_faq(
            keywords=["thank", "thanks", "thank you", "appreciate"],
            response="You're welcome! Is there anything else I can help you with today?",
            category="greeting"
        )
        
        # Goodbye
        self.add_faq(
            keywords=["bye", "goodbye", "see you", "exit", "quit"],
            response="Thank you for contacting us! Have a great day. "
                    "Feel free to reach out if you need any further assistance.",
            category="greeting"
        )
    
    def add_faq(self, keywords: List[str], response: str, category: str = "general") -> None:
        """
        Add a new FAQ entry to the HashMap.
        
        Time Complexity: O(k) where k is the number of keywords
        
        Args:
            keywords: List of keywords that trigger this response
            response: The response text
            category: Category for organization
        """
        faq_entry = {
            "response": response,
            "category": category,
            "keywords": keywords
        }
        
        # Map each keyword to the FAQ entry
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            self._faq_map[keyword_lower] = faq_entry
        
        # Update category index
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].extend(keywords)
    
    def lookup(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Look up a response for the given query.
        
        This demonstrates O(1) HashMap lookup:
        - Tokenize query into words
        - Check each word in HashMap
        - Return first match found
        
        Time Complexity: O(w) where w is number of words in query
                        Each word lookup is O(1)!
        
        Args:
            query: The user's query text
            
        Returns:
            Dictionary with response and metadata, or None if no match
        """
        query_lower = query.lower().strip()
        
        # First, try exact phrase match
        if query_lower in self._faq_map:
            return {
                "response": self._faq_map[query_lower]["response"],
                "category": self._faq_map[query_lower]["category"],
                "matched_keyword": query_lower,
                "match_type": "exact"
            }
        
        # Then, try multi-word keyword matches
        for keyword in self._faq_map:
            if keyword in query_lower:
                return {
                    "response": self._faq_map[keyword]["response"],
                    "category": self._faq_map[keyword]["category"],
                    "matched_keyword": keyword,
                    "match_type": "phrase"
                }
        
        # Finally, try single word matches
        words = query_lower.split()
        for word in words:
            if word in self._faq_map:
                return {
                    "response": self._faq_map[word]["response"],
                    "category": self._faq_map[word]["category"],
                    "matched_keyword": word,
                    "match_type": "word"
                }
        
        return None
    
    def get_all_keywords(self) -> List[str]:
        """Return all FAQ keywords (for populating the Trie)."""
        return list(self._faq_map.keys())
    
    def get_categories(self) -> List[str]:
        """Return all FAQ categories."""
        return list(self._categories.keys())
    
    def size(self) -> int:
        """Return the number of FAQ entries."""
        return len(self._faq_map)


# =============================================================================
# FEATURE 4: CONVERSATION TREE - Structured Conversation Flow
# =============================================================================

class ConversationTreeNode:
    """
    A node in the Conversation Tree.
    
    Each node represents a state in the conversation with:
    - A response message
    - Possible follow-up options (branches)
    - Metadata about the conversation context
    """
    
    def __init__(self, node_id: str, message: str, options: Optional[Dict[str, str]] = None):
        """
        Initialize a conversation tree node.
        
        Args:
            node_id: Unique identifier for this node
            message: The bot's response message at this node
            options: Dict mapping option keywords to child node IDs
        """
        self.node_id = node_id
        self.message = message
        self.options = options or {}  # keyword -> child_node_id
        self.children: Dict[str, 'ConversationTreeNode'] = {}


class ConversationTree:
    """
    Tree structure for managing conversation flow.
    
    DATA STRUCTURE: Tree (implemented with dictionaries and custom nodes)
    
    WHY TREE FOR CONVERSATION FLOW:
    1. Natural hierarchical representation of conversation paths
    2. Each node is a conversation state with branching options
    3. Easy to traverse based on user input
    4. Supports multi-level, context-aware responses
    5. Clear parent-child relationships model conversation progression
    
    STRUCTURE:
    - Root node: Initial greeting/state
    - Internal nodes: Conversation states with options
    - Leaf nodes: Final responses/resolution states
    
    COMPARISON WITH ALTERNATIVES:
    - Flat dictionary: No natural hierarchy, harder to manage context
    - List: Linear structure doesn't represent branching
    - Graph: Overly complex for structured conversation
    - Tree: Perfect balance of structure and flexibility!
    """
    
    def __init__(self):
        """Initialize the conversation tree with predefined flows."""
        # Store all nodes by ID for quick access
        self._nodes: Dict[str, ConversationTreeNode] = {}
        
        # Track current position in tree for each user session
        self._user_positions: Dict[str, str] = {}
        
        # Build the conversation tree
        self._build_tree()
    
    def _build_tree(self) -> None:
        """Build the conversation tree structure."""
        
        # Root node - Entry point
        self._add_node(
            "root",
            "Welcome! I can help you with:\n"
            "• Orders - Check status, track, or cancel\n"
            "• Returns - Initiate or check return status\n"
            "• Account - Password, settings, profile\n"
            "• Billing - Payment issues, invoices\n\n"
            "What would you like help with?",
            {"orders": "orders_menu", "returns": "returns_menu", 
             "account": "account_menu", "billing": "billing_menu",
             "order": "orders_menu", "return": "returns_menu",
             "payment": "billing_menu", "bill": "billing_menu"}
        )
        
        # Orders branch
        self._add_node(
            "orders_menu",
            "I can help you with orders. What do you need?\n"
            "• Track - Check order status\n"
            "• Cancel - Cancel an order\n"
            "• History - View past orders",
            {"track": "order_track", "cancel": "order_cancel", 
             "history": "order_history", "status": "order_track"}
        )
        
        self._add_node(
            "order_track",
            "To track your order:\n"
            "1. Go to 'My Orders' in your account\n"
            "2. Click on the order you want to track\n"
            "3. View real-time shipping updates\n\n"
            "Do you have your order ID? I can look it up for you.",
            {"yes": "order_track_with_id", "no": "order_track_help"}
        )
        
        self._add_node(
            "order_track_with_id",
            "Please enter your Order ID (format: ORD-XXXXX) and I'll check the status for you.\n"
            "For this demo, any order ID will show sample tracking info.",
            {}
        )
        
        self._add_node(
            "order_track_help",
            "No problem! You can find your Order ID in:\n"
            "• Your confirmation email\n"
            "• The 'My Orders' section of your account\n\n"
            "Would you like help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "order_cancel",
            "To cancel an order:\n"
            "1. Orders can be cancelled within 24 hours of placing\n"
            "2. Go to 'My Orders' → Select Order → 'Cancel Order'\n"
            "3. Select a cancellation reason\n\n"
            "Is your order within the 24-hour window?",
            {"yes": "order_cancel_confirm", "no": "order_cancel_late"}
        )
        
        self._add_node(
            "order_cancel_confirm",
            "You should be able to cancel directly from your account. "
            "If you face any issues, please contact support with your Order ID.\n\n"
            "Can I help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "order_cancel_late",
            "Since it's past 24 hours, you may need to:\n"
            "1. Wait for delivery and then initiate a return, OR\n"
            "2. Contact support for special cancellation request\n\n"
            "Would you like information on returns?",
            {"yes": "returns_menu", "no": "root"}
        )
        
        self._add_node(
            "order_history",
            "To view your order history:\n"
            "1. Log into your account\n"
            "2. Go to 'My Orders'\n"
            "3. View all past and current orders\n\n"
            "You can filter by date, status, or search by product name.\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        # Returns branch
        self._add_node(
            "returns_menu",
            "I can help with returns. What do you need?\n"
            "• Start - Initiate a new return\n"
            "• Status - Check return status\n"
            "• Policy - View return policy",
            {"start": "return_start", "status": "return_status", 
             "policy": "return_policy", "initiate": "return_start"}
        )
        
        self._add_node(
            "return_start",
            "To start a return:\n"
            "1. Go to 'My Orders' → Select the order\n"
            "2. Click 'Return Items' \n"
            "3. Select items and reason for return\n"
            "4. Choose refund or exchange\n"
            "5. Print the prepaid shipping label\n\n"
            "Is your item within 30 days of delivery?",
            {"yes": "return_eligible", "no": "return_not_eligible"}
        )
        
        self._add_node(
            "return_eligible",
            "Your item should be eligible for return. Please make sure:\n"
            "• Item is unused and in original condition\n"
            "• Original packaging and tags are intact\n"
            "• All accessories are included\n\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "return_not_eligible",
            "Unfortunately, items past 30 days may not be eligible for standard return. "
            "However, you can:\n"
            "1. Check if the item has extended warranty\n"
            "2. Contact support for exceptions\n\n"
            "Would you like to explore other options?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "return_status",
            "To check your return status:\n"
            "1. Go to 'My Orders' → 'Returns'\n"
            "2. View status of all return requests\n\n"
            "Return processing typically takes 5-7 business days after we receive the item.\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "return_policy",
            "Our Return Policy:\n"
            "• 30-day return window from delivery date\n"
            "• Items must be unused and in original packaging\n"
            "• Free returns on most items\n"
            "• Refunds processed within 5-7 business days\n"
            "• Some items (e.g., personalized) are non-returnable\n\n"
            "Can I help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        # Account branch
        self._add_node(
            "account_menu",
            "I can help with your account. What do you need?\n"
            "• Password - Reset or change password\n"
            "• Profile - Update your information\n"
            "• Settings - Account preferences",
            {"password": "account_password", "profile": "account_profile", 
             "settings": "account_settings"}
        )
        
        self._add_node(
            "account_password",
            "To reset your password:\n"
            "1. Click 'Forgot Password' on login page\n"
            "2. Enter your registered email\n"
            "3. Check email for reset link (check spam too!)\n"
            "4. Create a new secure password\n\n"
            "Having trouble receiving the email?",
            {"yes": "account_password_help", "no": "root"}
        )
        
        self._add_node(
            "account_password_help",
            "If you're not receiving the reset email:\n"
            "1. Check your spam/junk folder\n"
            "2. Add support@example.com to contacts\n"
            "3. Try again in a few minutes\n"
            "4. If still having issues, contact support\n\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "account_profile",
            "To update your profile:\n"
            "1. Go to Account → Profile\n"
            "2. Update name, email, or phone\n"
            "3. Save changes\n\n"
            "Note: Changing email requires verification.\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "account_settings",
            "Account settings you can manage:\n"
            "• Notifications - Email and SMS preferences\n"
            "• Privacy - Data sharing settings\n"
            "• Connected apps - Third-party access\n"
            "• Delete account - Permanently remove account\n\n"
            "What would you like to update?",
            {"notifications": "settings_notifications", "privacy": "settings_privacy",
             "delete": "settings_delete"}
        )
        
        self._add_node(
            "settings_notifications",
            "To manage notifications:\n"
            "1. Go to Account → Settings → Notifications\n"
            "2. Toggle email/SMS for different types\n"
            "3. Save preferences\n\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "settings_privacy",
            "Privacy settings available:\n"
            "• Data sharing with partners\n"
            "• Personalized ads\n"
            "• Activity tracking\n\n"
            "Go to Account → Settings → Privacy to manage these.\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "settings_delete",
            "⚠️ Account deletion is permanent!\n\n"
            "Before deleting:\n"
            "• Download your data first\n"
            "• Cancel any active subscriptions\n"
            "• Complete any pending orders\n\n"
            "To delete: Account → Settings → Delete Account\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        # Billing branch
        self._add_node(
            "billing_menu",
            "I can help with billing. What do you need?\n"
            "• Payment - Update payment method\n"
            "• Invoice - View or download invoices\n"
            "• Issue - Report a billing problem",
            {"payment": "billing_payment", "invoice": "billing_invoice", 
             "issue": "billing_issue", "problem": "billing_issue"}
        )
        
        self._add_node(
            "billing_payment",
            "To update payment methods:\n"
            "1. Go to Account → Payment Methods\n"
            "2. Add, edit, or remove cards\n"
            "3. Set a default payment method\n\n"
            "We accept Visa, MasterCard, Amex, and PayPal.\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "billing_invoice",
            "To access invoices:\n"
            "1. Go to Account → Order History\n"
            "2. Click on an order\n"
            "3. Download Invoice (PDF)\n\n"
            "Invoices are also emailed after purchase.\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "billing_issue",
            "For billing issues:\n"
            "• Duplicate charge - We'll investigate and refund if confirmed\n"
            "• Wrong amount - Please share order details\n"
            "• Failed payment - Check card details and try again\n\n"
            "What type of issue are you experiencing?",
            {"duplicate": "billing_duplicate", "wrong": "billing_wrong", 
             "failed": "billing_failed"}
        )
        
        self._add_node(
            "billing_duplicate",
            "If you see a duplicate charge:\n"
            "1. Sometimes pending charges clear automatically\n"
            "2. Wait 24-48 hours for it to resolve\n"
            "3. If still duplicated, contact support with order ID\n\n"
            "We'll investigate and refund any confirmed duplicates.\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "billing_wrong",
            "For incorrect charge amounts:\n"
            "1. Check if tax or shipping was added\n"
            "2. Verify any applied discounts\n"
            "3. Compare with order confirmation email\n\n"
            "If still incorrect, contact support with details.\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        self._add_node(
            "billing_failed",
            "Payment failure troubleshooting:\n"
            "1. Verify card details and expiry date\n"
            "2. Ensure sufficient funds/credit\n"
            "3. Try a different payment method\n"
            "4. Check if your bank blocked the transaction\n\n"
            "If issues persist, contact your bank or our support.\n"
            "Need help with anything else?",
            {"yes": "root", "no": "goodbye"}
        )
        
        # Goodbye node
        self._add_node(
            "goodbye",
            "Thank you for using our support system! 👋\n\n"
            "If you need help in the future, I'm always here.\n"
            "Have a wonderful day!",
            {}
        )
    
    def _add_node(self, node_id: str, message: str, 
                  options: Optional[Dict[str, str]] = None) -> None:
        """Add a node to the tree."""
        self._nodes[node_id] = ConversationTreeNode(node_id, message, options)
    
    def get_response(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """
        Get the next response based on user input.
        
        This demonstrates TREE TRAVERSAL:
        - Start at current node (or root for new users)
        - Find matching option based on user input
        - Move to child node
        - Return the child node's message
        
        Time Complexity: O(k) where k is number of options at current node
        
        Args:
            user_id: Unique identifier for the user session
            user_input: The user's input text
            
        Returns:
            Dictionary with response and navigation info
        """
        # Get current position or start at root
        current_node_id = self._user_positions.get(user_id, "root")
        current_node = self._nodes.get(current_node_id, self._nodes["root"])
        
        # Process user input
        user_input_lower = user_input.lower().strip()
        
        # Find matching option
        next_node_id = None
        matched_option = None
        
        for option_keyword, child_node_id in current_node.options.items():
            if option_keyword in user_input_lower:
                next_node_id = child_node_id
                matched_option = option_keyword
                break
        
        # If no match found, stay at current node or go to root
        if next_node_id is None:
            # Check if input matches any root-level option for navigation
            root_node = self._nodes["root"]
            for option_keyword, child_node_id in root_node.options.items():
                if option_keyword in user_input_lower:
                    next_node_id = child_node_id
                    matched_option = option_keyword
                    break
        
        # If still no match, go to root
        if next_node_id is None:
            next_node_id = "root"
        
        # Update user position
        self._user_positions[user_id] = next_node_id
        next_node = self._nodes[next_node_id]
        
        return {
            "response": next_node.message,
            "node_id": next_node_id,
            "matched_option": matched_option,
            "available_options": list(next_node.options.keys()),
            "is_leaf": len(next_node.options) == 0
        }
    
    def reset_conversation(self, user_id: str) -> None:
        """Reset the conversation to the root node for a user."""
        self._user_positions[user_id] = "root"
    
    def get_current_node(self, user_id: str) -> Optional[ConversationTreeNode]:
        """Get the current node for a user session."""
        node_id = self._user_positions.get(user_id, "root")
        return self._nodes.get(node_id)


# =============================================================================
# FEATURE 7: RECENT INTERACTION CACHE - Short-term Memory
# =============================================================================

class RecentInteractionCache:
    """
    Bounded cache for storing recent interactions.
    
    DATA STRUCTURE: Deque with maxlen (collections.deque)
    
    WHY DEQUE (WITH MAXLEN) FOR RECENT CACHE:
    1. O(1) append operation - adds new interaction instantly
    2. AUTOMATIC removal of oldest when capacity exceeded (no manual cleanup!)
    3. O(1) access to both ends (most recent and oldest)
    4. Memory bounded - prevents unbounded growth
    5. Thread-safe for append and pop operations
    
    COMPARISON WITH LIST:
    - List: Would need manual size checking and removal
    - List: Removing from front is O(n)
    - Deque: Automatic size management with maxlen
    - Deque: O(1) operations at both ends
    
    WHY BOUNDED SIZE IS IMPORTANT:
    - Prevents memory from growing indefinitely
    - Keeps only relevant recent context
    - Simulates short-term memory
    - Efficient for showing "recent history" features
    
    Use Case: Storing last N interactions for context-aware responses
    """
    
    def __init__(self, max_size: int = 5):
        """
        Initialize the cache with a maximum size.
        
        Args:
            max_size: Maximum number of interactions to store (default: 5)
        """
        # Using deque with maxlen for automatic size management
        # When full, adding new item automatically removes oldest
        self._cache: deque = deque(maxlen=max_size)
        self._max_size = max_size
        self._interaction_count = 0
    
    def add_interaction(self, user_message: str, bot_response: str, 
                       module_used: str, data_structure: str) -> Dict[str, Any]:
        """
        Add a new interaction to the cache.
        
        Time Complexity: O(1) - deque.append is constant time
        Note: If cache is full, oldest item is AUTOMATICALLY removed!
        
        Args:
            user_message: The user's input
            bot_response: The bot's response
            module_used: Which module processed this
            data_structure: Which data structure was used
            
        Returns:
            The interaction record that was added
        """
        self._interaction_count += 1
        
        interaction = {
            "id": self._interaction_count,
            "user": user_message,
            "bot": bot_response[:100] + "..." if len(bot_response) > 100 else bot_response,
            "module": module_used,
            "data_structure": data_structure
        }
        
        # Append to deque - if full, oldest is automatically removed!
        self._cache.append(interaction)
        
        return interaction
    
    def get_recent_context(self) -> List[Dict[str, Any]]:
        """
        Get all recent interactions in chronological order.
        
        Time Complexity: O(n) where n is cache size (max 5 typically)
        
        Returns:
            List of recent interactions, oldest first
        """
        return list(self._cache)
    
    def get_last_interaction(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent interaction.
        
        Time Complexity: O(1) - direct access to last element
        
        Returns:
            The most recent interaction, or None if empty
        """
        if self._cache:
            return self._cache[-1]
        return None
    
    def get_context_summary(self) -> str:
        """
        Get a text summary of recent context for display.
        
        Returns:
            Formatted string summarizing recent interactions
        """
        if not self._cache:
            return "No recent interactions."
        
        lines = ["📋 Recent Conversation History:"]
        for idx, interaction in enumerate(self._cache, 1):
            lines.append(f"{idx}. User: {interaction['user'][:50]}...")
        
        return "\n".join(lines)
    
    def clear(self) -> None:
        """Clear all cached interactions."""
        self._cache.clear()
    
    def size(self) -> int:
        """Return the current number of cached interactions."""
        return len(self._cache)
    
    def max_size(self) -> int:
        """Return the maximum cache size."""
        return self._max_size
    
    def is_full(self) -> bool:
        """Check if the cache is at maximum capacity."""
        return len(self._cache) >= self._max_size
