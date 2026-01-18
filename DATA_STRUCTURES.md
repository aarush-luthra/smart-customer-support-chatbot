# Data Structures Documentation
## Customer Support Chatbot - Complete Technical Reference

This document provides an extensive explanation of the 6 data structures used in the Customer Support Chatbot, including their justification, visual representations, implementation details, time complexity analysis, and edge cases.

---

## Table of Contents

1. [Trie (Prefix Tree)](#1-trie-prefix-tree)
2. [HashMap](#2-hashmap)
3. [Decision Tree](#3-decision-tree)
4. [Stack](#4-stack)
5. [Union-Find (Disjoint Set)](#5-union-find-disjoint-set)
6. [Weighted Graph](#6-weighted-graph)

---

## 1. Trie (Prefix Tree)

### Definition

A Trie (pronounced "try") is a tree-like data structure used for efficient retrieval of keys in a dataset of strings. Each node represents a single character, and paths from the root to leaf nodes represent complete words.

### Justification for Use

**Why Trie for Auto-Complete?**

Traditional approaches to auto-complete have significant drawbacks:

| Approach | Time Complexity | Problem |
|----------|-----------------|---------|
| Linear Search | O(n × m) | Scans all n words, compares m characters each |
| Binary Search | O(log n × m) | Requires sorted list, can't find partial matches |
| Hash Table | O(m) per lookup | Can't find words by prefix |
| **Trie** | O(p + k) | Perfect for prefix matching! |

Where:
- n = number of words in dictionary
- m = average word length
- p = prefix length
- k = number of matches

**Real-World Scenario:**
When a user types "ord", the Trie instantly finds all words starting with "ord" (order, orders, order status, order tracking) without scanning unrelated words.

### Visual Representation

```
                    (root)
                   /  |  \
                  o   c   r
                  |   |   |
                  r   a   e
                  |   |   |
                  d   n   t
                 /|   |   |
                e s   c   u
                | |   |   |
                r t   e   r
                    / |   |
                   a  l   n
                   |
                   t
                   |
                   u
                   s

Words stored: order, orders, order status, cancel, cancellation, return
```

### Implementation Details

```python
class TrieNode:
    def __init__(self):
        self.children = {}      # Maps character -> TrieNode
        self.is_end_of_word = False
        self.word = None        # Stores complete word at leaf

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str) -> None:
        """Insert a word into the Trie. O(m) time."""
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.word = word
    
    def get_suggestions(self, prefix: str, max_suggestions: int = 8) -> List[str]:
        """Find all words starting with prefix. O(p + k) time."""
        # Navigate to prefix node
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []  # Prefix not found
            node = node.children[char]
        
        # Collect all words below this node (DFS)
        suggestions = []
        self._collect_words(node, suggestions, max_suggestions)
        return suggestions
```

### Time Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| Insert | O(m) | O(m) per word |
| Search | O(m) | O(1) |
| Get Suggestions | O(p + k) | O(k) for results |
| Delete | O(m) | O(1) |

Where m = word length, p = prefix length, k = number of matches

### Edge Cases Handled

| Edge Case | How It's Handled |
|-----------|------------------|
| **Empty prefix** | Returns empty list (min 2 chars required in UI) |
| **Prefix not found** | Returns empty list immediately |
| **Case sensitivity** | All inputs converted to lowercase |
| **Spaces in phrases** | Treated as valid characters ("order status") |
| **Single character** | UI requires 2+ chars before querying |
| **Very long prefix** | Returns empty if no match found |
| **Special characters** | Passed through, may not match if not in dictionary |
| **Max results limit** | Limited to 8 suggestions to prevent UI overflow |

### Memory Optimization

The Trie could be optimized using:
1. **Compressed Trie (Radix Tree)**: Merge single-child nodes
2. **Ternary Search Trie**: Three children instead of 26+
3. **Array-based children**: Use array[26] instead of dict for ASCII

---

## 2. HashMap

### Definition

A HashMap (also called Hash Table or Dictionary) is a data structure that implements an associative array, mapping keys to values using a hash function. It provides O(1) average-case lookup, insertion, and deletion.

### Justification for Use

**Why HashMap for FAQ Lookup?**

Customer support receives many repeated questions. A HashMap allows instant lookup:

```
User asks: "What are your shipping costs?"
                    ↓
HashMap.lookup("shipping") → O(1) average time
                    ↓
"Standard: 5-7 days (free over $50)
 Express: 2-3 days ($9.99)
 Overnight: Next day ($19.99)"
```

**Comparison with Alternatives:**

| Approach | Lookup Time | Memory | Use Case |
|----------|-------------|--------|----------|
| Linear Search | O(n) | O(n) | Small datasets |
| Binary Search | O(log n) | O(n) | Sorted, exact match |
| **HashMap** | O(1) avg | O(n) | Key-based lookup |
| Database Query | O(log n) + I/O | External | Large datasets |

### Visual Representation

```
Hash Function: hash(key) % bucket_count

Keywords: ["pricing", "shipping", "return", "hours", "payment"]

Bucket Array:
┌─────────────────────────────────────────────────────────────┐
│ Index │ Key        │ Value (Response)                       │
├───────┼────────────┼────────────────────────────────────────┤
│   0   │            │ (empty)                                │
│   1   │ "pricing"  │ "Our pricing varies by product..."    │
│   2   │ "shipping" │ "Standard: 5-7 days..."               │
│   3   │            │ (empty)                                │
│   4   │ "return"   │ "30-day return policy..."             │
│   5   │ "hours"    │ "Mon-Fri: 9 AM - 9 PM..."             │
│   6   │            │ (empty)                                │
│   7   │ "payment"  │ "Visa, MasterCard, PayPal..."         │
└─────────────────────────────────────────────────────────────┘

Collision Handling (Chaining):
┌───────┐
│   2   │ → "shipping" → "delivery" → "how long" (synonyms)
└───────┘
```

### Implementation Details

```python
class FAQHashMap:
    def __init__(self):
        self._faq_map: Dict[str, Dict[str, Any]] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def add_faq(self, keywords: List[str], response: str, category: str) -> None:
        """Add FAQ entry with multiple keyword triggers. O(k) for k keywords."""
        for keyword in keywords:
            key = keyword.lower().strip()
            self._faq_map[key] = {
                "response": response,
                "category": category,
                "matched_keyword": key
            }
            # Track by category
            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append(key)
    
    def lookup(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Look up FAQ response. O(1) average, O(w) for word-by-word check.
        """
        query_lower = query.lower().strip()
        
        # Direct match - O(1)
        if query_lower in self._faq_map:
            return self._faq_map[query_lower]
        
        # Word-by-word match - O(w) where w = word count
        for word in query_lower.split():
            if word in self._faq_map:
                return self._faq_map[word]
        
        return None
```

### Time Complexity Analysis

| Operation | Average | Worst Case | Notes |
|-----------|---------|------------|-------|
| Add FAQ | O(k) | O(k) | k = number of keywords |
| Lookup (exact) | O(1) | O(n) | Worst: all keys collide |
| Lookup (by word) | O(w) | O(w × n) | w = words in query |
| Get Category | O(1) | O(n) | Direct bucket access |

### Edge Cases Handled

| Edge Case | How It's Handled |
|-----------|------------------|
| **Key not found** | Returns None, falls through to Decision Tree |
| **Case variations** | All keys normalized to lowercase |
| **Multiple keywords match** | First matching word wins |
| **Empty query** | Returns None |
| **Partial word match** | Not matched ("ship" ≠ "shipping") |
| **Multi-word phrases** | Stored as single key ("order status") |
| **Collision handling** | Python dict handles internally |
| **Unicode characters** | Supported via Python's UTF-8 strings |

### Hash Collision Strategy

Python's dict uses:
1. **Open Addressing**: Probes next slot on collision
2. **Perturbation**: Uses multiple bits of hash
3. **Load Factor**: Resizes at ~66% capacity

---

## 3. Decision Tree

### Definition

A Decision Tree is a hierarchical data structure where each internal node represents a decision point, each branch represents a choice, and each leaf node represents an outcome. In this chatbot, it models the conversation flow.

### Justification for Use

**Why Decision Tree for Conversation Flow?**

Conversations naturally follow a tree-like structure:

```
User: "I have an order question"     → Orders Menu
User: "I want to track it"           → Track Order
User: "Actually, I want to cancel"   → Cancel Order (sibling node)
```

**Benefits over Alternatives:**

| Approach | Problem |
|----------|---------|
| Flat if/else | Unmaintainable, deeply nested |
| State Machine | Complex for branching paths |
| Rule Engine | Overkill, hard to visualize |
| **Decision Tree** | Natural fit, easy to extend |

### Visual Representation

```
                              ┌─────────────┐
                              │    ROOT     │
                              │  (Welcome)  │
                              └──────┬──────┘
           ┌──────────┬──────────┬───┴───┬──────────┬──────────┐
           ▼          ▼          ▼       ▼          ▼          ▼
      ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
      │ Orders │ │Returns │ │Account │ │Products│ │Contact │
      └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
          │          │          │          │          │
    ┌─────┼─────┐    │    ┌─────┼─────┐    │    ┌─────┼─────┐
    ▼     ▼     ▼    │    ▼     ▼     ▼    │    ▼     ▼     ▼
 ┌─────┐┌─────┐┌─────┐   ┌─────┐┌─────┐┌─────┐ ┌─────┐┌─────┐┌─────┐
 │Track││Cancel│Modify│   │Pass-││Pro- ││Order││ Phone││Email││Chat │
 │     ││     ││     │   │word ││file ││Hist.││      ││     ││     │
 └─────┘└─────┘└─────┘   └─────┘└─────┘└─────┘ └─────┘└─────┘└─────┘
    ▲                                              │
    │                                              │
    └──────────────── "back" command ──────────────┘
```

### Implementation Details

```python
@dataclass
class DecisionNode:
    node_id: str
    message: str
    options: Dict[str, str]    # keyword -> next_node_id
    is_leaf: bool = False

class DecisionTree:
    def __init__(self):
        self.nodes: Dict[str, DecisionNode] = {}
        self.root_id = "root"
        self.user_states: Dict[str, str] = {}    # user_id -> current_node_id
    
    def add_node(self, node_id: str, message: str, 
                 options: Dict[str, str] = None, is_leaf: bool = False):
        """Add a node to the tree. O(1)."""
        self.nodes[node_id] = DecisionNode(
            node_id=node_id,
            message=message,
            options=options or {},
            is_leaf=is_leaf
        )
    
    def get_response(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """
        Navigate tree based on user input.
        O(k) where k = number of options in current node.
        """
        # Get current state or start at root
        current_id = self.user_states.get(user_id, self.root_id)
        current_node = self.nodes.get(current_id)
        
        # Find matching option
        user_lower = user_input.lower().strip()
        next_node_id = None
        
        for keyword, target_id in current_node.options.items():
            if keyword in user_lower or user_lower in keyword:
                next_node_id = target_id
                break
        
        if next_node_id and next_node_id in self.nodes:
            self.user_states[user_id] = next_node_id
            next_node = self.nodes[next_node_id]
            return {
                "response": next_node.message,
                "node_id": next_node_id,
                "is_leaf": next_node.is_leaf
            }
        
        # No match - stay at current node
        return {
            "response": f"I didn't understand. {current_node.message}",
            "node_id": current_id,
            "no_match": True
        }
```

### Time Complexity Analysis

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| Add Node | O(1) | Dict insertion |
| Get Current State | O(1) | Dict lookup by user_id |
| Find Matching Option | O(k) | k = options in current node |
| Navigate to Node | O(1) | Dict lookup by node_id |
| Reset | O(1) | Update user state |

### Edge Cases Handled

| Edge Case | How It's Handled |
|-----------|------------------|
| **New user (no state)** | Starts at root node |
| **Unknown option** | Stays at current node, re-displays options |
| **Invalid node reference** | Falls back to root |
| **User at leaf node** | Can still use "back" or "menu" |
| **Multiple keyword match** | First matching option wins |
| **Empty user input** | Treated as no match |
| **Concurrent users** | Each user has separate state (user_id key) |
| **Orphan nodes** | Never reached, but don't crash system |

### Tree Traversal Patterns

```
Depth-First (User Path):     Breadth-First (Not Used):
ROOT → Orders → Track         ROOT → Orders, Returns, Account, Products, Contact
      ↑                            → Track, Cancel, Modify, Start, Status, ...
      └── back ──┘
```

---

## 4. Stack

### Definition

A Stack is a linear data structure that follows the Last-In-First-Out (LIFO) principle. Elements are added (pushed) and removed (popped) from the same end, called the "top" of the stack.

### Justification for Use

**Why Stack for Navigation History?**

Users need to backtrack through their conversation:

```
User journey: root → orders → track → (wants to go back)
                                        ↓
Stack: [root, orders, track]  →  pop()  →  [root, orders]
                                        ↓
                              Returns to "Orders Menu"
```

**The Stack perfectly models this because:**
1. Most recent state is at the top
2. "Back" = pop the top
3. "Home" = clear stack, push root
4. Prevents infinite backtracking

**Comparison:**

| Approach | Problem |
|----------|---------|
| Single "previous" variable | Only remembers 1 level |
| Array with index | Manual index management |
| Linked List | Overkill, harder to limit |
| **Stack** | Natural fit for LIFO navigation |

### Visual Representation

```
User types: "orders" → "track" → "cancel" → "back" → "back"

Step 1: Push "root"        Step 2: Push "orders"    Step 3: Push "track"
┌─────────────┐           ┌─────────────┐          ┌─────────────┐
│             │           │             │          │   track     │ ← TOP
│             │           │   orders    │ ← TOP    ├─────────────┤
│             │           ├─────────────┤          │   orders    │
│    root     │ ← TOP     │    root     │          ├─────────────┤
└─────────────┘           └─────────────┘          │    root     │
                                                   └─────────────┘

Step 4: Pop (back)         Step 5: Pop (back)
┌─────────────┐           ┌─────────────┐
│   orders    │ ← TOP     │    root     │ ← TOP
├─────────────┤           └─────────────┘
│    root     │           
└─────────────┘           User is at main menu
```

### Implementation Details

```python
class ConversationStack:
    def __init__(self, max_size: int = 10):
        self._stack: List[Dict[str, Any]] = []
        self._max_size = max_size
    
    def push(self, node_id: str, message: str = "") -> None:
        """
        Push state onto stack. O(1).
        Evicts oldest if at max capacity.
        """
        state = {
            "node_id": node_id,
            "message": message[:50],  # Truncate for memory
            "timestamp": time.time()
        }
        
        if len(self._stack) >= self._max_size:
            self._stack.pop(0)  # Remove oldest (bottom)
        
        self._stack.append(state)
    
    def pop(self) -> Optional[Dict[str, Any]]:
        """Remove and return top element. O(1)."""
        if not self._stack:
            return None
        return self._stack.pop()
    
    def peek(self) -> Optional[Dict[str, Any]]:
        """View top element without removing. O(1)."""
        if not self._stack:
            return None
        return self._stack[-1]
    
    def size(self) -> int:
        """Return stack size. O(1)."""
        return len(self._stack)
    
    def clear(self) -> None:
        """Clear all elements. O(1)."""
        self._stack.clear()
```

### Time Complexity Analysis

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| Push | O(1) | Append to end |
| Pop | O(1) | Remove from end |
| Peek | O(1) | Access last element |
| Size | O(1) | Length of list |
| Clear | O(1) | Python optimization |
| Is Empty | O(1) | Check length |

**Note on Overflow Handling:**
- Max size: 10 elements
- When full: oldest element evicted (O(n) shift, but rare)

### Edge Cases Handled

| Edge Case | How It's Handled |
|-----------|------------------|
| **Pop empty stack** | Returns None, no crash |
| **Peek empty stack** | Returns None |
| **"Back" at root** | Clears stack, stays at root |
| **Stack overflow** | Evicts oldest element (max 10) |
| **Multiple "back" commands** | Each pops one level |
| **Reset conversation** | Clears stack, pushes root |
| **Concurrent users** | Each user has own stack instance |
| **Very deep navigation** | Limited to 10 levels |

### Stack vs Queue Comparison

| Feature | Stack (LIFO) | Queue (FIFO) |
|---------|--------------|--------------|
| "Back" navigation | ✅ Perfect | ❌ Would go forward |
| Recent first | ✅ Yes | ❌ Oldest first |
| Undo functionality | ✅ Natural | ❌ Unnatural |
| Breadcrumb trail | ✅ Maintains path | ❌ Loses order |

---

## 5. Union-Find (Disjoint Set)

### Definition

Union-Find (also called Disjoint Set Union or DSU) is a data structure that tracks elements partitioned into disjoint (non-overlapping) sets. It supports two operations: **Find** (determine which set an element belongs to) and **Union** (merge two sets).

### Justification for Use

**Why Union-Find for Synonym Grouping?**

Users express the same intent in many ways:

```
"cancel order" = "stop order" = "abort" = "cancel my order"
         \           |            /           /
          └─────────┴────────────┴───────────┘
                      ↓
              Canonical: "cancel"
```

**Without Union-Find:**
```python
# Messy, unmaintainable
if intent in ["cancel", "cancel order", "stop order", "abort", "cancel my order"]:
    handle_cancel()
```

**With Union-Find:**
```python
canonical = union_find.find(user_intent)  # O(α(n)) ≈ O(1)
if canonical == "cancel":
    handle_cancel()
```

### Visual Representation

```
Initial State (after unions):

cancel ←─── cancel order
   ↑
   ├─────── stop order
   │
   └─────── abort

track ←──── tracking
   ↑
   ├─────── where is my order
   │
   └─────── order status

contact ←── agent
    ↑
    ├────── human
    │
    └────── speak to someone


Find("stop order"):
stop order → parent("stop order") = "cancel" → return "cancel"

Find("where is my order"):
where is my order → parent → "track" → return "track"
```

### Implementation Details

```python
class UnionFind:
    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}
    
    def find(self, x: str) -> str:
        """
        Find root of set containing x, with path compression.
        Amortized O(α(n)) ≈ O(1) where α is inverse Ackermann.
        """
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            return x
        
        # Path compression: make all nodes point directly to root
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        
        return self.parent[x]
    
    def union(self, x: str, y: str) -> str:
        """
        Merge sets containing x and y. Uses union by rank.
        O(α(n)) amortized.
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return root_x
        
        # Union by rank: attach smaller tree under larger
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
        """Check if x and y are in same set. O(α(n))."""
        return self.find(x) == self.find(y)
```

### Time Complexity Analysis

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| Find | O(α(n)) ≈ O(1) | With path compression |
| Union | O(α(n)) ≈ O(1) | With union by rank |
| Are Equivalent | O(α(n)) ≈ O(1) | Two finds |
| Create Set | O(1) | Initialize parent to self |

**α(n)** is the inverse Ackermann function, which grows incredibly slowly:
- α(10^80) ≤ 4 (10^80 is atoms in universe)
- For all practical purposes, O(α(n)) = O(1)

### Edge Cases Handled

| Edge Case | How It's Handled |
|-----------|------------------|
| **Unknown phrase** | Returns itself as canonical |
| **Self-union** | No-op, returns same root |
| **Transitive synonyms** | Automatically linked (A=B, B=C → A=C) |
| **Case sensitivity** | All inputs lowercased before find |
| **Empty string** | Returns empty string as its own root |
| **Partial matches** | Words checked individually |
| **Circular references** | Path compression prevents |
| **Very long chains** | Flattened by path compression |

### Synonym Groups Defined

```python
# Cancel Intent Group
union("cancel", "cancel order")
union("cancel", "abort")
union("cancel", "stop order")
union("cancel", "cancel my order")
# Now: find("stop order") returns "cancel"

# Track Intent Group
union("track", "tracking")
union("track", "where is my order")
union("track", "order status")
union("track", "where is my package")
# Now: find("where is my package") returns "track"

# Return Intent Group
union("return", "refund")
union("return", "money back")
union("return", "send back")

# Contact Intent Group
union("contact", "agent")
union("contact", "human")
union("contact", "speak to someone")
union("contact", "real person")
```

---

## 6. Weighted Graph

### Definition

A Weighted Graph is a graph where each edge has an associated numerical value (weight). In this chatbot, nodes represent conversation states and edge weights represent transition probabilities to suggest "next best actions."

### Justification for Use

**Why Weighted Graph for Suggestions?**

Based on user behavior data, some actions are more likely than others:

```
From "Orders Menu":
- 50% of users track their order
- 30% cancel their order
- 15% modify their order
- 5% go back to main menu

Edge Weights:
orders_menu ──(0.50)──→ order_track
           ──(0.30)──→ order_cancel
           ──(0.15)──→ order_modify
           ──(0.05)──→ root
```

**Benefits:**
1. Suggests most likely actions first
2. Adapts to different contexts
3. Can be updated based on analytics
4. Natural graph traversal

### Visual Representation

```
                    ┌────────────────────────────────────────────┐
                    ▼                                            │
              ┌──────────┐                                       │
              │   ROOT   │                                       │
              └────┬─────┘                                       │
                   │                                             │
    ┌──────────────┼──────────────┬────────────────┐            │
    │ 0.35         │ 0.25         │ 0.20           │ 0.12       │
    ▼              ▼              ▼                ▼            │
┌────────┐   ┌──────────┐   ┌──────────┐    ┌──────────┐       │
│ Orders │   │  Returns │   │ Account  │    │ Products │       │
└────┬───┘   └────┬─────┘   └────┬─────┘    └────┬─────┘       │
     │            │              │               │              │
     │ 0.50       │ 0.45         │ 0.40          │ 0.40        │
     ▼            ▼              ▼               ▼              │
┌─────────┐  ┌─────────┐   ┌──────────┐   ┌──────────┐         │
│  Track  │  │  Start  │   │ Password │   │ Pricing  │         │
└────┬────┘  └────┬────┘   └────┬─────┘   └────┬─────┘         │
     │            │              │               │              │
     │ 0.40       │ 0.35         │ 0.45          │ 0.35        │
     ▼            ▼              ▼               ▼              │
┌─────────┐  ┌─────────┐   ┌──────────┐   ┌──────────┐         │
│  Chat   │──│  Chat   │───│   Chat   │───│  Orders  │─────────┘
│ (Agent) │  │ (Agent) │   │ (Agent)  │   │  (Place) │
└─────────┘  └─────────┘   └──────────┘   └──────────┘

Edge weights shown are probabilities (0.0 to 1.0)
Top 3 edges from each node are suggested to user
```

### Implementation Details

```python
class WeightedGraph:
    def __init__(self):
        # Adjacency list: node -> [(neighbor, weight, label), ...]
        self.graph: Dict[str, List[Tuple[str, float, str]]] = {}
        self.node_labels: Dict[str, str] = {}
    
    def add_node(self, node_id: str, label: str = "") -> None:
        """Add a node to the graph. O(1)."""
        if node_id not in self.graph:
            self.graph[node_id] = []
        self.node_labels[node_id] = label
    
    def add_edge(self, from_node: str, to_node: str, 
                 weight: float = 1.0, label: str = "") -> None:
        """Add weighted edge. O(1)."""
        if from_node not in self.graph:
            self.graph[from_node] = []
        self.graph[from_node].append((to_node, weight, label))
    
    def get_suggestions(self, current_node: str, top_k: int = 3) -> List[Dict]:
        """
        Get top-k next actions sorted by weight.
        O(E log E) where E = edges from current node.
        """
        if current_node not in self.graph:
            return []
        
        edges = self.graph[current_node]
        
        # Sort by weight descending
        sorted_edges = sorted(edges, key=lambda x: x[1], reverse=True)
        
        # Return top k
        suggestions = []
        for to_node, weight, label in sorted_edges[:top_k]:
            suggestions.append({
                "action": to_node,
                "weight": weight,
                "label": label or self.node_labels.get(to_node, to_node)
            })
        
        return suggestions
```

### Time Complexity Analysis

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| Add Node | O(1) | Dict insertion |
| Add Edge | O(1) | List append |
| Get Suggestions | O(E log E) | Sort edges, E = edge count |
| BFS/DFS | O(V + E) | If needed for analytics |

For our use case with ~5 edges per node: O(5 log 5) ≈ O(1)

### Edge Cases Handled

| Edge Case | How It's Handled |
|-----------|------------------|
| **Unknown node** | Returns empty suggestions |
| **No outgoing edges** | Returns empty list |
| **Fewer than k edges** | Returns all available edges |
| **Zero weight edges** | Still included, sorted last |
| **Negative weights** | Allowed, sorted correctly |
| **Self-loops** | Allowed but not added in our case |
| **Multiple edges** | All stored, highest weight suggested |
| **Disconnected nodes** | Each handles individually |

### Weight Calibration

Weights can be calibrated based on:

```python
# Example: Analytics-based weight update
def update_weights_from_analytics(analytics_data):
    for from_node, to_node, click_count in analytics_data:
        total_clicks = sum(c for _, _, c in analytics_data if _ == from_node)
        new_weight = click_count / total_clicks
        graph.update_edge(from_node, to_node, new_weight)
```

---

## Summary Comparison

| Data Structure | Time Complexity | Space | Primary Use |
|----------------|-----------------|-------|-------------|
| **Trie** | O(m) insert, O(p+k) search | O(n×m) | Auto-complete |
| **HashMap** | O(1) average | O(n) | FAQ lookup |
| **Decision Tree** | O(k) per navigation | O(n) nodes | Conversation flow |
| **Stack** | O(1) all ops | O(h) depth | Back navigation |
| **Union-Find** | O(α(n)) ≈ O(1) | O(n) | Synonym grouping |
| **Weighted Graph** | O(E log E) suggest | O(V+E) | Next best actions |

---

## Integration Flow

```
User Input: "stop order"
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        PROCESSING PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│  1. TRIE: Show suggestions as user types                        │
│     └─→ "stop", "stop order" suggestions appear                 │
│                                                                  │
│  2. UNION-FIND: Normalize intent                                 │
│     └─→ find("stop order") = "cancel"                           │
│                                                                  │
│  3. HASHMAP: Check for FAQ match                                 │
│     └─→ lookup("cancel") = None (not an FAQ)                    │
│                                                                  │
│  4. DECISION TREE: Navigate conversation                         │
│     └─→ "cancel" matches option → order_cancel node              │
│                                                                  │
│  5. STACK: Record navigation history                             │
│     └─→ push("order_cancel")                                     │
│                                                                  │
│  6. WEIGHTED GRAPH: Suggest next actions                         │
│     └─→ [Start Return (40%), Chat (35%), Back (25%)]            │
└─────────────────────────────────────────────────────────────────┘
      │
      ▼
Response: "Cancel Order" + Quick Action Buttons with %
```

---

## References

1. Cormen, T.H., et al. "Introduction to Algorithms" (CLRS)
2. Sedgewick, R. "Algorithms" (4th Edition)
3. Skiena, S. "The Algorithm Design Manual"
4. Python Documentation: Data Structures
5. Tarjan, R.E. "Efficiency of a Good But Not Linear Set Union Algorithm"
