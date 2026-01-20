"""
Data Structures Module for E-Commerce Customer Support Chatbot

This module contains 10 core data structure implementations:
1. Trie - Auto-complete suggestions
2. HashMap (FAQHashMap) - O(1) FAQ lookups  
3. DecisionTree - Conversation flow with branching
4. Stack - "Go back" navigation
5. UnionFind - Synonym intent grouping
6. WeightedGraph - Next best action suggestions
7. OrderDatabase - O(1) order lookup by ID
8. UserProfile - HashMap + Stack for profile management
9. ShoppingCart - HashMap + Stack for cart with undo
10. Wishlist - HashMap for O(1) contains check
11. PriorityQueue - Heap for product recommendations
12. RecentlyViewedList - Doubly Linked List for browsing history
13. CheckoutQueue - FIFO Queue for checkout process

Author: Smart Customer Support System
"""


from typing import Dict, Any, List, Optional, Tuple
from collections import deque
import heapq


# =============================================================================
# DATA STRUCTURE 1: TRIE - Auto-Complete Suggestions
# =============================================================================

class TrieNode:
    """
    A node in the Trie data structure.
    
    TIME COMPLEXITY:
    - Child lookup: O(1) using dictionary
    """
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word: bool = False
        self.word: str = ""  # Store the complete word at end nodes


class Trie:
    """
    Trie (Prefix Tree) for auto-complete suggestions.
    
    DATA STRUCTURE: Trie (Prefix Tree)
    
    WHY TRIE FOR AUTO-COMPLETE:
    1. O(m) lookup where m = prefix length (independent of dictionary size)
    2. Natural prefix matching - finds all words starting with a prefix
    3. Memory efficient for words with common prefixes
    
    OPERATIONS:
    - insert(word): O(m) where m = word length
    - search(word): O(m)
    - get_suggestions(prefix): O(m + k) where k = number of matches
    """
    
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0
    
    def insert(self, word: str) -> None:
        """Insert a word into the Trie. O(m) time."""
        if not word:
            return
        
        word = word.lower().strip()
        node = self.root
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        if not node.is_end_of_word:
            node.is_end_of_word = True
            node.word = word
            self.word_count += 1
    
    def search(self, word: str) -> bool:
        """Search for exact word. O(m) time."""
        node = self._find_node(word.lower().strip())
        return node is not None and node.is_end_of_word
    
    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        """Find node at end of prefix path."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
    
    def get_suggestions(self, prefix: str, max_suggestions: int = 8) -> List[str]:
        """
        Get all words starting with prefix.
        
        TIME COMPLEXITY: O(m + k) where m = prefix length, k = matches
        
        Args:
            prefix: The prefix to search for
            max_suggestions: Maximum suggestions to return
            
        Returns:
            List of words starting with the prefix
        """
        prefix = prefix.lower().strip()
        if not prefix:
            return []
        
        node = self._find_node(prefix)
        if not node:
            return []
        
        suggestions = []
        self._collect_words(node, suggestions, max_suggestions)
        return suggestions
    
    def _collect_words(self, node: TrieNode, suggestions: List[str], max_count: int) -> None:
        """Recursively collect words using DFS."""
        if len(suggestions) >= max_count:
            return
        
        if node.is_end_of_word:
            suggestions.append(node.word)
        
        for child in node.children.values():
            if len(suggestions) >= max_count:
                return
            self._collect_words(child, suggestions, max_count)
    
    def get_word_count(self) -> int:
        """Return total words in Trie."""
        return self.word_count


# =============================================================================
# DATA STRUCTURE 2: HASHMAP - O(1) FAQ Lookups
# =============================================================================

class FAQHashMap:
    """
    HashMap (Dictionary) for FAQ response lookup.
    
    DATA STRUCTURE: HashMap (Python dict)
    
    WHY HASHMAP FOR FAQ:
    1. O(1) average lookup time - instant responses
    2. Perfect for keyword → response mapping
    3. Simple and efficient
    
    OPERATIONS:
    - add_faq(keywords, response): O(k) where k = number of keywords
    - lookup(query): O(w) where w = words in query, each lookup O(1)
    """
    
    def __init__(self):
        # Main storage: keyword → response data
        self._faq_map: Dict[str, Dict[str, Any]] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def add_faq(self, keywords: List[str], response: str, category: str = "general") -> None:
        """
        Add FAQ entry with multiple keywords.
        
        Args:
            keywords: List of trigger keywords
            response: The response text
            category: Category for organization
        """
        faq_data = {
            "response": response,
            "category": category,
            "keywords": keywords
        }
        
        for keyword in keywords:
            key = keyword.lower().strip()
            self._faq_map[key] = faq_data
        
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].extend(keywords)
    
    def lookup(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Look up response for query.
        
        TIME COMPLEXITY: O(w) where w = words in query
        Each word lookup is O(1)!
        
        Returns:
            Dictionary with response and metadata, or None
        """
        query_lower = query.lower().strip()
        
        # First try exact match
        if query_lower in self._faq_map:
            result = self._faq_map[query_lower].copy()
            result["matched_keyword"] = query_lower
            return result
        
        # Then try word-by-word matching
        words = query_lower.split()
        for word in words:
            if word in self._faq_map:
                result = self._faq_map[word].copy()
                result["matched_keyword"] = word
                return result
        
        return None
    
    def get_all_keywords(self) -> List[str]:
        """Return all FAQ keywords."""
        return list(self._faq_map.keys())
    
    def size(self) -> int:
        """Return number of unique FAQ entries."""
        return len(set(id(v) for v in self._faq_map.values()))


