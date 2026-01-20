"""
Support Engine - Main Orchestrator for the Customer Support System

This module coordinates all 7 data structures:
1. Trie - Auto-complete suggestions
2. HashMap - O(1) FAQ lookups
3. Decision Tree - Conversation flow with branching
4. Stack - "Go back" navigation
5. Union-Find - Synonym intent grouping
6. Weighted Graph - Next best action suggestions
7. OrderDatabase - O(1) order lookup

Author: Customer Support System
"""

from typing import Dict, Any, List, Optional
import re
from backend.data_structures import (
    Trie,
    FAQHashMap,
    DecisionTree,
    ConversationStack,
    UnionFind,
    WeightedGraph,
    OrderDatabase,
    UserProfile,
    ShoppingCart,
    Wishlist
)


class SupportEngine:
    """
    Main orchestrator for the customer support system.
    
    Coordinates all 7 data structures to provide intelligent responses.
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
        
        # DS 7: OrderDatabase for order lookup
        self._order_db = OrderDatabase()
        
        # DS 8-10: New E-Commerce Features (per-user)
        self._user_profiles: Dict[str, UserProfile] = {}
        self._user_carts: Dict[str, ShoppingCart] = {}
        self._user_wishlists: Dict[str, Wishlist] = {}
        
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
    
    def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create profile for user. Uses HashMap for O(1) lookup."""
        if user_id not in self._user_profiles:
            self._user_profiles[user_id] = UserProfile(user_id)
        return self._user_profiles[user_id]
    
    def _get_user_cart(self, user_id: str) -> ShoppingCart:
        """Get or create cart for user. Uses HashMap for O(1) lookup."""
        if user_id not in self._user_carts:
            self._user_carts[user_id] = ShoppingCart()
        return self._user_carts[user_id]
    
    def _get_user_wishlist(self, user_id: str) -> Wishlist:
        """Get or create wishlist for user. Uses HashMap for O(1) lookup."""
        if user_id not in self._user_wishlists:
            self._user_wishlists[user_id] = Wishlist()
        return self._user_wishlists[user_id]
    
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
            
            # E-Commerce Features
            "cart", "shopping cart", "add to cart", "view cart",
            "wishlist", "add to wishlist", "my wishlist",
            "profile", "my profile", "view profile",
            "order history", "recent orders", "past orders",
            "undo", "checkout",
            
            # Products for cart/wishlist
            "headphones", "wireless headphones", "phone case",
            "laptop stand", "usb hub", "webcam", "keyboard",
            "gaming mouse", "monitor light", "desk mat",
            
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
                "keywords": ["shipping time", "delivery time", "how long shipping"],
                "response": "Standard shipping: 5-7 business days (free over $50)\nExpress shipping: 2-3 business days ($9.99)\nOvernight: Next business day ($19.99)",
                "category": "shipping"
            },
            {
                "keywords": ["return policy info", "return window", "how to return"],
                "response": "We offer a 30-day return policy for unused items in original packaging. Refunds are processed within 5-7 business days after we receive the item.",
                "category": "returns"
            },
            {
                "keywords": ["contact info", "support email", "customer service"],
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
                "keywords": ["tracking number", "track package", "where is my order", "track my package"],
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
            "- Cart: View or manage shopping cart\n"
            "- Wishlist: View saved items\n"
            "- Profile: View your profile\n"
            "- Returns: Return items or request refunds\n"
            "- Products: Browse products & pricing\n"
            "- Contact: Speak to a human agent",
            options={
                "order": "orders_menu",
                "orders": "orders_menu",
                "cart": "cart_menu",
                "shopping": "cart_menu",
                "wishlist": "wishlist_menu",
                "wish": "wishlist_menu",
                "profile": "profile_menu",
                "my profile": "profile_menu",
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
            "**Navigation:**\n"
            "- Type 'back' → Orders menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "orders_menu", "orders": "orders_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
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
            "**Navigation:**\n"
            "- Type 'back' → Orders menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "orders_menu", "orders": "orders_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
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
            "**Navigation:**\n"
            "- Type 'back' → Orders menu\n"
            "- Type 'menu' → Main menu\n"
            "- Type 'chat' → Live agent",
            options={"back": "orders_menu", "orders": "orders_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
            is_leaf=True
        )
        
        # ===== SHOPPING CART MENU (HashMap + Stack) =====
        tree.add_node(
            "cart_menu",
            "**Shopping Cart** 🛒\n\n"
            "Your cart uses HashMap for O(1) item lookup!\n\n"
            "Available actions:\n"
            "- View: See cart contents\n"
            "- Add: Add a product (e.g., 'add headphones')\n"
            "- Remove: Remove an item\n"
            "- Undo: Reverse last action (Stack!)\n"
            "- Products: See available products\n"
            "- Back: Return to main menu",
            options={
                "view": "cart_view",
                "see": "cart_view",
                "add": "cart_add",
                "remove": "cart_remove",
                "delete": "cart_remove",
                "products": "cart_products",
                "catalog": "cart_products",
                "back": "root",
                "menu": "root"
            }
        )
        
        tree.add_node(
            "cart_view",
            "**View Cart**\n\n"
            "Type 'show cart' to see your current cart contents.\n\n"
            "**Navigation:**\n"
            "- Type 'add [product]' → Add item\n"
            "- Type 'undo' → Undo last action\n"
            "- Type 'back' → Cart menu",
            options={"back": "cart_menu", "cart": "cart_menu", "menu": "root", "add": "cart_add"},
            is_leaf=True
        )
        
        tree.add_node(
            "cart_add",
            "**Add to Cart**\n\n"
            "Type the product name to add:\n"
            "- Wireless Headphones ($79.99)\n"
            "- Phone Case ($19.99)\n"
            "- Laptop Stand ($49.99)\n"
            "- Gaming Mouse ($59.99)\n"
            "- Mechanical Keyboard ($129.99)\n\n"
            "Example: 'add headphones'\n\n"
            "**Navigation:**\n"
            "- Type 'back' → Cart menu",
            options={"back": "cart_menu", "cart": "cart_menu", "menu": "root", "view": "cart_view"},
            is_leaf=True
        )
        
        tree.add_node(
            "cart_remove",
            "**Remove from Cart**\n\n"
            "Type 'remove [product name]' to remove an item.\n"
            "Or 'view' to see your cart first.\n\n"
            "**Navigation:**\n"
            "- Type 'back' → Cart menu",
            options={"back": "cart_menu", "cart": "cart_menu", "menu": "root", "view": "cart_view"},
            is_leaf=True
        )
        
        tree.add_node(
            "cart_products",
            "**Available Products**\n\n"
            "Browse our catalog:\n"
            "1. Wireless Headphones - $79.99\n"
            "2. Phone Case - $19.99\n"
            "3. Laptop Stand - $49.99\n"
            "4. USB-C Hub - $39.99\n"
            "5. Webcam HD - $69.99\n"
            "6. Mechanical Keyboard - $129.99\n"
            "7. Gaming Mouse - $59.99\n"
            "8. Monitor Light Bar - $45.99\n"
            "9. Desk Mat - $24.99\n"
            "10. Cable Management Kit - $15.99\n\n"
            "Say 'add [product]' to add to cart!",
            options={"back": "cart_menu", "cart": "cart_menu", "menu": "root", "add": "cart_add"},
            is_leaf=True
        )
        
        # ===== WISHLIST MENU (HashMap) =====
        tree.add_node(
            "wishlist_menu",
            "**Wishlist** ❤️\n\n"
            "Your wishlist uses HashMap for O(1) lookups!\n\n"
            "Available actions:\n"
            "- View: See wishlist items\n"
            "- Add: Save a product for later\n"
            "- Remove: Remove from wishlist\n"
            "- Move: Move item to cart\n"
            "- Back: Return to main menu",
            options={
                "view": "wishlist_view",
                "see": "wishlist_view",
                "add": "wishlist_add",
                "save": "wishlist_add",
                "remove": "wishlist_remove",
                "move": "wishlist_move",
                "back": "root",
                "menu": "root"
            }
        )
        
        tree.add_node(
            "wishlist_view",
            "**View Wishlist**\n\n"
            "Type 'show wishlist' to see your saved items.\n\n"
            "**Navigation:**\n"
            "- Type 'add [product]' → Save item\n"
            "- Type 'move [product]' → Move to cart\n"
            "- Type 'back' → Wishlist menu",
            options={"back": "wishlist_menu", "wishlist": "wishlist_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "wishlist_add",
            "**Add to Wishlist**\n\n"
            "Type 'wishlist [product name]' to save for later.\n\n"
            "Example: 'wishlist headphones'\n\n"
            "**Navigation:**\n"
            "- Type 'back' → Wishlist menu",
            options={"back": "wishlist_menu", "wishlist": "wishlist_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "wishlist_remove",
            "**Remove from Wishlist**\n\n"
            "Type 'remove [product]' to remove from wishlist.\n\n"
            "**Navigation:**\n"
            "- Type 'back' → Wishlist menu",
            options={"back": "wishlist_menu", "wishlist": "wishlist_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "wishlist_move",
            "**Move to Cart**\n\n"
            "Type 'move [product]' to add to cart from wishlist.\n\n"
            "**Navigation:**\n"
            "- Type 'back' → Wishlist menu",
            options={"back": "wishlist_menu", "wishlist": "wishlist_menu", "menu": "root"},
            is_leaf=True
        )
        
        # ===== PROFILE MENU (HashMap + Stack) =====
        tree.add_node(
            "profile_menu",
            "**Your Profile** 👤\n\n"
            "Profile uses HashMap for O(1) field access\n"
            "and Stack for navigation history!\n\n"
            "Options:\n"
            "- View: See your profile\n"
            "- Addresses: View saved addresses\n"
            "- Payment: View payment methods\n"
            "- Orders: View order history\n"
            "- Back: Return to main menu",
            options={
                "view": "profile_view",
                "see": "profile_view",
                "address": "profile_addresses",
                "addresses": "profile_addresses",
                "payment": "profile_payment",
                "payments": "profile_payment",
                "orders": "profile_orders",
                "history": "profile_orders",
                "back": "root",
                "menu": "root"
            }
        )
        
        tree.add_node(
            "profile_view",
            "**View Profile**\n\n"
            "Type 'show profile' to see your full profile.\n\n"
            "**Navigation:**\n"
            "- Type 'addresses' → View addresses\n"
            "- Type 'payment' → View payment methods\n"
            "- Type 'back' → Profile menu",
            options={"back": "profile_menu", "profile": "profile_menu", "menu": "root", "addresses": "profile_addresses", "payment": "profile_payment"},
            is_leaf=True
        )
        
        tree.add_node(
            "profile_addresses",
            "**Saved Addresses**\n\n"
            "Type 'show addresses' to see your addresses.\n\n"
            "**Navigation:**\n"
            "- Type 'back' → Profile menu",
            options={"back": "profile_menu", "profile": "profile_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "profile_payment",
            "**Payment Methods**\n\n"
            "Type 'show payment' to see your saved cards.\n\n"
            "**Navigation:**\n"
            "- Type 'back' → Profile menu",
            options={"back": "profile_menu", "profile": "profile_menu", "menu": "root"},
            is_leaf=True
        )
        
        tree.add_node(
            "profile_orders",
            "**Order History**\n\n"
            "Your recent orders:\n"
            "- ORD-12345: Shipped\n"
            "- ORD-67890: Processing\n"
            "- ORD-11111: Delivered\n"
            "- ORD-22222: Out for Delivery\n"
            "- ORD-33333: Cancelled\n\n"
            "Type an Order ID to see details!\n\n"
            "**Navigation:**\n"
            "- Type 'back' → Profile menu",
            options={"back": "profile_menu", "profile": "profile_menu", "menu": "root", "orders": "orders_menu"},
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
            "**Navigation:**\n"
            "- Type 'back' → Returns menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "returns_menu", "returns": "returns_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
            is_leaf=True
        )
        
        tree.add_node(
            "return_status",
            "**Return Status**\n\n"
            "Enter your Return ID (e.g., RET-12345) to check:\n"
            "- Return shipment status\n"
            "- Refund processing status\n"
            "- Expected refund date\n\n"
            "**Navigation:**\n"
            "- Type 'back' → Returns menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "returns_menu", "returns": "returns_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
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
            "**Navigation:**\n"
            "- Type 'back' → Returns menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "returns_menu", "returns": "returns_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
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
            "**Navigation:**\n"
            "- Type 'back' → Account menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "account_menu", "account": "account_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
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
            "**Navigation:**\n"
            "- Type 'back' → Account menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "account_menu", "account": "account_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
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
            "**Navigation:**\n"
            "- Type 'back' → Account menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "account_menu", "account": "account_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
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
            "**Navigation:**\n"
            "- Type 'back' → Products menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "products_menu", "products": "products_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
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
            "**Navigation:**\n"
            "- Type 'back' → Products menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "products_menu", "products": "products_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
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
            "**Navigation:**\n"
            "- Type 'back' → Products menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "products_menu", "products": "products_menu", "menu": "root", "chat": "contact_chat", "agent": "contact_chat"},
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
            "**Navigation:**\n"
            "- Type 'back' → Contact menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "contact_menu", "contact": "contact_menu", "menu": "root"},
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
            "**Navigation:**\n"
            "- Type 'back' → Contact menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "contact_menu", "contact": "contact_menu", "menu": "root"},
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
            "**Navigation:**\n"
            "- Type 'back' → Contact menu\n"
            "- Type 'menu' → Main menu",
            options={"back": "contact_menu", "contact": "contact_menu", "menu": "root"},
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
        
        # ===== ROOT / MAIN MENU =====
        g.add_node("root", "Main Menu")
        g.add_edge("root", "orders_menu", 0.35, "Check Orders")
        g.add_edge("root", "returns_menu", 0.25, "Returns & Refunds")
        g.add_edge("root", "account_menu", 0.20, "Account Help")
        g.add_edge("root", "products_menu", 0.12, "Products & Pricing")
        g.add_edge("root", "contact_menu", 0.08, "Contact Support")
        
        # ===== ORDERS MENU =====
        g.add_node("orders_menu", "Orders")
        g.add_edge("orders_menu", "order_track", 0.50, "Track Order")
        g.add_edge("orders_menu", "order_cancel", 0.30, "Cancel Order")
        g.add_edge("orders_menu", "order_modify", 0.15, "Modify Order")
        g.add_edge("orders_menu", "root", 0.05, "Back to Menu")
        
        # Order Track
        g.add_node("order_track", "Track Order")
        g.add_edge("order_track", "contact_chat", 0.40, "Chat with Agent")
        g.add_edge("order_track", "order_cancel", 0.30, "Cancel Order")
        g.add_edge("order_track", "orders_menu", 0.30, "Back to Orders")
        
        # Order Cancel
        g.add_node("order_cancel", "Cancel Order")
        g.add_edge("order_cancel", "return_start", 0.40, "Start Return")
        g.add_edge("order_cancel", "contact_chat", 0.35, "Chat with Agent")
        g.add_edge("order_cancel", "orders_menu", 0.25, "Back to Orders")
        
        # Order Modify
        g.add_node("order_modify", "Modify Order")
        g.add_edge("order_modify", "contact_chat", 0.45, "Chat with Agent")
        g.add_edge("order_modify", "order_track", 0.30, "Track Order")
        g.add_edge("order_modify", "orders_menu", 0.25, "Back to Orders")
        
        # ===== RETURNS MENU =====
        g.add_node("returns_menu", "Returns")
        g.add_edge("returns_menu", "return_start", 0.45, "Start Return")
        g.add_edge("returns_menu", "return_status", 0.30, "Check Status")
        g.add_edge("returns_menu", "return_policy", 0.15, "View Policy")
        g.add_edge("returns_menu", "root", 0.10, "Back to Menu")
        
        # Return Start
        g.add_node("return_start", "Start Return")
        g.add_edge("return_start", "return_status", 0.40, "Check Status")
        g.add_edge("return_start", "contact_chat", 0.35, "Chat with Agent")
        g.add_edge("return_start", "returns_menu", 0.25, "Back to Returns")
        
        # Return Status
        g.add_node("return_status", "Return Status")
        g.add_edge("return_status", "contact_chat", 0.50, "Chat with Agent")
        g.add_edge("return_status", "return_policy", 0.25, "View Policy")
        g.add_edge("return_status", "returns_menu", 0.25, "Back to Returns")
        
        # Return Policy
        g.add_node("return_policy", "Return Policy")
        g.add_edge("return_policy", "return_start", 0.50, "Start Return")
        g.add_edge("return_policy", "contact_chat", 0.25, "Chat with Agent")
        g.add_edge("return_policy", "returns_menu", 0.25, "Back to Returns")
        
        # ===== ACCOUNT MENU =====
        g.add_node("account_menu", "Account")
        g.add_edge("account_menu", "account_password", 0.40, "Reset Password")
        g.add_edge("account_menu", "account_profile", 0.30, "Update Profile")
        g.add_edge("account_menu", "account_orders", 0.20, "Order History")
        g.add_edge("account_menu", "root", 0.10, "Back to Menu")
        
        # Account Password
        g.add_node("account_password", "Password Reset")
        g.add_edge("account_password", "contact_chat", 0.45, "Chat with Agent")
        g.add_edge("account_password", "account_profile", 0.30, "Update Profile")
        g.add_edge("account_password", "account_menu", 0.25, "Back to Account")
        
        # Account Profile
        g.add_node("account_profile", "Update Profile")
        g.add_edge("account_profile", "account_password", 0.35, "Reset Password")
        g.add_edge("account_profile", "account_orders", 0.35, "Order History")
        g.add_edge("account_profile", "account_menu", 0.30, "Back to Account")
        
        # Account Orders
        g.add_node("account_orders", "Order History")
        g.add_edge("account_orders", "orders_menu", 0.45, "Manage Orders")
        g.add_edge("account_orders", "return_start", 0.30, "Start Return")
        g.add_edge("account_orders", "account_menu", 0.25, "Back to Account")
        
        # ===== PRODUCTS MENU =====
        g.add_node("products_menu", "Products")
        g.add_edge("products_menu", "products_pricing", 0.40, "View Pricing")
        g.add_edge("products_menu", "products_deals", 0.35, "Current Deals")
        g.add_edge("products_menu", "products_stock", 0.15, "Check Stock")
        g.add_edge("products_menu", "root", 0.10, "Back to Menu")
        
        # Products Pricing
        g.add_node("products_pricing", "Pricing")
        g.add_edge("products_pricing", "products_deals", 0.45, "Current Deals")
        g.add_edge("products_pricing", "products_stock", 0.30, "Check Stock")
        g.add_edge("products_pricing", "products_menu", 0.25, "Back to Products")
        
        # Products Stock
        g.add_node("products_stock", "Stock")
        g.add_edge("products_stock", "products_pricing", 0.40, "View Pricing")
        g.add_edge("products_stock", "contact_chat", 0.35, "Chat with Agent")
        g.add_edge("products_stock", "products_menu", 0.25, "Back to Products")
        
        # Products Deals
        g.add_node("products_deals", "Deals")
        g.add_edge("products_deals", "products_pricing", 0.40, "View Pricing")
        g.add_edge("products_deals", "orders_menu", 0.35, "Place Order")
        g.add_edge("products_deals", "products_menu", 0.25, "Back to Products")
        
        # ===== CONTACT MENU =====
        g.add_node("contact_menu", "Contact")
        g.add_edge("contact_menu", "contact_chat", 0.50, "Live Chat")
        g.add_edge("contact_menu", "contact_phone", 0.30, "Call Us")
        g.add_edge("contact_menu", "contact_email", 0.15, "Email Us")
        g.add_edge("contact_menu", "root", 0.05, "Back to Menu")
        
        # Contact Phone
        g.add_node("contact_phone", "Phone Support")
        g.add_edge("contact_phone", "contact_chat", 0.50, "Live Chat")
        g.add_edge("contact_phone", "contact_email", 0.30, "Email Us")
        g.add_edge("contact_phone", "contact_menu", 0.20, "Back to Contact")
        
        # Contact Email
        g.add_node("contact_email", "Email Support")
        g.add_edge("contact_email", "contact_chat", 0.50, "Live Chat")
        g.add_edge("contact_email", "contact_phone", 0.30, "Call Us")
        g.add_edge("contact_email", "contact_menu", 0.20, "Back to Contact")
        
        # Contact Chat
        g.add_node("contact_chat", "Live Chat")
        g.add_edge("contact_chat", "root", 0.50, "Back to Menu")
        g.add_edge("contact_chat", "orders_menu", 0.30, "Check Orders")
        g.add_edge("contact_chat", "returns_menu", 0.20, "Returns")
    
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
    
    def _get_completion_nav_actions(self, current_state: str) -> List[Dict[str, Any]]:
        """
        Get navigation actions after completing an action (like viewing order details).
        Shows options to go back to parent menu or main menu.
        """
        # Map leaf nodes to their parent menus
        parent_map = {
            # Orders
            "order_track": ("orders_menu", "Orders Menu"),
            "order_cancel": ("orders_menu", "Orders Menu"),
            "order_modify": ("orders_menu", "Orders Menu"),
            # Returns
            "return_start": ("returns_menu", "Returns Menu"),
            "return_status": ("returns_menu", "Returns Menu"),
            "return_policy": ("returns_menu", "Returns Menu"),
            # Account
            "account_password": ("account_menu", "Account Menu"),
            "account_profile": ("account_menu", "Account Menu"),
            "account_orders": ("account_menu", "Account Menu"),
            # Products
            "products_pricing": ("products_menu", "Products Menu"),
            "products_stock": ("products_menu", "Products Menu"),
            "products_deals": ("products_menu", "Products Menu"),
            # Contact
            "contact_phone": ("contact_menu", "Contact Menu"),
            "contact_email": ("contact_menu", "Contact Menu"),
            "contact_chat": ("contact_menu", "Contact Menu"),
            # Cart
            "cart_view": ("cart_menu", "Cart Menu"),
            "cart_add": ("cart_menu", "Cart Menu"),
            "cart_remove": ("cart_menu", "Cart Menu"),
            "cart_products": ("cart_menu", "Cart Menu"),
            # Wishlist
            "wishlist_view": ("wishlist_menu", "Wishlist Menu"),
            "wishlist_add": ("wishlist_menu", "Wishlist Menu"),
            "wishlist_remove": ("wishlist_menu", "Wishlist Menu"),
            "wishlist_move": ("wishlist_menu", "Wishlist Menu"),
            # Profile
            "profile_view": ("profile_menu", "Profile Menu"),
            "profile_addresses": ("profile_menu", "Profile Menu"),
            "profile_payment": ("profile_menu", "Profile Menu"),
            "profile_orders": ("profile_menu", "Profile Menu"),
        }
        
        nav_actions = []
        
        # Add "Back to Parent" option
        if current_state in parent_map:
            parent_id, parent_name = parent_map[current_state]
            nav_actions.append({
                "action": parent_id,
                "label": f"Back to {parent_name.split()[0]}",
                "weight": 0.45
            })
        
        # Add "Main Menu" option
        nav_actions.append({
            "action": "root",
            "label": "Main Menu",
            "weight": 0.35
        })
        
        # Add "Chat with Agent" option
        nav_actions.append({
            "action": "contact_chat",
            "label": "Chat with Agent",
            "weight": 0.20
        })
        
        return nav_actions
    
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
        6. Check for Order ID (OrderDatabase)
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
        
        # Get current state for context-aware lookups
        current_state = self._decision_tree.get_current_state(user_id)
        
        # DS 7: Check for tracking number first (if at order_track node)
        if current_state == "order_track":
            tracking_number = self._check_for_tracking_number(message)
            if tracking_number:
                tracking_result = self.lookup_tracking(tracking_number)
                data_structures_used.append("OrderDatabase")
                
                # Show navigation options after completing action
                nav_actions = self._get_completion_nav_actions(current_state)
                
                return self._create_response(
                    tracking_result["response"],
                    "Tracking Lookup",
                    ", ".join(data_structures_used),
                    order_found=tracking_result["success"],
                    next_actions=nav_actions
                )
        
        # DS 7: Check for Order ID pattern - uses OrderDatabase (HashMap)
        order_id = self._check_for_order_id(message)
        if order_id:
            # Use context for appropriate response format
            order_result = self.lookup_order(order_id, context=current_state)
            data_structures_used.append("OrderDatabase")
            
            # Show navigation options after completing action
            nav_actions = self._get_completion_nav_actions(current_state)
            
            return self._create_response(
                order_result["response"],
                "Order Lookup",
                ", ".join(data_structures_used),
                order_found=order_result["success"],
                next_actions=nav_actions
            )
        
        # =========================================================================
        # E-COMMERCE FEATURES: Cart, Wishlist, Profile (HashMap + Stack)
        # =========================================================================
        message_lower = message.lower().strip()
        
        # ----- SHOPPING CART COMMANDS -----
        # Show cart
        if message_lower in ["show cart", "view cart", "my cart", "cart"]:
            cart = self._get_user_cart(user_id)
            return self._create_response(
                cart.format_cart(),
                "Shopping Cart",
                "HashMap + Stack",
                cart_items=cart.get_cart()["item_count"],
                next_actions=[
                    {"action": "cart_add", "label": "Add Items", "weight": 0.5},
                    {"action": "root", "label": "Main Menu", "weight": 0.3},
                    {"action": "wishlist_menu", "label": "View Wishlist", "weight": 0.2}
                ]
            )
        
        # Add to cart
        if message_lower.startswith("add "):
            product_name = message[4:].strip()
            cart = self._get_user_cart(user_id)
            # Find product by name
            product_id = None
            for pid, prod in cart.get_products().items():
                if product_name.lower() in prod["name"].lower():
                    product_id = pid
                    break
            
            if product_id:
                result = cart.add_item(product_id)
                response = result["message"] if result["success"] else result["error"]
                response += f"\n\n{cart.format_cart()}"
                return self._create_response(
                    response,
                    "Cart Add",
                    "HashMap + Stack",
                    success=result["success"],
                    next_actions=[
                        {"action": "cart_menu", "label": "Cart Menu", "weight": 0.4},
                        {"action": "cart_add", "label": "Add More", "weight": 0.35},
                        {"action": "root", "label": "Main Menu", "weight": 0.25}
                    ]
                )
            else:
                return self._create_response(
                    f"Product '{product_name}' not found.\n\nAvailable products:\n" +
                    "\n".join([f"- {p['name']}" for p in cart.get_products().values()]),
                    "Cart Add",
                    "HashMap",
                    success=False
                )
        
        # Remove from cart
        if message_lower.startswith("remove "):
            product_name = message[7:].strip()
            cart = self._get_user_cart(user_id)
            product_id = None
            for pid, prod in cart.get_products().items():
                if product_name.lower() in prod["name"].lower():
                    product_id = pid
                    break
            
            if product_id:
                result = cart.remove_item(product_id)
                response = result["message"] if result["success"] else result["error"]
                response += f"\n\n{cart.format_cart()}"
                return self._create_response(
                    response,
                    "Cart Remove",
                    "HashMap + Stack",
                    success=result["success"]
                )
        
        # Undo cart action (only in cart context or explicit undo cart)
        if message_lower == "undo" and current_state.startswith("cart"):
            cart = self._get_user_cart(user_id)
            result = cart.undo()
            response = result["message"] if result["success"] else result["error"]
            response += f"\n\n{cart.format_cart()}"
            return self._create_response(
                response,
                "Cart Undo",
                "Stack (LIFO)",
                success=result["success"]
            )
        
        # ----- WISHLIST COMMANDS -----
        # Show wishlist
        if message_lower in ["show wishlist", "view wishlist", "my wishlist"]:
            wishlist = self._get_user_wishlist(user_id)
            return self._create_response(
                wishlist.format_wishlist(),
                "Wishlist",
                "HashMap",
                wishlist_count=wishlist.size(),
                next_actions=[
                    {"action": "wishlist_add", "label": "Add Items", "weight": 0.4},
                    {"action": "cart_menu", "label": "View Cart", "weight": 0.35},
                    {"action": "root", "label": "Main Menu", "weight": 0.25}
                ]
            )
        
        # Add to wishlist
        if message_lower.startswith("wishlist ") or message_lower.startswith("save "):
            prefix_len = 9 if message_lower.startswith("wishlist ") else 5
            product_name = message[prefix_len:].strip()
            wishlist = self._get_user_wishlist(user_id)
            product_id = wishlist.find_by_name(product_name)
            
            if product_id:
                result = wishlist.add(product_id)
                response = result["message"] if result["success"] else result["error"]
                response += f"\n\n{wishlist.format_wishlist()}"
                return self._create_response(
                    response,
                    "Wishlist Add",
                    "HashMap",
                    success=result["success"]
                )
            else:
                return self._create_response(
                    f"Product '{product_name}' not found.",
                    "Wishlist Add",
                    "HashMap",
                    success=False
                )
        
        # Move from wishlist to cart
        if message_lower.startswith("move "):
            product_name = message[5:].strip()
            wishlist = self._get_user_wishlist(user_id)
            cart = self._get_user_cart(user_id)
            product_id = wishlist.find_by_name(product_name)
            
            if product_id and wishlist.contains(product_id):
                wishlist.remove(product_id)
                cart.add_item(product_id)
                return self._create_response(
                    f"Moved item to cart!\n\n{cart.format_cart()}",
                    "Move to Cart",
                    "HashMap + Stack",
                    success=True
                )
        
        # ----- PROFILE COMMANDS -----
        # Show profile
        if message_lower in ["show profile", "view profile", "my profile"]:
            profile = self._get_user_profile(user_id)
            profile.push_view("profile_summary")
            return self._create_response(
                profile.format_profile_summary(),
                "User Profile",
                "HashMap + Stack",
                next_actions=[
                    {"action": "profile_addresses", "label": "View Addresses", "weight": 0.35},
                    {"action": "profile_orders", "label": "Order History", "weight": 0.35},
                    {"action": "root", "label": "Main Menu", "weight": 0.3}
                ]
            )
        
        # Show addresses
        if message_lower in ["show addresses", "my addresses", "addresses"]:
            profile = self._get_user_profile(user_id)
            profile.push_view("addresses")
            addresses = profile.get_field("addresses")
            addr_str = "\n".join([
                f"• **{addr['type']}**: {addr['street']}, {addr['city']}, {addr['state']} {addr['zip']}"
                for addr in addresses
            ])
            return self._create_response(
                f"**Your Saved Addresses**\n\n{addr_str}",
                "Profile Addresses",
                "HashMap + Stack"
            )
        
        # Show payment methods
        if message_lower in ["show payment", "payment methods", "my cards"]:
            profile = self._get_user_profile(user_id)
            profile.push_view("payment")
            payments = profile.get_field("payment_methods")
            pay_str = "\n".join([
                f"• {pm['type']} {'••••' + pm.get('last_four', '') if pm.get('last_four') else pm.get('email', '')} {'(Default)' if pm.get('default') else ''}"
                for pm in payments
            ])
            return self._create_response(
                f"**Your Payment Methods**\n\n{pay_str}",
                "Profile Payment",
                "HashMap + Stack"
            )
        
        # =========================================================================
        # END E-COMMERCE FEATURES
        # =========================================================================
        
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
    
    # =========================================================================
    # DATA STRUCTURE 7: ORDER DATABASE - Order Lookup
    # =========================================================================
    
    def lookup_order(self, order_id: str, context: str = "general") -> Dict[str, Any]:
        """
        Look up an order by ID.
        
        DATA STRUCTURE: HashMap (O(1) lookup)
        
        Args:
            order_id: Order ID or tracking number
            context: Current context (e.g., "order_track" for tracking-focused response)
        """
        order = self._order_db.get_order(order_id)
        
        if order:
            # Use tracking-focused response if at track order node
            if context == "order_track":
                response = self._order_db.format_tracking_response(order)
            else:
                response = self._order_db.format_order_response(order)
            
            return {
                "success": True,
                "order": order,
                "response": response,
                "data_structure": "HashMap (OrderDatabase)"
            }
        else:
            # Return list of valid order IDs for demo
            valid_ids = self._order_db.get_all_order_ids()
            return {
                "success": False,
                "response": f"Order not found. Try one of these demo orders:\n" + 
                           "\n".join(f"- {oid}" for oid in valid_ids),
                "valid_order_ids": valid_ids,
                "data_structure": "HashMap (OrderDatabase)"
            }
    
    def lookup_tracking(self, tracking_number: str) -> Dict[str, Any]:
        """
        Look up an order by tracking number.
        
        DATA STRUCTURE: HashMap (O(n) lookup - scans for tracking match)
        """
        order = self._order_db.get_by_tracking(tracking_number)
        
        if order:
            return {
                "success": True,
                "order": order,
                "response": self._order_db.format_tracking_response(order),
                "data_structure": "HashMap (OrderDatabase)"
            }
        else:
            return {
                "success": False,
                "response": f"Tracking number not found: {tracking_number}\n\n"
                           "Try these demo tracking numbers:\n"
                           "- 1Z999AA10123456784 (Shipped)\n"
                           "- 1Z999AA10123456001 (Delivered)\n"
                           "- 1Z999AA10123456002 (Out for Delivery)",
                "data_structure": "HashMap (OrderDatabase)"
            }
    
    def _check_for_order_id(self, message: str) -> Optional[str]:
        """Check if message contains an order ID pattern."""
        # Pattern: ORD-XXXXX or just XXXXX (5 digits)
        patterns = [
            r'\bORD-(\d{5})\b',  # ORD-12345
            r'\bord-(\d{5})\b',  # ord-12345 (lowercase)
            r'\b(\d{5})\b',      # Just 5 digits
        ]
        
        message_upper = message.upper()
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                digits = match.group(1) if '(' in pattern else match.group(0)
                return f"ORD-{digits}" if not message_upper.startswith("ORD-") else message_upper.split()[0]
        
        # Also check for exact match with ORD prefix
        if "ORD-" in message_upper:
            parts = message_upper.split()
            for part in parts:
                if part.startswith("ORD-"):
                    return part
        
        return None
    
    def _check_for_tracking_number(self, message: str) -> Optional[str]:
        """Check if message contains a tracking number pattern."""
        # UPS-style tracking: 1Z followed by alphanumeric
        ups_pattern = r'\b1Z[A-Z0-9]{16}\b'
        match = re.search(ups_pattern, message.upper())
        if match:
            return match.group(0)
        return None
    
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
            "order_count": self._order_db.size(),
            "data_structures": [
                "Trie", "HashMap", "Decision Tree", 
                "Stack", "Union-Find", "Weighted Graph",
                "OrderDatabase"
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
