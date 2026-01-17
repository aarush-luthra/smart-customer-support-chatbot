"""
Support Engine - Main Orchestrator for the Customer Support System

This module coordinates all 6 data structures:
1. Trie - Auto-complete suggestions
2. HashMap - O(1) FAQ lookups
3. Decision Tree - Conversation flow with branching
4. Stack - "Go back" navigation
5. Union-Find - Synonym intent grouping
6. Weighted Graph - Next best action suggestions

Author: Customer Support System
"""

from typing import Dict, Any, List, Optional
from backend.data_structures import (
    Trie,
    FAQHashMap,
    DecisionTree,
    ConversationStack,
    UnionFind,
    WeightedGraph
)


class SupportEngine:
    """
    Main orchestrator for the customer support system.
    
    Coordinates all 6 data structures to provide intelligent responses.
    """
    
    def __init__(self):
        """Initialize all data structures."""
        # DS 1: Trie for auto-complete
        self._trie = Trie()
        
        # DS 2: HashMap for FAQ lookups
        self._faq_map = FAQHashMap()
        
        # DS 3: Decision Tree for conversation flow
        self._decision_tree = DecisionTree()
        
        # DS 4: Stack for user navigation (per user)
        self._user_stacks: Dict[str, ConversationStack] = {}
        
        # DS 5: Union-Find for synonym grouping
        self._intent_groups = UnionFind()
        
        # DS 6: Weighted Graph for next actions
        self._action_graph = WeightedGraph()
        
        # Initialize all content
        self._populate_trie()
        self._populate_faq()
        self._build_decision_tree()
        self._setup_intent_groups()
        self._build_action_graph()
    
    def _get_user_stack(self, user_id: str) -> ConversationStack:
        """Get or create stack for user."""
        if user_id not in self._user_stacks:
            self._user_stacks[user_id] = ConversationStack()
        return self._user_stacks[user_id]
    
    # =========================================================================
    # DATA STRUCTURE 1: TRIE - Auto-Complete
    # =========================================================================
    
    def _populate_trie(self) -> None:
        """Populate Trie with keywords for auto-suggestions."""
        keywords = [
            # Order related
            "order", "order status", "order tracking", "my order",
            "orders", "track order", "where is my order",
            
            # Cancel/Return
            "cancel", "cancel order", "cancellation", "return",
            "refund", "return policy", "money back",
            
            # Shipping
            "shipping", "delivery", "track package", "shipping cost",
            "free shipping", "express delivery",
            
            # Payment
            "payment", "pay", "credit card", "payment failed",
            "invoice", "receipt", "billing",
            
            # Account
            "account", "login", "password", "reset password",
            "profile", "settings", "my account",
            
            # Support
            "help", "support", "contact", "agent", "human",
            "problem", "issue", "complaint",
            
            # Products
            "products", "pricing", "discount", "sale", "coupon",
            
            # General
            "hello", "hi", "thanks", "thank you", "bye", "goodbye"
        ]
        
        for word in keywords:
            self._trie.insert(word)
    
    def get_suggestions(self, prefix: str) -> Dict[str, Any]:
        """
        Get auto-suggestions using Trie.
        
        DATA STRUCTURE: Trie (Prefix Tree)
        """
        suggestions = self._trie.get_suggestions(prefix, max_suggestions=8)
        
        return {
            "suggestions": suggestions,
            "prefix": prefix,
            "count": len(suggestions),
            "data_structure": "Trie (Prefix Tree)",
            "complexity": "O(prefix_length + matches)"
        }
    
    # =========================================================================
    # DATA STRUCTURE 2: HASHMAP - FAQ Lookup
    # =========================================================================
    
    def _populate_faq(self) -> None:
        """Populate FAQ HashMap with responses."""
        faqs = [
            {
                "keywords": ["pricing", "price", "cost", "how much"],
                "response": "Our pricing varies by product. Visit our Products page for current prices. Most items range from $10-$500. Premium members get 15% off!",
                "category": "pricing"
            },
            {
                "keywords": ["shipping", "delivery time", "how long"],
                "response": "Standard shipping: 5-7 business days (free over $50)\nExpress shipping: 2-3 business days ($9.99)\nOvernight: Next business day ($19.99)",
                "category": "shipping"
            },
            {
                "keywords": ["return", "return policy", "returns"],
                "response": "We offer a 30-day return policy for unused items in original packaging. Refunds are processed within 5-7 business days after we receive the item.",
                "category": "returns"
            },
            {
                "keywords": ["contact", "phone", "email", "reach"],
                "response": "Contact us:\nEmail: support@shop.com\nPhone: 1-800-SHOP-NOW\nLive chat: 9 AM - 9 PM EST\nAddress: 123 Commerce St, NY",
                "category": "contact"
            },
            {
                "keywords": ["hours", "open", "business hours"],
                "response": "Customer Support Hours:\nMonday-Friday: 9 AM - 9 PM EST\nSaturday: 10 AM - 6 PM EST\nSunday: Closed\nChatbot: 24/7",
                "category": "hours"
            },
            {
                "keywords": ["payment", "payment methods", "pay with"],
                "response": "We accept:\n- Credit/Debit Cards (Visa, MasterCard, Amex)\n- PayPal\n- Apple Pay\n- Google Pay\n- Gift Cards",
                "category": "payment"
            },
            {
                "keywords": ["track", "tracking", "where is", "package"],
                "response": "To track your order:\n1. Log into your account\n2. Go to 'My Orders'\n3. Click 'Track Package'\n\nOr enter your tracking number at our tracking page!",
                "category": "tracking"
            },
            {
                "keywords": ["discount", "coupon", "promo", "sale"],
                "response": "Current offers:\n- SAVE10: 10% off orders over $50\n- FREESHIP: Free shipping on any order\n- Join our newsletter for exclusive deals!",
                "category": "promotions"
            }
        ]
        
        for faq in faqs:
            self._faq_map.add_faq(
                keywords=faq["keywords"],
                response=faq["response"],
                category=faq["category"]
            )
    
    # =========================================================================
    # DATA STRUCTURE 3: DECISION TREE - Conversation Flow
    # =========================================================================
    
    def _build_decision_tree(self) -> None:
        """Build the conversation decision tree."""
        tree = self._decision_tree
        
        # Root node
        tree.add_node(
            "root",
            "Welcome to Customer Support! How can I help you today?\n\n"
            "Choose a topic:\n"
            "- Orders: Track, cancel, or modify orders\n"
            "- Returns: Return items or request refunds\n"
            "- Account: Login, password, or profile help\n"
            "- Products: Pricing and availability\n"
            "- Contact: Speak to a human agent",
            options={
                "order": "orders_menu",
                "orders": "orders_menu",
                "return": "returns_menu",
                "refund": "returns_menu",
                "account": "account_menu",
                "login": "account_menu",
                "product": "products_menu",
                "pricing": "products_menu",
                "contact": "contact_menu",
                "agent": "contact_menu",
                "human": "contact_menu"
            }
        )
        
        # Orders Menu
        tree.add_node(
            "orders_menu",
            "**Orders Menu**\n\n"
            "What would you like to do?\n"
            "- Track: Check order status\n"
            "- Cancel: Cancel an order\n"
            "- Modify: Change order details\n"
            "- Back: Return to main menu",
            options={
                "track": "order_track",
                "status": "order_track",
                "cancel": "order_cancel",
                "modify": "order_modify",
                "change": "order_modify",
                "back": "root",
                "menu": "root"
            }
        )
        
        tree.add_node(
            "order_track",
            "**Track Your Order**\n\n"
            "To track your order, please provide:\n"
            "- Your Order ID (e.g., ORD-12345)\n"
            "- Or the email used for the order\n\n"
            "Tip: Check your confirmation email for the Order ID.\n\n"
            "Type 'back' to return to Orders menu.",
            options={"back": "orders_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "order_cancel",
            "**Cancel Order**\n\n"
            "I can help you cancel your order.\n\n"
            "Please note:\n"
            "- Orders can only be cancelled before shipping\n"
            "- Refund will be processed in 5-7 days\n\n"
            "Please provide your Order ID to proceed.\n\n"
            "Type 'back' to return to Orders menu.",
            options={"back": "orders_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "order_modify",
            "**Modify Order**\n\n"
            "You can modify:\n"
            "- Shipping address\n"
            "- Delivery date\n"
            "- Add gift wrapping\n\n"
            "Note: Modifications only available before shipping.\n\n"
            "Please provide your Order ID.\n\n"
            "Type 'back' to return to Orders menu.",
            options={"back": "orders_menu", "menu": "root"},
            is_leaf=True
        )
        
        # Returns Menu
        tree.add_node(
            "returns_menu",
            "**Returns & Refunds**\n\n"
            "How can I help?\n"
            "- Start Return: Begin a new return\n"
            "- Check Status: Track your return\n"
            "- Policy: View return policy\n"
            "- Back: Return to main menu",
            options={
                "start": "return_start",
                "begin": "return_start",
                "new": "return_start",
                "status": "return_status",
                "check": "return_status",
                "policy": "return_policy",
                "back": "root",
                "menu": "root"
            }
        )
        
        tree.add_node(
            "return_start",
            "**Start a Return**\n\n"
            "To initiate a return:\n"
            "1. Provide your Order ID\n"
            "2. Select items to return\n"
            "3. Choose refund method\n\n"
            "Return window: 30 days from delivery.\n\n"
            "Type 'back' to return to Returns menu.",
            options={"back": "returns_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "return_status",
            "**Return Status**\n\n"
            "Enter your Return ID (e.g., RET-12345) to check:\n"
            "- Return shipment status\n"
            "- Refund processing status\n"
            "- Expected refund date\n\n"
            "Type 'back' to return to Returns menu.",
            options={"back": "returns_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "return_policy",
            "**Return Policy**\n\n"
            "Allowed:\n"
            "- 30-day return window\n"
            "- Free returns for members\n"
            "- Full refund to original payment\n"
            "- Exchange available\n\n"
            "Not allowed:\n"
            "- Final sale items non-returnable\n"
            "- Items must be unused with tags\n\n"
            "Type 'back' to return to Returns menu.",
            options={"back": "returns_menu", "menu": "root"},
            is_leaf=True
        )
        
        # Account Menu
        tree.add_node(
            "account_menu",
            "**Account Help**\n\n"
            "What do you need help with?\n"
            "- Password: Reset or change password\n"
            "- Profile: Update your information\n"
            "- Orders: View order history\n"
            "- Back: Return to main menu",
            options={
                "password": "account_password",
                "reset": "account_password",
                "profile": "account_profile",
                "update": "account_profile",
                "orders": "account_orders",
                "history": "account_orders",
                "back": "root",
                "menu": "root"
            }
        )
        
        tree.add_node(
            "account_password",
            "**Password Reset**\n\n"
            "To reset your password:\n"
            "1. Click 'Forgot Password' on login page\n"
            "2. Enter your email address\n"
            "3. Check email for reset link\n"
            "4. Create new password\n\n"
            "Password must be 8+ characters.\n\n"
            "Type 'back' to return to Account menu.",
            options={"back": "account_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "account_profile",
            "**Update Profile**\n\n"
            "You can update:\n"
            "- Name and email\n"
            "- Shipping addresses\n"
            "- Payment methods\n"
            "- Communication preferences\n\n"
            "Go to Account > Profile Settings\n\n"
            "Type 'back' to return to Account menu.",
            options={"back": "account_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "account_orders",
            "**Order History**\n\n"
            "View all your orders at Account > My Orders\n\n"
            "From there you can:\n"
            "- Track active orders\n"
            "- Reorder past items\n"
            "- Download invoices\n"
            "- Start returns\n\n"
            "Type 'back' to return to Account menu.",
            options={"back": "account_menu", "menu": "root"},
            is_leaf=True
        )
        
        # Products Menu
        tree.add_node(
            "products_menu",
            "**Products & Pricing**\n\n"
            "What would you like to know?\n"
            "- Pricing: Current prices\n"
            "- Availability: Stock status\n"
            "- Deals: Current promotions\n"
            "- Back: Return to main menu",
            options={
                "pricing": "products_pricing",
                "price": "products_pricing",
                "cost": "products_pricing",
                "availability": "products_stock",
                "stock": "products_stock",
                "deals": "products_deals",
                "discount": "products_deals",
                "back": "root",
                "menu": "root"
            }
        )
        
        tree.add_node(
            "products_pricing",
            "**Pricing Information**\n\n"
            "Prices are shown on each product page.\n\n"
            "Member discounts:\n"
            "- Silver: 5% off\n"
            "- Gold: 10% off\n"
            "- Platinum: 15% off\n\n"
            "Type a product name to check its price!\n\n"
            "Type 'back' to return to Products menu.",
            options={"back": "products_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "products_stock",
            "**Stock Availability**\n\n"
            "Stock status is shown on product pages:\n"
            "- In Stock: Ships within 24h\n"
            "- Low Stock: Only a few left\n"
            "- Pre-order: Coming soon\n"
            "- Out of Stock: Sign up for alerts\n\n"
            "Type 'back' to return to Products menu.",
            options={"back": "products_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "products_deals",
            "**Current Deals**\n\n"
            "Active promotions:\n"
            "- SAVE10: 10% off $50+ orders\n"
            "- FREESHIP: Free shipping\n"
            "- NEWUSER: 15% off first order\n\n"
            "Subscribe to our newsletter for exclusive deals!\n\n"
            "Type 'back' to return to Products menu.",
            options={"back": "products_menu", "menu": "root"},
            is_leaf=True
        )
        
        # Contact Menu
        tree.add_node(
            "contact_menu",
            "**Contact Support**\n\n"
            "How would you like to reach us?\n"
            "- Phone: Call our support line\n"
            "- Email: Send us a message\n"
            "- Chat: Live agent (if available)\n"
            "- Back: Return to main menu",
            options={
                "phone": "contact_phone",
                "call": "contact_phone",
                "email": "contact_email",
                "mail": "contact_email",
                "chat": "contact_chat",
                "live": "contact_chat",
                "agent": "contact_chat",
                "back": "root",
                "menu": "root"
            }
        )
        
        tree.add_node(
            "contact_phone",
            "**Phone Support**\n\n"
            "Call us at: 1-800-SHOP-NOW (1-800-746-7669)\n\n"
            "Hours:\n"
            "- Mon-Fri: 9 AM - 9 PM EST\n"
            "- Saturday: 10 AM - 6 PM EST\n"
            "- Sunday: Closed\n\n"
            "Average wait time: 5 minutes\n\n"
            "Type 'back' to return to Contact menu.",
            options={"back": "contact_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "contact_email",
            "**Email Support**\n\n"
            "Email: support@shop.com\n\n"
            "Response times:\n"
            "- General inquiries: 24-48 hours\n"
            "- Urgent issues: 4-6 hours\n"
            "- Order problems: Same business day\n\n"
            "Include your Order ID for faster help!\n\n"
            "Type 'back' to return to Contact menu.",
            options={"back": "contact_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "contact_chat",
            "**Live Chat**\n\n"
            "Our live agents are here to help!\n\n"
            "Status: ONLINE\n"
            "Wait time: ~2 minutes\n\n"
            "A human agent will join this chat shortly...\n\n"
            "(This is a demo - no actual agent will connect)\n\n"
            "Type 'back' to return to Contact menu.",
            options={"back": "contact_menu", "menu": "root"},
            is_leaf=True
        )
    
    # =========================================================================
    # DATA STRUCTURE 5: UNION-FIND - Intent Grouping
    # =========================================================================
    
    def _setup_intent_groups(self) -> None:
        """Setup synonym/intent groups using Union-Find."""
        uf = self._intent_groups
        
        # Cancel intent group
        uf.union("cancel", "cancel order")
        uf.union("cancel", "abort")
        uf.union("cancel", "stop order")
        uf.union("cancel", "cancel my order")
        
        # Track intent group
        uf.union("track", "tracking")
        uf.union("track", "where is my order")
        uf.union("track", "order status")
        uf.union("track", "where is my package")
        uf.union("track", "track order")
        
        # Return intent group
        uf.union("return", "refund")
        uf.union("return", "money back")
        uf.union("return", "send back")
        uf.union("return", "return item")
        
        # Contact intent group
        uf.union("contact", "agent")
        uf.union("contact", "human")
        uf.union("contact", "speak to someone")
        uf.union("contact", "talk to agent")
        uf.union("contact", "real person")
        
        # Account intent group
        uf.union("account", "login")
        uf.union("account", "password")
        uf.union("account", "sign in")
        uf.union("account", "my account")
    
    def normalize_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Normalize user input to canonical intent using Union-Find.
        
        DATA STRUCTURE: Union-Find (Disjoint Set)
        """
        user_lower = user_input.lower().strip()
        
        # Try to find canonical intent
        canonical = self._intent_groups.find(user_lower)
        
        # Also check individual words
        words = user_lower.split()
        for word in words:
            word_canonical = self._intent_groups.find(word)
            if word_canonical != word:  # Found a grouping
                canonical = word_canonical
                break
        
        return {
            "original": user_input,
            "canonical": canonical,
            "normalized": canonical != user_lower,
            "data_structure": "Union-Find (Disjoint Set)"
        }
    
    # =========================================================================
    # DATA STRUCTURE 6: WEIGHTED GRAPH - Next Actions
    # =========================================================================
    
    def _build_action_graph(self) -> None:
        """Build weighted graph for next action suggestions."""
        g = self._action_graph
        
        # From root/main menu
        g.add_node("root", "Main Menu")
        g.add_edge("root", "orders_menu", 0.4, "Check Orders")
        g.add_edge("root", "returns_menu", 0.25, "Returns & Refunds")
        g.add_edge("root", "products_menu", 0.2, "Browse Products")
        g.add_edge("root", "contact_menu", 0.15, "Contact Support")
        
        # From orders menu
        g.add_node("orders_menu", "Orders")
        g.add_edge("orders_menu", "order_track", 0.5, "Track Order")
        g.add_edge("orders_menu", "order_cancel", 0.3, "Cancel Order")
        g.add_edge("orders_menu", "order_modify", 0.15, "Modify Order")
        g.add_edge("orders_menu", "root", 0.05, "Main Menu")
        
        # From order tracking
        g.add_node("order_track", "Track Order")
        g.add_edge("order_track", "contact_chat", 0.4, "Chat with Agent")
        g.add_edge("order_track", "order_cancel", 0.3, "Cancel Order")
        g.add_edge("order_track", "orders_menu", 0.3, "Back to Orders")
        
        # From order cancel
        g.add_node("order_cancel", "Cancel Order")
        g.add_edge("order_cancel", "return_start", 0.4, "Start Return Instead")
        g.add_edge("order_cancel", "contact_chat", 0.35, "Need Help?")
        g.add_edge("order_cancel", "orders_menu", 0.25, "Back to Orders")
        
        # From returns menu
        g.add_node("returns_menu", "Returns")
        g.add_edge("returns_menu", "return_start", 0.45, "Start Return")
        g.add_edge("returns_menu", "return_status", 0.35, "Check Status")
        g.add_edge("returns_menu", "return_policy", 0.15, "View Policy")
        g.add_edge("returns_menu", "root", 0.05, "Main Menu")
        
        # From return start
        g.add_node("return_start", "Start Return")
        g.add_edge("return_start", "return_status", 0.4, "Track Return")
        g.add_edge("return_start", "contact_chat", 0.35, "Need Help?")
        g.add_edge("return_start", "returns_menu", 0.25, "Back to Returns")
        
        # From contact menu
        g.add_node("contact_menu", "Contact")
        g.add_edge("contact_menu", "contact_chat", 0.5, "Live Chat")
        g.add_edge("contact_menu", "contact_phone", 0.3, "Call Us")
        g.add_edge("contact_menu", "contact_email", 0.15, "Email")
        g.add_edge("contact_menu", "root", 0.05, "Main Menu")
    
    def get_next_actions(self, current_state: str) -> Dict[str, Any]:
        """
        Get suggested next actions using Weighted Graph.
        
        DATA STRUCTURE: Weighted Graph (Adjacency List)
        """
        suggestions = self._action_graph.get_suggestions(current_state, top_k=3)
        
        return {
            "current_state": current_state,
            "suggestions": suggestions,
            "count": len(suggestions),
            "data_structure": "Weighted Graph"
        }
    
    # =========================================================================
    # MAIN MESSAGE PROCESSING
    # =========================================================================
    
    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Process user message using all 6 data structures.
        
        Flow:
        1. Normalize intent (Union-Find)
        2. Check FAQ (HashMap)
        3. Navigate conversation (Decision Tree)
        4. Track history (Stack)
        5. Suggest next actions (Weighted Graph)
        """
        message = message.strip()
        if not message:
            return self._create_response(
                "Please enter a message.",
                "Input Validation",
                "None"
            )
        
        stack = self._get_user_stack(user_id)
        data_structures_used = []
        
        # Check for "go back" command - uses STACK
        if message.lower() in ["back", "go back", "previous", "undo"]:
            if stack.size() > 1:
                stack.pop()  # Remove current state
                prev_state = stack.peek()
                if prev_state:
                    self._decision_tree.set_state(user_id, prev_state["node_id"])
                    current_state = prev_state["node_id"]
                    current_node = self._decision_tree.nodes.get(current_state)
                    
                    # Get next action suggestions
                    next_actions = self.get_next_actions(current_state)
                    
                    return self._create_response(
                        f"Going back...\n\n{current_node.message}",
                        "Navigation",
                        "Stack",
                        node_id=current_state,
                        stack_size=stack.size(),
                        next_actions=next_actions["suggestions"]
                    )
            else:
                # Reset to root
                self._decision_tree.reset(user_id)
                stack.clear()
                root_node = self._decision_tree.nodes.get("root")
                stack.push("root", root_node.message[:50])
                
                return self._create_response(
                    f"Returning to main menu...\n\n{root_node.message}",
                    "Navigation",
                    "Stack",
                    node_id="root",
                    stack_size=1
                )
        
        # DS 5: Normalize intent using Union-Find
        intent_result = self.normalize_intent(message)
        normalized_message = intent_result["canonical"]
        if intent_result["normalized"]:
            data_structures_used.append("Union-Find")
        
        # DS 2: Check FAQ HashMap first
        faq_result = self._faq_map.lookup(normalized_message)
        if faq_result:
            data_structures_used.append("HashMap")
            
            # Still get current state for suggestions
            current_state = self._decision_tree.get_current_state(user_id)
            next_actions = self.get_next_actions(current_state)
            
            return self._create_response(
                faq_result["response"],
                "FAQ Lookup",
                ", ".join(data_structures_used) if data_structures_used else "HashMap",
                matched_keyword=faq_result.get("matched_keyword"),
                category=faq_result.get("category"),
                next_actions=next_actions["suggestions"]
            )
        
        # DS 3: Navigate Decision Tree
        tree_result = self._decision_tree.get_response(user_id, normalized_message)
        data_structures_used.append("Decision Tree")
        
        # DS 4: Push to Stack
        stack.push(tree_result["node_id"], tree_result["response"][:50])
        data_structures_used.append("Stack")
        
        # DS 6: Get next action suggestions from Weighted Graph
        next_actions = self.get_next_actions(tree_result["node_id"])
        data_structures_used.append("Weighted Graph")
        
        response_text = tree_result["response"]
        
        # Add suggestions if available
        if next_actions["suggestions"] and not tree_result.get("no_match"):
            response_text += "\n\n**Quick Actions:**"
            for i, action in enumerate(next_actions["suggestions"][:3], 1):
                response_text += f"\n{i}. {action['label']}"
        
        return self._create_response(
            response_text,
            "Conversation Flow",
            ", ".join(data_structures_used),
            node_id=tree_result["node_id"],
            available_options=tree_result.get("available_options", []),
            stack_size=stack.size(),
            next_actions=next_actions["suggestions"],
            intent_normalized=intent_result["normalized"]
        )
    
    def _create_response(self, response: str, module: str, 
                        data_structure: str, **kwargs) -> Dict[str, Any]:
        """Create standardized response."""
        result = {
            "response": response,
            "module": module,
            "data_structure": data_structure,
            "success": True
        }
        result.update(kwargs)
        return result
    
    def reset_conversation(self, user_id: str) -> Dict[str, Any]:
        """Reset conversation for user."""
        self._decision_tree.reset(user_id)
        stack = self._get_user_stack(user_id)
        stack.clear()
        
        root_node = self._decision_tree.nodes.get("root")
        stack.push("root", "Welcome")
        
        return {
            "success": True,
            "message": "Conversation reset.",
            "data_structure": "Stack, Decision Tree"
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            "trie_words": self._trie.get_word_count(),
            "faq_entries": self._faq_map.size(),
            "tree_nodes": len(self._decision_tree.nodes),
            "active_sessions": len(self._user_stacks),
            "data_structures": [
                "Trie", "HashMap", "Decision Tree", 
                "Stack", "Union-Find", "Weighted Graph"
            ]
        }


# Global engine instance
_engine_instance = None


def get_engine() -> SupportEngine:
    """Get or create global engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SupportEngine()
    return _engine_instance
