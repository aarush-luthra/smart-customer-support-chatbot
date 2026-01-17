"""
Data Structures Module for E-Commerce Customer Support Chatbot

This module contains 6 core data structure implementations:
1. Trie - Auto-complete suggestions
2. HashMap (FAQHashMap) - O(1) FAQ lookups  
3. DecisionTree - Conversation flow with branching
4. Stack - "Go back" navigation
5. UnionFind - Synonym intent grouping
6. WeightedGraph - Next best action suggestions

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
