"""
Support Engine - Main Orchestrator for the Customer Support System

This module is the central coordinator that:
1. Receives user input
2. Gets Trie suggestions for auto-complete
3. Checks FAQ HashMap for instant responses
4. Falls back to Queue/Priority Queue for processing
5. Uses Conversation Tree for multi-step dialogues
6. Maintains Recent Interaction Cache

Author: Smart Customer Support System
"""

from typing import Dict, Any, List, Optional
from backend.data_structures import (
    Trie,
    QueryQueue,
    PriorityQueue,
    FAQHashMap,
    ConversationTree,
    RecentInteractionCache
)


class SupportEngine:
    """
    Main orchestrator for the customer support system.
    
    This engine coordinates all data structures and provides a unified
    interface for processing customer queries.
    
    Components:
        - Trie: For real-time keyword suggestions
        - QueryQueue: For FIFO query management
        - PriorityQueue: For urgent query handling
        - FAQHashMap: For instant FAQ responses
        - ConversationTree: For multi-step conversations
        - RecentInteractionCache: For context retention
    """
    
    def __init__(self, cache_size: int = 5):
        """
        Initialize the support engine with all components.
        
        Args:
            cache_size: Maximum number of recent interactions to cache
        """
        # Initialize all data structures
        self._trie = Trie()
        self._query_queue = QueryQueue()
        self._priority_queue = PriorityQueue()
        self._faq_map = FAQHashMap()
        self._conversation_tree = ConversationTree()
        self._interaction_cache = RecentInteractionCache(max_size=cache_size)
        
        # Populate Trie with FAQ keywords and common words
        self._populate_trie()
        
        # Track session data
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def _populate_trie(self) -> None:
        """Populate the Trie with keywords for auto-suggestions."""
        # Add all FAQ keywords
        for keyword in self._faq_map.get_all_keywords():
            self._trie.insert(keyword)
        
        # Add common support-related words
        common_words = [
            # Order related
            "order", "orders", "order status", "order tracking",
            "cancel", "cancellation", "cancelled",
            
            # Shipping
            "shipping", "ship", "shipment", "delivery", "delivered",
            "tracking", "track", "transit",
            
            # Returns & Refunds
            "return", "returns", "refund", "refunds", "money back",
            "exchange", "replacement",
            
            # Account
            "account", "login", "password", "email", "profile",
            "settings", "preferences", "notifications",
            
            # Payment
            "payment", "pay", "credit card", "debit card", "paypal",
            "invoice", "receipt", "billing", "charge",
            
            # Support
            "help", "support", "assistance", "problem", "issue",
            "urgent", "emergency", "complaint",
            
            # General
            "hello", "hi", "thanks", "thank you", "bye", "goodbye"
        ]
        
        for word in common_words:
            self._trie.insert(word)
    
    def get_suggestions(self, prefix: str) -> Dict[str, Any]:
        """
        Get auto-suggestions for the given prefix using the Trie.
        
        DATA STRUCTURE USED: Trie (Prefix Tree)
        TIME COMPLEXITY: O(m + k) where m = prefix length, k = matches
        
        Args:
            prefix: The prefix to get suggestions for
            
        Returns:
            Dictionary with suggestions and metadata
        """
        suggestions = self._trie.get_suggestions(prefix, max_suggestions=8)
        
        return {
            "suggestions": suggestions,
            "prefix": prefix,
            "count": len(suggestions),
            "module": "Auto-Suggestion Module",
            "data_structure": "Trie (Prefix Tree)",
            "complexity": "O(m + k) where m = prefix length"
        }
    
    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        FLOW:
        1. Check for urgent keywords → Priority Queue
        2. Check FAQ HashMap for instant match
        3. If no FAQ match → Regular Queue + Conversation Tree
        4. Update Recent Interaction Cache
        
        Args:
            user_id: Unique identifier for the user session
            message: The user's message text
            
        Returns:
            Dictionary with response and all metadata
        """
        message = message.strip()
        if not message:
            return self._create_response(
                response="Please enter a message.",
                module="Input Validation",
                data_structure="None",
                success=False
            )
        
        # Initialize session if new
        if user_id not in self._sessions:
            self._sessions[user_id] = {"in_tree_flow": False}
        
        # Step 1: Check if message is urgent → Priority Queue
        priority_result = self._check_priority(message)
        is_urgent = priority_result["is_urgent"]
        
        # Step 2: Check FAQ HashMap for instant response
        faq_result = self._faq_map.lookup(message)
        
        if faq_result and not self._sessions[user_id].get("in_tree_flow"):
            # FAQ match found - instant response!
            response = self._create_response(
                response=faq_result["response"],
                module="FAQ Response Module",
                data_structure="HashMap (Dictionary)",
                faq_category=faq_result["category"],
                matched_keyword=faq_result["matched_keyword"]
            )
            
            # Add to interaction cache
            self._interaction_cache.add_interaction(
                user_message=message,
                bot_response=faq_result["response"],
                module_used="FAQ Response Module",
                data_structure="HashMap"
            )
            
            return response
        
        # Step 3: Check Conversation Tree for contextual response
        tree_result = self._conversation_tree.get_response(user_id, message)
        
        # Mark session as in tree flow
        self._sessions[user_id]["in_tree_flow"] = True
        
        # If tree gives goodbye, reset the flow
        if tree_result["node_id"] == "goodbye":
            self._sessions[user_id]["in_tree_flow"] = False
        
        # Step 4: Queue the message (Priority or Regular)
        if is_urgent:
            # Add to priority queue
            queue_result = self._priority_queue.enqueue(message, user_id)
            queue_module = "Priority Handling Module"
            queue_ds = "Priority Queue (heapq)"
            extra_info = {
                "priority": queue_result["priority"],
                "priority_label": queue_result["priority_label"]
            }
        else:
            # Add to regular queue
            queue_result = self._query_queue.enqueue(message, user_id)
            queue_module = "Query Management Module"
            queue_ds = "Queue (deque)"
            extra_info = {"queue_position": queue_result["position"]}
        
        # Build response with tree navigation
        response = self._create_response(
            response=tree_result["response"],
            module="Conversation Flow Module",
            data_structure="Tree",
            node_id=tree_result["node_id"],
            available_options=tree_result["available_options"],
            secondary_module=queue_module,
            secondary_ds=queue_ds,
            **extra_info
        )
        
        # Add to interaction cache
        self._interaction_cache.add_interaction(
            user_message=message,
            bot_response=tree_result["response"],
            module_used="Conversation Flow Module",
            data_structure="Tree"
        )
        
        return response
    
    def _check_priority(self, message: str) -> Dict[str, Any]:
        """Check if a message should be treated as urgent."""
        message_lower = message.lower()
        urgent_keywords = ["urgent", "emergency", "critical", "asap", 
                         "immediately", "help", "problem", "error",
                         "failed", "locked", "hacked", "stolen"]
        
        is_urgent = any(kw in message_lower for kw in urgent_keywords)
        
        return {
            "is_urgent": is_urgent,
            "module": "Priority Detection",
            "data_structure": "Priority Queue (heapq)" if is_urgent else "Queue (deque)"
        }
    
    def _create_response(self, response: str, module: str, 
                        data_structure: str, **kwargs) -> Dict[str, Any]:
        """Create a standardized response dictionary."""
        result = {
            "response": response,
            "module": module,
            "data_structure": data_structure,
            "success": kwargs.get("success", True)
        }
        
        # Add any extra fields
        for key, value in kwargs.items():
            if key != "success":
                result[key] = value
        
        return result
    
    def get_recent_context(self) -> Dict[str, Any]:
        """
        Get recent interaction context.
        
        DATA STRUCTURE USED: Deque (bounded)
        
        Returns:
            Dictionary with recent interactions and metadata
        """
        interactions = self._interaction_cache.get_recent_context()
        
        return {
            "interactions": interactions,
            "count": len(interactions),
            "max_size": self._interaction_cache.max_size(),
            "module": "Recent Interaction Cache Module",
            "data_structure": "Deque (collections.deque with maxlen)"
        }
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current status of both queues."""
        return {
            "regular_queue": {
                "size": self._query_queue.size(),
                "data_structure": "Queue (deque)"
            },
            "priority_queue": {
                "size": self._priority_queue.size(),
                "has_urgent": self._priority_queue.has_urgent_queries(),
                "data_structure": "Priority Queue (heapq)"
            }
        }
    
    def reset_conversation(self, user_id: str) -> Dict[str, Any]:
        """Reset the conversation for a user."""
        self._conversation_tree.reset_conversation(user_id)
        if user_id in self._sessions:
            self._sessions[user_id]["in_tree_flow"] = False
        
        return {
            "success": True,
            "message": "Conversation reset to beginning.",
            "module": "Conversation Flow Module",
            "data_structure": "Tree"
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            "trie_words": self._trie.get_word_count(),
            "faq_entries": self._faq_map.size(),
            "regular_queue_size": self._query_queue.size(),
            "priority_queue_size": self._priority_queue.size(),
            "cached_interactions": self._interaction_cache.size(),
            "active_sessions": len(self._sessions)
        }


# Create a global engine instance for the server
_engine_instance = None


def get_engine() -> SupportEngine:
    """Get or create the global engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SupportEngine()
    return _engine_instance
