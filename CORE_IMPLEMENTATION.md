# Core Logic Implementation - ShopDS Data Structures

This document outlines the core implementation logic for the data structures used in the Customer Support System.

## 1. Trie (Prefix Tree) - Auto-Complete
*Used for real-time search suggestions.*

```python
# In SupportEngine.get_suggestions():
def get_suggestions(self, prefix: str) -> Dict[str, Any]:
    # Use Trie to get suggestions O(prefix_length + matches)
    suggestions = self._trie.get_suggestions(prefix, max_suggestions=8)
    return {
        "suggestions": suggestions,
        "count": len(suggestions)
    }
```

## 2. HashMap - FAQ Lookup
*Used for O(1) retrieval of frequently asked questions.*

```python
# In SupportEngine.process_message():
# O(1) Lookup in FAQ HashMap
faq_result = self._faq_map.lookup(normalized_message)

if faq_result:
    return self._create_response(
        faq_result["response"],
        "FAQ Lookup",
        "HashMap"
    )
```

## 3. Decision Tree - Conversation Flow
*Used for managing branching conversation paths.*

```python
# In SupportEngine.process_message():
# Navigate Decision Tree based on user input
tree_result = self._decision_tree.get_response(user_id, normalized_message)

# Result contains new state node_id and response message
next_node = tree_result["node_id"]
response = tree_result["response"]
```

## 4. Stack - Navigation History
*Used for "Go Back" functionality (LIFO).*

```python
# In SupportEngine.process_message():
if message.lower() == "back":
    # Pop current state to go back
    if stack.size() > 1:
        stack.pop() 
        prev_state = stack.peek()
        # Restore previous state in Decision Tree
        self._decision_tree.set_state(user_id, prev_state["node_id"])
```

## 5. Union-Find - Synonym Grouping
*Used for standardizing user intent.*

```python
def normalize_intent(self, user_input: str) -> Dict[str, Any]:
    # Use Union-Find to get canonical intent
    # e.g., "stop order" -> "cancel"
    canonical = self._intent_groups.find(user_input.lower())
    
    return {
        "original": user_input,
        "canonical": canonical
    }
```

## 6. Weighted Graph - Next Best Actions
*Used for suggesting actions based on probabilities.*

```python
def get_next_actions(self, current_state: str) -> Dict[str, Any]:
    # Get top 3 suggested actions based on edge weights
    # Users are 50% likely to click "Track" from Orders Menu
    suggestions = self._action_graph.get_suggestions(current_state, top_k=3)
    
    return {"suggestions": suggestions}
```

## 7. Linked List - Recently Viewed Items
*Used to maintain browsing history.*

```python
# In SupportEngine.process_message():
if message in ["show profile", "view profile"]:
    # Add "profile_summary" to history stack
    # Moves to front if already exists (Linked List behavior)
    profile.push_view("profile_summary")
```

## 8. Priority Queue (Heap) - Recommendations
*Used to rank products by relevance.*

```python
def record_product_click(self, product_id: str):
    # Update score in Priority Queue
    # Higher score = higher priority in recommendations
    current_score = self.get_score(product_id)
    new_score = min(0.99, current_score + 0.05)
    
    self._recommendation_queue.update_score(product_id, new_score)
```

## 9. Queue - Checkout Process
*Used for sequential ordering steps (FIFO).*

```python
# In Checkout Process:
def advance_step(self):
    # Dequeue the current step (FIFO)
    current_step = self._checkout_queue.dequeue()
    
    # Process step...
    
    # Peek at next step
    next_step = self._checkout_queue.peek()
```