# =============================================================================
# DATA STRUCTURE 3: DECISION TREE - Conversation Flow
# =============================================================================

class DecisionNode:
    """A node in the Decision Tree."""
    
    def __init__(self, node_id: str, message: str, 
                 is_leaf: bool = False, 
                 options: Optional[Dict[str, str]] = None):
        """
        Args:
            node_id: Unique identifier
            message: Bot response at this node
            is_leaf: Whether this is an end node
            options: Dict mapping user choice → next node_id
        """
        self.node_id = node_id
        self.message = message
        self.is_leaf = is_leaf
        self.options = options or {}


class DecisionTree:
    """
    Decision Tree for conversation flow with branching.
    
    DATA STRUCTURE: Tree (with dictionaries for O(1) node lookup)
    
    WHY DECISION TREE FOR CONVERSATION:
    1. Natural representation of branching dialogues
    2. Each node = conversation state with response
    3. Edges = user choices leading to next states
    4. Easy to visualize and maintain
    
    OPERATIONS:
    - add_node(): O(1)
    - get_response(): O(1) node lookup + O(k) option matching
    - traverse(): Following tree paths
    """
    
    def __init__(self):
        self.nodes: Dict[str, DecisionNode] = {}
        self.root_id = "root"
        self.user_states: Dict[str, str] = {}  # user_id → current node_id
    
    def add_node(self, node_id: str, message: str, 
                 is_leaf: bool = False,
                 options: Optional[Dict[str, str]] = None) -> None:
        """Add a node to the tree."""
        self.nodes[node_id] = DecisionNode(node_id, message, is_leaf, options)
    
    def get_current_state(self, user_id: str) -> str:
        """Get current node for user."""
        return self.user_states.get(user_id, self.root_id)
    
    def get_response(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """
        Get response based on current state and user input.
        
        TIME COMPLEXITY: O(1) for node lookup, O(k) for option matching
        
        Returns:
            Dict with response, current_node, available_options
        """
        current_id = self.get_current_state(user_id)
        current_node = self.nodes.get(current_id)
        
        if not current_node:
            # Reset to root if node not found
            current_node = self.nodes.get(self.root_id)
            current_id = self.root_id
        
        # Find matching option based on user input
        user_lower = user_input.lower().strip()
        next_node_id = None
        
        for keyword, target_id in current_node.options.items():
            if keyword.lower() in user_lower or user_lower in keyword.lower():
                next_node_id = target_id
                break
        
        if next_node_id and next_node_id in self.nodes:
            # Transition to next node
            self.user_states[user_id] = next_node_id
            next_node = self.nodes[next_node_id]
            
            return {
                "response": next_node.message,
                "node_id": next_node_id,
                "previous_node": current_id,
                "is_leaf": next_node.is_leaf,
                "available_options": list(next_node.options.keys())
            }
        else:
            # No match - stay at current node, show options
            return {
                "response": current_node.message,
                "node_id": current_id,
                "previous_node": None,
                "is_leaf": current_node.is_leaf,
                "available_options": list(current_node.options.keys()),
                "no_match": True
            }
    
    def reset(self, user_id: str) -> None:
        """Reset user to root node."""
        self.user_states[user_id] = self.root_id
    
    def set_state(self, user_id: str, node_id: str) -> bool:
        """Set user to specific node. Returns False if node doesn't exist."""
        if node_id in self.nodes:
            self.user_states[user_id] = node_id
            return True
        return False


# =============================================================================
# DATA STRUCTURE 4: STACK - "Go Back" Navigation
# =============================================================================

class ConversationStack:
    """
    Stack for conversation history and "go back" functionality.
    
    DATA STRUCTURE: Stack (using Python list)
    
    WHY STACK FOR NAVIGATION:
    1. LIFO (Last In, First Out) - perfect for backtracking
    2. O(1) push and pop operations
    3. Natural fit for "undo" and "go back" features
    
    OPERATIONS:
    - push(state): O(1)
    - pop(): O(1)
    - peek(): O(1)
    """
    
    def __init__(self, max_size: int = 10):
        self._stack: List[Dict[str, Any]] = []
        self._max_size = max_size
    
    def push(self, state_id: str, message: str = "") -> None:
        """
        Push a state onto the stack.
        
        TIME COMPLEXITY: O(1)
        """
        state = {
            "node_id": state_id,
            "message": message
        }
        
        if len(self._stack) >= self._max_size:
            # Remove oldest to make room
            self._stack.pop(0)
        
        self._stack.append(state)
    
    def pop(self) -> Optional[Dict[str, Any]]:
        """
        Pop and return the most recent state.
        
        TIME COMPLEXITY: O(1)
        """
        if self._stack:
            return self._stack.pop()
        return None
    
    def peek(self) -> Optional[Dict[str, Any]]:
        """View top state without removing. O(1)"""
        if self._stack:
            return self._stack[-1]
        return None
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get full history stack."""
        return list(self._stack)
    
    def size(self) -> int:
        """Return stack size."""
        return len(self._stack)
    
    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self._stack) == 0
    
    def clear(self) -> None:
        """Clear the stack."""
        self._stack.clear()


# =============================================================================
# DATA STRUCTURE 5: UNION-FIND - Synonym Intent Grouping
# =============================================================================

class UnionFind:
    """
    Union-Find (Disjoint Set) for grouping equivalent intents.
    
    DATA STRUCTURE: Union-Find with path compression and union by rank
    
    WHY UNION-FIND FOR SYNONYMS:
    1. Groups equivalent phrases that mean the same thing
    2. O(α(n)) ≈ O(1) amortized time for find and union
    3. Multiple phrases → same canonical handler
    
    EXAMPLE:
    "cancel order" ∪ "stop order" ∪ "abort purchase" → CANCEL_INTENT
    
    OPERATIONS:
    - find(x): O(α(n)) amortized - find canonical representative
    - union(x, y): O(α(n)) amortized - merge equivalence classes
    """
    
    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}
    
    def _make_set(self, x: str) -> None:
        """Create a new set with single element."""
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
    
    def find(self, x: str) -> str:
        """
        Find the canonical representative for x.
        
        Uses PATH COMPRESSION for O(α(n)) amortized time.
        """
        self._make_set(x)
        
        if self.parent[x] != x:
            # Path compression: point directly to root
            self.parent[x] = self.find(self.parent[x])
        
        return self.parent[x]
    
    def union(self, x: str, y: str) -> str:
        """
        Merge the sets containing x and y.
        
        Uses UNION BY RANK for balanced trees.
        Returns the new canonical representative.
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return root_x
        
        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
            return root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
            return root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
            return root_x
    
    def are_equivalent(self, x: str, y: str) -> bool:
        """Check if x and y are in the same equivalence class."""
        return self.find(x) == self.find(y)
    
    def get_canonical(self, intent: str) -> str:
        """Get the canonical form of an intent."""
        return self.find(intent)


# =============================================================================
# DATA STRUCTURE 6: WEIGHTED GRAPH - Next Best Action Suggestions
# =============================================================================

class WeightedGraph:
    """
    Weighted Graph for "Next Best Action" suggestions.
    
    DATA STRUCTURE: Adjacency List with weights
    
    WHY WEIGHTED GRAPH FOR SUGGESTIONS:
    1. Nodes = conversation states or actions
    2. Edges = transitions with probability/relevance weights
    3. Suggests most likely next actions based on current state
    
    EXAMPLE:
    After ORDER_STATUS:
      - TRACK_ORDER (weight 0.6) - most likely
      - CANCEL_ORDER (weight 0.3)
      - CONTACT_SUPPORT (weight 0.1)
    
    OPERATIONS:
    - add_node(): O(1)
    - add_edge(): O(1)
    - get_suggestions(): O(k log k) where k = number of edges from node
    """
    
    def __init__(self):
        # Adjacency list: node → [(neighbor, weight, label)]
        self.graph: Dict[str, List[Tuple[str, float, str]]] = {}
        self.node_labels: Dict[str, str] = {}
    
    def add_node(self, node_id: str, label: str = "") -> None:
        """Add a node to the graph."""
        if node_id not in self.graph:
            self.graph[node_id] = []
        self.node_labels[node_id] = label or node_id
    
    def add_edge(self, from_node: str, to_node: str, 
                 weight: float = 1.0, label: str = "") -> None:
        """
        Add weighted directed edge.
        
        Args:
            from_node: Source node
            to_node: Target node
            weight: Edge weight (higher = more likely suggestion)
            label: Human-readable label for the action
        """
        if from_node not in self.graph:
            self.add_node(from_node)
        if to_node not in self.graph:
            self.add_node(to_node)
        
        self.graph[from_node].append((to_node, weight, label or to_node))
    
    def get_suggestions(self, current_node: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Get top-k next action suggestions based on weights.
        
        TIME COMPLEXITY: O(k log k) for sorting top suggestions
        
        Returns:
            List of suggested actions sorted by weight (descending)
        """
        if current_node not in self.graph:
            return []
        
        edges = self.graph[current_node]
        if not edges:
            return []
        
        # Sort by weight descending
        sorted_edges = sorted(edges, key=lambda x: x[1], reverse=True)
        
        suggestions = []
        for node_id, weight, label in sorted_edges[:top_k]:
            suggestions.append({
                "action": node_id,
                "label": label,
                "weight": weight,
                "confidence": f"{weight * 100:.0f}%"
            })
        
        return suggestions
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighbors of a node."""
        if node_id not in self.graph:
            return []
        return [edge[0] for edge in self.graph[node_id]]


# =============================================================================
# DATA STRUCTURE 7: ORDER DATABASE (HashMap) - Order Lookup
# =============================================================================

class OrderDatabase:
    """
    HashMap-based Order Database for order lookup simulation.
    
    DATA STRUCTURE: HashMap (Python dict)
    
    WHY HASHMAP FOR ORDERS:
    1. O(1) lookup by Order ID
    2. Real-world simulation of order management
    3. Demonstrates key-value storage
    
    OPERATIONS:
    - add_order(): O(1)
    - get_order(): O(1)
    - update_status(): O(1)
    """
    
    def __init__(self):
        self._orders: Dict[str, Dict[str, Any]] = {}
        self._populate_sample_orders()
    
    def _populate_sample_orders(self) -> None:
        """Add sample orders for demo."""
        sample_orders = [
            {
                "order_id": "ORD-12345",
                "customer_name": "John Smith",
                "items": ["Wireless Headphones", "Phone Case"],
                "total": 89.99,
                "status": "Shipped",
                "tracking": "1Z999AA10123456784",
                "order_date": "2026-01-15",
                "estimated_delivery": "2026-01-20"
            },
            {
                "order_id": "ORD-67890",
                "customer_name": "Sarah Johnson",
                "items": ["Laptop Stand", "USB-C Hub", "Webcam"],
                "total": 156.50,
                "status": "Processing",
                "tracking": None,
                "order_date": "2026-01-17",
                "estimated_delivery": "2026-01-24"
            },
            {
                "order_id": "ORD-11111",
                "customer_name": "Mike Brown",
                "items": ["Gaming Mouse"],
                "total": 49.99,
                "status": "Delivered",
                "tracking": "1Z999AA10123456001",
                "order_date": "2026-01-10",
                "estimated_delivery": "2026-01-14",
                "delivered_date": "2026-01-13"
            },
            {
                "order_id": "ORD-22222",
                "customer_name": "Emily Davis",
                "items": ["Mechanical Keyboard", "Desk Mat"],
                "total": 124.00,
                "status": "Out for Delivery",
                "tracking": "1Z999AA10123456002",
                "order_date": "2026-01-16",
                "estimated_delivery": "2026-01-18"
            },
            {
                "order_id": "ORD-33333",
                "customer_name": "Alex Wilson",
                "items": ["Monitor Light Bar", "Cable Management Kit"],
                "total": 78.99,
                "status": "Cancelled",
                "tracking": None,
                "order_date": "2026-01-14",
                "cancelled_date": "2026-01-15",
                "refund_status": "Processed"
            }
        ]
        
        for order in sample_orders:
            self._orders[order["order_id"]] = order
            # Also index by lowercase
            self._orders[order["order_id"].lower()] = order
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Look up order by ID. O(1) time.
        
        Args:
            order_id: The order ID (e.g., "ORD-12345")
            
        Returns:
            Order details dict or None if not found
        """
        # Clean the order ID
        clean_id = order_id.strip().upper()
        
        # Try exact match
        if clean_id in self._orders:
            return self._orders[clean_id].copy()
        
        # Try with ORD- prefix
        if not clean_id.startswith("ORD-"):
            prefixed = f"ORD-{clean_id}"
            if prefixed in self._orders:
                return self._orders[prefixed].copy()
        
        return None
    
    def add_order(self, order: Dict[str, Any]) -> bool:
        """Add a new order. O(1) time."""
        if "order_id" not in order:
            return False
        self._orders[order["order_id"]] = order
        self._orders[order["order_id"].lower()] = order
        return True
    
    def update_status(self, order_id: str, new_status: str) -> bool:
        """Update order status. O(1) time."""
        order = self.get_order(order_id)
        if order:
            self._orders[order["order_id"]]["status"] = new_status
            return True
        return False
    
    def get_by_tracking(self, tracking_number: str) -> Optional[Dict[str, Any]]:
        """
        Look up order by tracking number. O(n) time.
        
        Args:
            tracking_number: UPS/FedEx tracking number
            
        Returns:
            Order details dict or None if not found
        """
        tracking_number = tracking_number.strip().upper()
        for order in self._orders.values():
            if order.get("tracking") and order["tracking"].upper() == tracking_number:
                return order.copy()
        return None
    
    def format_order_response(self, order: Dict[str, Any]) -> str:
        """Format order as readable response."""
        items_str = ", ".join(order["items"])
        
        response = f"""**Order Details**

**Order ID:** {order['order_id']}
**Status:** {order['status']}
**Items:** {items_str}
**Total:** ${order['total']:.2f}
**Order Date:** {order['order_date']}"""
        
        if order.get("tracking"):
            response += f"\n**Tracking:** {order['tracking']}"
        
        if order["status"] == "Delivered":
            response += f"\n**Delivered:** {order.get('delivered_date', 'N/A')}"
        elif order["status"] == "Cancelled":
            response += f"\n**Cancelled:** {order.get('cancelled_date', 'N/A')}"
            response += f"\n**Refund:** {order.get('refund_status', 'Pending')}"
        else:
            response += f"\n**Est. Delivery:** {order.get('estimated_delivery', 'N/A')}"
        
        return response
    
    def format_tracking_response(self, order: Dict[str, Any]) -> str:
        """Format order as tracking-focused response."""
        response = f"""**Tracking Information**

**Order ID:** {order['order_id']}
**Tracking Number:** {order.get('tracking', 'Not yet assigned')}
**Status:** {order['status']}

**Shipping Updates:**"""
        
        # Generate dummy tracking history based on status
        if order["status"] == "Delivered":
            response += f"""
- {order.get('delivered_date', 'N/A')} - Delivered to recipient
- {order['order_date']} - Package picked up
- {order['order_date']} - Shipping label created"""
        elif order["status"] == "Out for Delivery":
            response += f"""
- Today - Out for delivery
- Yesterday - Arrived at local facility
- {order['order_date']} - Package picked up"""
        elif order["status"] == "Shipped":
            response += f"""
- In transit to destination
- {order['order_date']} - Package picked up
- {order['order_date']} - Shipping label created"""
        elif order["status"] == "Processing":
            response += "\n- Order is being prepared for shipment"
        else:
            response += "\n- No tracking updates available"
        
        if order.get("estimated_delivery"):
            response += f"\n\n**Estimated Delivery:** {order['estimated_delivery']}"
        
        return response
    
    def get_all_order_ids(self) -> List[str]:
        """Get list of all order IDs."""
        return [k for k in self._orders.keys() if k.startswith("ORD-")]
    
    def size(self) -> int:
        """Return number of orders."""
        return len(self.get_all_order_ids())


# =============================================================================
# DATA STRUCTURE 8: USER PROFILE (HashMap + Stack)
# =============================================================================

class UserProfile:
    """
    User Profile with navigation history.
    
    DATA STRUCTURES USED:
    - HashMap (dict): Store user profile data with O(1) access
    - Stack (list): Track profile view history for navigation
    
    WHY THESE DATA STRUCTURES:
    1. HashMap for instant profile field access
    2. Stack for "back" navigation through profile sections
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        # HashMap for profile data
        self._profile: Dict[str, Any] = {
            "user_id": user_id,
            "name": "Demo User",
            "email": "demo@example.com",
            "phone": "+1-555-0123",
            "member_since": "2025-01-01",
            "membership_tier": "Gold",
            "addresses": [
                {
                    "type": "Home",
                    "street": "123 Main Street",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001"
                },
                {
                    "type": "Work",
                    "street": "456 Business Ave",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10002"
                }
            ],
            "payment_methods": [
                {"type": "Visa", "last_four": "4242", "default": True},
                {"type": "PayPal", "email": "demo@example.com", "default": False}
            ],
            "preferences": {
                "notifications": True,
                "newsletter": True,
                "language": "English"
            }
        }
        # Stack for navigation history
        self._view_history: List[str] = []
    
    def get_profile(self) -> Dict[str, Any]:
        """Get full profile. O(1)."""
        return self._profile.copy()
    
    def get_field(self, field: str) -> Any:
        """Get specific field. O(1)."""
        return self._profile.get(field)
    
    def update_field(self, field: str, value: Any) -> bool:
        """Update profile field. O(1)."""
        if field in self._profile:
            self._profile[field] = value
            return True
        return False
    
    def push_view(self, section: str) -> None:
        """Record section view in history. O(1)."""
        self._view_history.append(section)
        # Limit history size
        if len(self._view_history) > 10:
            self._view_history.pop(0)
    
    def pop_view(self) -> Optional[str]:
        """Go back to previous section. O(1)."""
        if self._view_history:
            return self._view_history.pop()
        return None
    
    def get_view_history(self) -> List[str]:
        """Get navigation history."""
        return list(self._view_history)
    
    def format_profile_summary(self) -> str:
        """Format profile as readable summary."""
        p = self._profile
        addresses_str = "\n".join([
            f"  • {addr['type']}: {addr['street']}, {addr['city']}, {addr['state']} {addr['zip']}"
            for addr in p.get("addresses", [])
        ])
        payments_str = "\n".join([
            f"  • {pm['type']} {'(Default)' if pm.get('default') else ''}"
            for pm in p.get("payment_methods", [])
        ])
        
        return f"""**Your Profile**

**Name:** {p.get('name', 'N/A')}
**Email:** {p.get('email', 'N/A')}
**Phone:** {p.get('phone', 'N/A')}
**Member Since:** {p.get('member_since', 'N/A')}
**Tier:** {p.get('membership_tier', 'Standard')}

**Saved Addresses:**
{addresses_str}

**Payment Methods:**
{payments_str}"""


# =============================================================================
# DATA STRUCTURE 9: SHOPPING CART (HashMap + Stack)
# =============================================================================

class ShoppingCart:
    """
    Shopping Cart with undo functionality.
    
    DATA STRUCTURES USED:
    - HashMap (dict): Store cart items with product_id as key - O(1) operations
    - Stack (list): Track actions for undo functionality - O(1) push/pop
    
    WHY THESE DATA STRUCTURES:
    1. HashMap for instant add/remove/update by product ID
    2. Stack for undo - last action can be reversed (LIFO)
    """
    
    def __init__(self):
        # HashMap: product_id -> {name, price, quantity}
        self._items: Dict[str, Dict[str, Any]] = {}
        # Stack: action history for undo
        self._action_history: List[Dict[str, Any]] = []
        # Sample products catalog
        self._products: Dict[str, Dict[str, Any]] = {
            "PROD-001": {"name": "Wireless Headphones", "price": 79.99},
            "PROD-002": {"name": "Phone Case", "price": 19.99},
            "PROD-003": {"name": "Laptop Stand", "price": 49.99},
            "PROD-004": {"name": "USB-C Hub", "price": 39.99},
            "PROD-005": {"name": "Webcam HD", "price": 69.99},
            "PROD-006": {"name": "Mechanical Keyboard", "price": 129.99},
            "PROD-007": {"name": "Gaming Mouse", "price": 59.99},
            "PROD-008": {"name": "Monitor Light Bar", "price": 45.99},
            "PROD-009": {"name": "Desk Mat", "price": 24.99},
            "PROD-010": {"name": "Cable Management Kit", "price": 15.99}
        }
    
    def add_item(self, product_id: str, quantity: int = 1) -> Dict[str, Any]:
        """Add item to cart. O(1)."""
        product_id = product_id.upper()
        
        if product_id not in self._products:
            return {"success": False, "error": "Product not found"}
        
        product = self._products[product_id]
        
        if product_id in self._items:
            old_qty = self._items[product_id]["quantity"]
            self._items[product_id]["quantity"] += quantity
            # Record for undo
            self._action_history.append({
                "action": "add",
                "product_id": product_id,
                "quantity": quantity,
                "was_new": False,
                "old_quantity": old_qty
            })
        else:
            self._items[product_id] = {
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity
            }
            self._action_history.append({
                "action": "add",
                "product_id": product_id,
                "quantity": quantity,
                "was_new": True
            })
        
        return {
            "success": True,
            "message": f"Added {quantity}x {product['name']} to cart",
            "item": self._items[product_id]
        }
    
    def remove_item(self, product_id: str) -> Dict[str, Any]:
        """Remove item from cart. O(1)."""
        product_id = product_id.upper()
        
        if product_id not in self._items:
            return {"success": False, "error": "Item not in cart"}
        
        removed_item = self._items.pop(product_id)
        self._action_history.append({
            "action": "remove",
            "product_id": product_id,
            "item": removed_item
        })
        
        return {
            "success": True,
            "message": f"Removed {removed_item['name']} from cart"
        }
    
    def undo(self) -> Dict[str, Any]:
        """Undo last cart action. O(1)."""
        if not self._action_history:
            return {"success": False, "error": "Nothing to undo"}
        
        last_action = self._action_history.pop()
        
        if last_action["action"] == "add":
            if last_action.get("was_new"):
                # Remove the item completely
                self._items.pop(last_action["product_id"], None)
                return {"success": True, "message": f"Undid: Removed newly added item"}
            else:
                # Restore old quantity
                self._items[last_action["product_id"]]["quantity"] = last_action["old_quantity"]
                return {"success": True, "message": f"Undid: Restored previous quantity"}
        
        elif last_action["action"] == "remove":
            # Re-add the removed item
            self._items[last_action["product_id"]] = last_action["item"]
            return {"success": True, "message": f"Undid: Restored {last_action['item']['name']}"}
        
        return {"success": False, "error": "Unknown action"}
    
    def get_cart(self) -> Dict[str, Any]:
        """Get cart contents. O(n) where n = items."""
        items = list(self._items.values())
        total = sum(item["price"] * item["quantity"] for item in items)
        
        return {
            "items": items,
            "item_count": len(items),
            "total": round(total, 2),
            "can_undo": len(self._action_history) > 0
        }
    
    def clear(self) -> None:
        """Clear cart."""
        self._items.clear()
        self._action_history.clear()
    
    def get_products(self) -> Dict[str, Dict[str, Any]]:
        """Get available products catalog."""
        return self._products.copy()
    
    def format_cart(self) -> str:
        """Format cart as readable string."""
        cart = self.get_cart()
        
        if not cart["items"]:
            return "**Your Shopping Cart**\n\nYour cart is empty.\n\nTry adding items with: 'add [product name]'"
        
        items_str = "\n".join([
            f"• {item['name']} x{item['quantity']} - ${item['price'] * item['quantity']:.2f}"
            for item in cart["items"]
        ])
        
        undo_hint = "\n\n💡 Type 'undo' to reverse your last action" if cart["can_undo"] else ""
        
        return f"""**Your Shopping Cart**

{items_str}

**Total:** ${cart['total']:.2f}
**Items:** {cart['item_count']}{undo_hint}"""


# =============================================================================
# DATA STRUCTURE 10: WISHLIST (HashMap + Trie integration)
# =============================================================================

class Wishlist:
    """
    Wishlist with product search integration.
    
    DATA STRUCTURES USED:
    - HashMap (dict): Store unique wishlist items - O(1) add/remove/check
    - Integrates with Trie: Auto-complete product names when searching
    
    WHY THESE DATA STRUCTURES:
    1. HashMap for O(1) contains check - "Is this item in my wishlist?"
    2. Trie integration for product name suggestions
    """
    
    def __init__(self):
        # HashMap: product_id -> product details
        self._items: Dict[str, Dict[str, Any]] = {}
        # Sample products (shared with cart)
        self._products: Dict[str, Dict[str, Any]] = {
            "PROD-001": {"name": "Wireless Headphones", "price": 79.99, "category": "Electronics"},
            "PROD-002": {"name": "Phone Case", "price": 19.99, "category": "Accessories"},
            "PROD-003": {"name": "Laptop Stand", "price": 49.99, "category": "Office"},
            "PROD-004": {"name": "USB-C Hub", "price": 39.99, "category": "Electronics"},
            "PROD-005": {"name": "Webcam HD", "price": 69.99, "category": "Electronics"},
            "PROD-006": {"name": "Mechanical Keyboard", "price": 129.99, "category": "Electronics"},
            "PROD-007": {"name": "Gaming Mouse", "price": 59.99, "category": "Electronics"},
            "PROD-008": {"name": "Monitor Light Bar", "price": 45.99, "category": "Office"},
            "PROD-009": {"name": "Desk Mat", "price": 24.99, "category": "Office"},
            "PROD-010": {"name": "Cable Management Kit", "price": 15.99, "category": "Office"}
        }
    
    def add(self, product_id: str) -> Dict[str, Any]:
        """Add to wishlist. O(1)."""
        product_id = product_id.upper()
        
        if product_id not in self._products:
            return {"success": False, "error": "Product not found"}
        
        if product_id in self._items:
            return {"success": False, "error": "Already in wishlist"}
        
        product = self._products[product_id]
        self._items[product_id] = {
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],
            "category": product["category"]
        }
        
        return {
            "success": True,
            "message": f"Added '{product['name']}' to wishlist"
        }
    
    def remove(self, product_id: str) -> Dict[str, Any]:
        """Remove from wishlist. O(1)."""
        product_id = product_id.upper()
        
        if product_id not in self._items:
            return {"success": False, "error": "Item not in wishlist"}
        
        removed = self._items.pop(product_id)
        return {
            "success": True,
            "message": f"Removed '{removed['name']}' from wishlist"
        }
    
    def contains(self, product_id: str) -> bool:
        """Check if in wishlist. O(1)."""
        return product_id.upper() in self._items
    
    def get_items(self) -> List[Dict[str, Any]]:
        """Get all wishlist items."""
        return list(self._items.values())
    
    def size(self) -> int:
        """Get wishlist size."""
        return len(self._items)
    
    def find_by_name(self, name: str) -> Optional[str]:
        """Find product ID by name (case-insensitive). O(n)."""
        name_lower = name.lower()
        for pid, product in self._products.items():
            if name_lower in product["name"].lower():
                return pid
        return None
    
    def get_products(self) -> Dict[str, Dict[str, Any]]:
        """Get all available products."""
        return self._products.copy()
    
    def format_wishlist(self) -> str:
        """Format wishlist as readable string."""
        items = self.get_items()
        
        if not items:
            return "**Your Wishlist**\n\n❤️ Your wishlist is empty.\n\nAdd items with: 'add to wishlist [product]'"
        
        items_str = "\n".join([
            f"• {item['name']} - ${item['price']:.2f} ({item['category']})"
            for item in items
        ])
        return f"""**Your Wishlist** ❤️

{items_str}

**Total Items:** {len(items)}

💡 Say 'move to cart [product]' to add to your cart"""


# =============================================================================
# DATA STRUCTURE 11: PRIORITY QUEUE (HEAP) - Product Recommendations
# =============================================================================

class ProductRecommendationQueue:
    """
    Priority Queue (Min-Heap) for product recommendations.
    
    DATA STRUCTURE: Binary Heap (via Python heapq)
    
    WHY PRIORITY QUEUE FOR RECOMMENDATIONS:
    1. Always get the highest relevance products in O(1)
    2. Insert new recommendations in O(log n)
    3. Maintains sorted order automatically
    
    EXAMPLE:
    Products scored by relevance → Heap keeps top items accessible
    
    OPERATIONS:
    - push(): O(log n) - Add product with relevance score
    - pop(): O(log n) - Get highest relevance product
    - peek(): O(1) - View top product without removing
    - get_top_k(): O(k log n) - Get k best recommendations
    """
    
    def __init__(self):
        # Using negative scores for max-heap behavior
        self._heap: List[Tuple[float, str, Dict[str, Any]]] = []
        self._products: Dict[str, Dict[str, Any]] = {}
    
    def push(self, product_id: str, relevance_score: float, product_data: Dict[str, Any]) -> None:
        """
        Add product with relevance score. O(log n).
        
        Args:
            product_id: Unique product identifier
            relevance_score: Higher = more relevant (0.0 to 1.0)
            product_data: Product details
        """
        # Negate score for max-heap behavior (heapq is min-heap)
        heapq.heappush(self._heap, (-relevance_score, product_id, product_data))
        self._products[product_id] = {
            "score": relevance_score,
            "data": product_data
        }
    
    def pop(self) -> Optional[Dict[str, Any]]:
        """
        Get and remove highest relevance product. O(log n).
        
        Returns:
            Product data with score, or None if empty
        """
        if not self._heap:
            return None
        
        neg_score, product_id, product_data = heapq.heappop(self._heap)
        self._products.pop(product_id, None)
        
        return {
            "product_id": product_id,
            "relevance_score": -neg_score,
            "data": product_data
        }
    
    def peek(self) -> Optional[Dict[str, Any]]:
        """View top product without removing. O(1)."""
        if not self._heap:
            return None
        
        neg_score, product_id, product_data = self._heap[0]
        return {
            "product_id": product_id,
            "relevance_score": -neg_score,
            "data": product_data
        }
    
    def get_top_k(self, k: int = 5) -> List[Dict[str, Any]]:
        """
        Get top k recommendations. O(k log n).
        
        Note: Does not remove items from queue.
        """
        # Sort and take top k
        sorted_items = sorted(self._heap, key=lambda x: x[0])[:k]
        
        return [
            {
                "product_id": item[1],
                "relevance_score": -item[0],
                "data": item[2]
            }
            for item in sorted_items
        ]
    
    def update_score(self, product_id: str, new_score: float) -> bool:
        """
        Update relevance score for a product. O(n) rebuild.
        
        In production, would use decrease-key operation.
        """
        if product_id not in self._products:
            return False
        
        # Rebuild heap (simple approach)
        old_data = self._products[product_id]["data"]
        self._heap = [(s, pid, d) for s, pid, d in self._heap if pid != product_id]
        heapq.heapify(self._heap)
        self.push(product_id, new_score, old_data)
        return True
    
    def size(self) -> int:
        """Return number of items in queue."""
        return len(self._heap)
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._heap) == 0


