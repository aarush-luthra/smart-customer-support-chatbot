# Data Structures Documentation
## ShopDS Technical Reference

This document provides a non-technical guide to the data structures used in the ShopDS application and Support Assistant. It explains how each feature utilizes a specific structure to provide a fast and intelligent user experience.

---

## Table of Contents

1. [Auto-Complete Suggestions (Trie)](#1-auto-complete-suggestions-trie)
2. [Data Management & Lookups (HashMap)](#2-data-management--lookups-hashmap)
3. [Conversation Flow (Decision Tree)](#3-conversation-flow-decision-tree)
4. [Navigation History (Stack)](#4-navigation-history-stack)
5. [Intent Normalization (Union-Find)](#5-intent-normalization-union-find)
6. [Next Best Actions (Weighted Graph)](#6-next-best-actions-weighted-graph)
7. [Recently Viewed (Linked List)](#7-recently-viewed-linked-list)
8. [Product Recommendations (Priority Queue)](#8-product-recommendations-priority-queue)
9. [Transaction Processing (Queue)](#9-transaction-processing-queue)

---

## 1. Auto-Complete Suggestions (Trie)

### What it is
A Trie (Prefix Tree) is a tree-like structure where each node represents a character. It is optimized for searching strings based on their prefix.

### How it is used
As the user types into the chatbot input, the system traverses the Trie character by character. If the user types "or", the system instantly finds all paths starting with "o" -> "r", yielding results like "orders" or "order history".

### Why we use it (Justification)
Unlike a simple list search that scans every word, a Trie only visits the characters typed. This ensures suggestions appear **instantly** without lag, improving the user experience for frequent commands.

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
                    u
                    s

Words stored: order, orders, order status, cancel, cancellation, return
```

---

## 2. Data Management & Lookups (HashMap)

### What it is
A HashMap maps unique keys to values, providing near-instant retrieval of data.

### How it is used
The application uses HashMaps for several core features:
- **Product Catalog**: Retrieves full product details instantly using the Product ID.
- **User Profile**: Accesses user info (Aarush, Email) using the User ID.
- **Support FAQs**: Matches user keywords to pre-defined answers.
- **Wishlist/Cart**: Tracks which items are selected without duplicates.

### Why we use it (Justification)
In an e-commerce setting, as the number of products grows, searching through a long list becomes slow. A HashMap ensures that looking up an item takes the **same amount of time** whether there are 10 products or 10 million.

### Visual Representation
```
Index │ Key        │ Value (Data/Response)                  
──────┼────────────┼────────────────────────────────────────
  1   │ "pricing"  │ "Our pricing varies by product..."    
  2   │ "shipping" │ "Standard: 5-7 days..."               
  4   │ "return"   │ "30-day return policy..."             
  5   │ "hours"    │ "Mon-Fri: 9 AM - 9 PM..."             
```

---

## 3. Conversation Flow (Decision Tree)

### What it is
A Decision Tree is a hierarchical structure where each choice leads to a new "node" or state in the conversation.

### How it is used
The chatbot uses this to guide users through help menus. Choosing "Orders" moves the user to a specific "Orders Menu" node, which then branches into "Track" or "Cancel".

### Why we use it (Justification)
It mirrors a natural conversation. Instead of analyzing every sentence with complex AI, the tree provides a **reliable and structured** way to help users solve common problems quickly.

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
    ┌─────┴─────┐    │    ┌─────┴─────┐    │    ┌─────┴─────┐
    ▼           ▼    ▼    ▼           ▼    ▼    ▼           ▼
 ┌─────┐     ┌─────┐   ┌─────────┐ ┌─────────┐ ┌─────────┐
 │Track│     │Cancel│   │Password │ │Profile  │ │Email/Chat
 └─────┘     └─────┘   └─────────┘ └─────────┘ └─────────┘
```

---

## 4. Navigation History (Stack)

### What it is
A Stack is a "Last-In, First-Out" structure. The last item added is the first one removed (like a stack of plates).

### How it is used
The chatbot uses a Stack to power the **"Back" command**. Every time you navigate to a new menu, the system "pushes" the previous menu onto the stack. When you type "back", it "pops" that last menu to return you exactly where you were.

### Why we use it (Justification)
A Stack is the perfect tool for **undoing actions**. It ensures that the user can never get "lost" in deep menus, as they can always walk back their steps one by one.

### Visual Representation
```
Step 1: In "Orders"        Step 2: In "Track"       Step 3: Pop (Back)
┌─────────────┐           ┌─────────────┐          ┌─────────────┐
│             │           │   track     │ ← TOP    │             │
│   orders    │ ← TOP     ├─────────────┤          │   orders    │ ← TOP
├─────────────┤           │   orders    │          ├─────────────┤
│    root     │           ├─────────────┤          │    root     │
└─────────────┘           │    root     │          └─────────────┘
                          └─────────────┘
```

---

## 5. Intent Normalization (Union-Find)

### What it is
Union-Find groups related items into "sets." It can quickly determine if two items belong to the same group.

### How it is used
The chatbot uses this for **synonym detection**. Words like "buy", "purchase", and "pay" are all grouped into the same set. When a user types any of these, the system identifies the core "intent" instantly.

### Why we use it (Justification)
It makes the chatbot feel smarter without needing to manually program every possible word variation. It simplifies complex language into **meaningful categories**.

### Visual Representation
```
Group: CANCEL              Group: TRACK
cancel ←── cancel order    track ←── tracking
   ↑                          ↑
   ├─────── stop order        ├─────── where is it
   │                          │
   └─────── abort             └─────── status
```

---

## 6. Next Best Actions (Weighted Graph)

### What it is
A Weighted Graph connects nodes with edges that have "weights" (importance or probability).

### How it is used
The Support Assistant uses this to suggest **Quick Actions**. It analyzes common paths—for example, most users who check "Orders" also want to "Track"—so it assigns a higher "weight" to the Track suggestion.

### Why we use it (Justification)
It makes the assistant **proactive**. By predicting the user's next logical step based on weights, the system saves the user time by placing the most relevant buttons right in front of them.

### Visual Representation
```
From Orders Menu:
──(0.50)──→ Track Order (High probability)
──(0.30)──→ Cancel Order
──(0.15)──→ Modify Order
──(0.05)──→ Return to Menu (Low probability)
```

---

## 7. Recently Viewed (Linked List)

### What it is
A Linked List is a series of nodes where each node points to the next, ideal for maintaining an ordered sequence.

### How it is used
Every time you view a product, it is added to the head of the **Recently Viewed** list. If the list exceeds 4 items, the oldest item (the tail) is removed.

### Why we use it (Justification)
It is the most efficient way to manage a **scrolling history**. Adding a new item to the front of a Linked List is extremely fast (O(1)), ensuring the page remains responsive even while tracking user behavior.

---

## 8. Product Recommendations (Priority Queue)

### What it is
A Priority Queue stores items and always keeps the "most important" or "highest scoring" items at the top.

### How it is used
The **Recommendations** section calculates a score for products based on your profile. A Priority Queue automatically sorts the products so that those with the highest scores are displayed first.

### Why we use it (Justification)
Instead of sorting the entire catalog every time (which is slow), a Priority Queue efficiently extracts the **Top 5** items, making the discovery process fast and personalized.

---

## 9. Transaction Processing (Queue)

### What it is
A Queue follows "First-In, First-Out" (FIFO). The first item to enter is the first to leave.

### How it is used
The **Checkout Flow** uses a queue to ensure users follow the correct sequence: Cart -> Shipping -> Payment -> Confirm. It also ensures that order processing happens in the correct chronological order.

### Why we use it (Justification)
It guarantees **fairness and order**. In high-traffic scenarios, a Queue ensures that the first customer who finishes their payment is the first one who gets their order confirmed.

---

## Summary of Efficiency

| Feature             | Data Structure  | Efficiency | Impact                    |
|---------------------|-----------------|------------|---------------------------|
| Search/Suggestions  | Trie            | High       | Instant typing feedback   |
| Product Retrieval   | HashMap         | Constant   | Fast page loads           |
| Conversation Flow   | Decision Tree   | Linear     | Reliable bot responses    |
| Navigate Back       | Stack           | Constant   | Smooth menu navigation    |
| Synonym Matching    | Union-Find      | Amortized  | Intelligent understanding |
| Likely Actions      | Weighted Graph  | Predictive | Proactive user help       |
| History Tracking    | Linked List     | Constant   | Zero-lag history updates  |
| Personalized List   | Priority Queue  | Logarithmic| Best products first       |
| Multi-step Flow     | Queue           | Constant   | Secure checkout order     |
