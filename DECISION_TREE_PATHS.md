# Decision Tree Paths
## Complete Navigation Guide

This document shows all possible paths through the chatbot's decision tree.

---

## Tree Structure Overview

```
Welcome (Root)
├── Orders
│   ├── Track Order
│   ├── Cancel Order
│   └── Modify Order
├── Returns
│   ├── Start Return
│   ├── Check Status
│   └── Return Policy
├── Account
│   ├── Password Reset
│   ├── Update Profile
│   └── Order History
├── Products
│   ├── Pricing
│   ├── Stock
│   └── Deals
└── Contact
    ├── Phone
    ├── Email
    └── Live Chat
```

---

## All Navigation Paths

### Path 1: Orders → Track Order
```
Welcome → "orders" → Orders Menu → "track" → Track Order
```
**Keywords:** orders, order, track, status

---

### Path 2: Orders → Cancel Order
```
Welcome → "orders" → Orders Menu → "cancel" → Cancel Order
```
**Keywords:** orders, cancel

---

### Path 3: Orders → Modify Order
```
Welcome → "orders" → Orders Menu → "modify" → Modify Order
```
**Keywords:** orders, modify, change

---

### Path 4: Returns → Start Return
```
Welcome → "returns" → Returns Menu → "start" → Start Return
```
**Keywords:** returns, refund, start, begin, new

---

### Path 5: Returns → Check Status
```
Welcome → "returns" → Returns Menu → "status" → Return Status
```
**Keywords:** returns, status, check

---

### Path 6: Returns → Return Policy
```
Welcome → "returns" → Returns Menu → "policy" → Return Policy
```
**Keywords:** returns, policy

---

### Path 7: Account → Password Reset
```
Welcome → "account" → Account Menu → "password" → Password Reset
```
**Keywords:** account, login, password, reset

---

### Path 8: Account → Update Profile
```
Welcome → "account" → Account Menu → "profile" → Update Profile
```
**Keywords:** account, profile, update

---

### Path 9: Account → Order History
```
Welcome → "account" → Account Menu → "orders" → Order History
```
**Keywords:** account, orders, history

---

### Path 10: Products → Pricing
```
Welcome → "products" → Products Menu → "pricing" → Pricing Info
```
**Keywords:** products, pricing, price, cost

---

### Path 11: Products → Stock
```
Welcome → "products" → Products Menu → "stock" → Stock Availability
```
**Keywords:** products, stock, availability

---

### Path 12: Products → Deals
```
Welcome → "products" → Products Menu → "deals" → Current Deals
```
**Keywords:** products, deals, discount

---

### Path 13: Contact → Phone
```
Welcome → "contact" → Contact Menu → "phone" → Phone Support
```
**Keywords:** contact, agent, human, phone, call

---

### Path 14: Contact → Email
```
Welcome → "contact" → Contact Menu → "email" → Email Support
```
**Keywords:** contact, email, mail

---

### Path 15: Contact → Live Chat
```
Welcome → "contact" → Contact Menu → "chat" → Live Chat
```
**Keywords:** contact, chat, live, agent

---

## Navigation Commands

| Command | Action |
|---------|--------|
| `back` | Go to previous screen |
| `menu` | Return to Welcome screen |

---

## Synonym Mappings (Union-Find)

These phrases are treated as equivalent:

| You Type | Interpreted As |
|----------|----------------|
| "stop order" | cancel |
| "abort" | cancel |
| "where is my order" | track |
| "tracking" | track |
| "order status" | track |
| "refund" | return |
| "money back" | return |
| "agent" | contact |
| "human" | contact |
| "speak to someone" | contact |

---

## Quick Reference Card

| To Do This | Type This |
|------------|-----------|
| Track an order | `orders` → `track` |
| Cancel an order | `orders` → `cancel` |
| Start a return | `returns` → `start` |
| Check return status | `returns` → `status` |
| Reset password | `account` → `password` |
| View pricing | `products` → `pricing` |
| See current deals | `products` → `deals` |
| Talk to someone | `contact` → `chat` |
| Look up order | Type Order ID: `ORD-12345` |
| Go back | `back` |
| Start over | `menu` |