# =============================================================================
# DATA STRUCTURE 12: DOUBLY LINKED LIST - Recently Viewed Products
# =============================================================================

class ListNode:
    """Node for Doubly Linked List."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.prev: Optional['ListNode'] = None
        self.next: Optional['ListNode'] = None


class RecentlyViewedList:
    """
    Doubly Linked List for recently viewed products.
    
    DATA STRUCTURE: Doubly Linked List with HashMap for O(1) lookup
    
    WHY DOUBLY LINKED LIST FOR RECENTLY VIEWED:
    1. O(1) add to front (most recent)
    2. O(1) remove from back (oldest)
    3. O(1) move existing item to front
    4. Supports prev/next navigation
    
    EXAMPLE:
    User views: A → B → C → A
    List becomes: A ↔ C ↔ B (A moved to front)
    
    OPERATIONS:
    - add_to_front(): O(1) - Add/move item to front
    - remove_oldest(): O(1) - Remove from back
    - get_all(): O(n) - Get all items in order
    """
    
    def __init__(self, max_size: int = 10):
        self._head: Optional[ListNode] = None
        self._tail: Optional[ListNode] = None
        self._lookup: Dict[str, ListNode] = {}  # HashMap for O(1) access
        self._size: int = 0
        self._max_size: int = max_size
    
    def add_to_front(self, product_id: str, product_data: Dict[str, Any]) -> None:
        """
        Add product to front (most recent). O(1).
        
        If product already exists, moves it to front.
        If at capacity, removes oldest item.
        """
        # If already exists, remove it first
        if product_id in self._lookup:
            self._remove_node(self._lookup[product_id])
        
        # Create new node
        new_node = ListNode({"product_id": product_id, **product_data})
        self._lookup[product_id] = new_node
        
        # Add to front
        if not self._head:
            self._head = self._tail = new_node
        else:
            new_node.next = self._head
            self._head.prev = new_node
            self._head = new_node
        
        self._size += 1
        
        # Remove oldest if over capacity
        if self._size > self._max_size:
            self.remove_oldest()
    
    def remove_oldest(self) -> Optional[Dict[str, Any]]:
        """Remove and return oldest item (from tail). O(1)."""
        if not self._tail:
            return None
        
        removed = self._tail
        removed_data = removed.data
        product_id = removed_data.get("product_id")
        
        self._remove_node(removed)
        self._lookup.pop(product_id, None)
        
        return removed_data
    
    def _remove_node(self, node: ListNode) -> None:
        """Internal: Remove a node from the list. O(1)."""
        if node.prev:
            node.prev.next = node.next
        else:
            self._head = node.next
        
        if node.next:
            node.next.prev = node.prev
        else:
            self._tail = node.prev
        
        self._size -= 1
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all items from most to least recent. O(n)."""
        items = []
        current = self._head
        while current:
            items.append(current.data)
            current = current.next
        return items
    
    def get_item(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get item by product ID. O(1)."""
        node = self._lookup.get(product_id)
        return node.data if node else None
    
    def contains(self, product_id: str) -> bool:
        """Check if product is in list. O(1)."""
        return product_id in self._lookup
    
    def size(self) -> int:
        """Return number of items."""
        return self._size
    
    def clear(self) -> None:
        """Clear all items."""
        self._head = None
        self._tail = None
        self._lookup.clear()
        self._size = 0


# =============================================================================
# DATA STRUCTURE 13: QUEUE (FIFO) - Checkout Process
# =============================================================================

class CheckoutQueue:
    """
    FIFO Queue for checkout process simulation.
    
    DATA STRUCTURE: Queue (via collections.deque)
    
    WHY QUEUE FOR CHECKOUT:
    1. Steps must be completed in order (FIFO)
    2. O(1) enqueue and dequeue operations
    3. Models real checkout flow: Cart → Shipping → Payment → Confirm
    
    EXAMPLE:
    enqueue("cart_review") → enqueue("shipping") → enqueue("payment") → ...
    dequeue() returns each step in order
    
    OPERATIONS:
    - enqueue(): O(1) - Add step to queue
    - dequeue(): O(1) - Get next step
    - peek(): O(1) - View next step without removing
    """
    
    # Standard checkout steps
    CHECKOUT_STEPS = [
        {"step": 1, "name": "cart_review", "label": "Cart Review"},
        {"step": 2, "name": "shipping", "label": "Shipping Address"},
        {"step": 3, "name": "payment", "label": "Payment Method"},
        {"step": 4, "name": "confirmation", "label": "Order Confirmation"}
    ]
    
    def __init__(self):
        self._queue: deque = deque()
        self._current_step: int = 0
        self._completed_steps: List[Dict[str, Any]] = []
        self._order_data: Dict[str, Any] = {}
    
    def start_checkout(self, cart_items: List[Dict[str, Any]], 
                       total: float) -> Dict[str, Any]:
        """
        Initialize checkout with cart data. O(k) where k = steps.
        
        Args:
            cart_items: List of items in cart
            total: Cart total
            
        Returns:
            First step data
        """
        self._queue.clear()
        self._completed_steps.clear()
        self._current_step = 0
        self._order_data = {
            "items": cart_items,
            "total": total,
            "started_at": None,  # Would be timestamp
            "status": "in_progress"
        }
        
        # Enqueue all steps
        for step in self.CHECKOUT_STEPS:
            self._queue.append(step.copy())
        
        return self.get_current_step()
    
    def get_current_step(self) -> Optional[Dict[str, Any]]:
        """View current step without advancing. O(1)."""
        if not self._queue:
            return None
        return self._queue[0]
    
    def complete_current_step(self, step_data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Complete current step and move to next. O(1).
        
        Args:
            step_data: Any data collected in this step
            
        Returns:
            Next step data, or completion confirmation
        """
        if not self._queue:
            return None
        
        # Dequeue current step
        completed = self._queue.popleft()
        completed["completed"] = True
        completed["data"] = step_data or {}
        self._completed_steps.append(completed)
        self._current_step += 1
        
        # Check if checkout complete
        if not self._queue:
            self._order_data["status"] = "completed"
            return {
                "complete": True,
                "order_data": self._order_data,
                "steps_completed": len(self._completed_steps)
            }
        
        return self.get_current_step()
    
    def go_back(self) -> Optional[Dict[str, Any]]:
        """
        Go back to previous step. O(1).
        
        Re-enqueues the last completed step at the front.
        """
        if not self._completed_steps:
            return None
        
        # Pop last completed step
        last_step = self._completed_steps.pop()
        last_step.pop("completed", None)
        last_step.pop("data", None)
        
        # Add back to front of queue
        self._queue.appendleft(last_step)
        self._current_step -= 1
        
        return self.get_current_step()
    
    def get_progress(self) -> Dict[str, Any]:
        """Get checkout progress. O(1)."""
        total_steps = len(self.CHECKOUT_STEPS)
        completed = len(self._completed_steps)
        
        return {
            "current_step": self._current_step + 1,
            "total_steps": total_steps,
            "completed": completed,
            "remaining": total_steps - completed,
            "percentage": round((completed / total_steps) * 100) if total_steps > 0 else 0
        }
    
    def cancel_checkout(self) -> Dict[str, Any]:
        """Cancel checkout and clear queue."""
        self._queue.clear()
        self._order_data["status"] = "cancelled"
        
        return {
            "cancelled": True,
            "steps_completed": len(self._completed_steps)
        }
    
    def size(self) -> int:
        """Return number of remaining steps."""
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """Check if checkout is complete (no more steps)."""
        return len(self._queue) == 0
