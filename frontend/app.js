/**
 * ShopDS - E-Commerce Powered by Data Structures (Simplified)
 */

const CONFIG = {
    API_BASE: '',
    USER_ID: 'user_' + Math.random().toString(36).substr(2, 9)
};

const state = {
    isLoading: false,
    cartOpen: false,
    chatOpen: false,
    checkoutStep: 1,
    recentlyViewed: [],
    cart: { items: [] },
    wishlist: new Set()
};

const PRODUCTS = [
    { id: 'PROD-001', name: 'Wireless Headphones', price: 6499, category: 'Electronics', image: 'assets/images/headphones.png' },
    { id: 'PROD-002', name: 'Phone Case', price: 1499, category: 'Accessories', image: 'assets/images/phonecase.png' },
    { id: 'PROD-003', name: 'Laptop Stand', price: 3999, category: 'Office', image: 'assets/images/laptopstand.png' },
    { id: 'PROD-004', name: 'USB-C Hub', price: 2999, category: 'Electronics', image: 'assets/images/usbhub.png' },
    { id: 'PROD-005', name: 'Webcam HD', price: 5499, category: 'Electronics', image: 'assets/images/webcam.png' },
    { id: 'PROD-006', name: 'Mechanical Keyboard', price: 9999, category: 'Electronics', image: 'assets/images/keyboard.png' }
];

const elements = {
    productList: document.getElementById('product-list'),
    recentlyViewed: document.getElementById('recently-viewed'),
    recommendationsList: document.getElementById('recommendations-list'),
    cartDrawer: document.getElementById('cart-drawer'),
    drawerOverlay: document.getElementById('drawer-overlay'),
    cartItems: document.getElementById('cart-items'),
    cartTotal: document.getElementById('cart-total'),
    cartCount: document.getElementById('cart-count'),
    wishlistCount: document.getElementById('wishlist-count'),
    chatWidget: document.getElementById('chat-widget'),
    chatToggle: document.getElementById('chat-toggle'),
    chatMessages: document.getElementById('chat-messages'),
    chatInput: document.getElementById('chat-input'),
    modalOverlay: document.getElementById('modal-overlay'),
    checkoutModal: document.getElementById('checkout-modal')
};

// Check if we're on a page with chat elements
const hasChatElements = elements.chatWidget && elements.chatInput;

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function highlightDS(name) {
    document.querySelectorAll('.ds-item').forEach(item => item.classList.remove('active'));
    if (!name) return;
    const lower = name.toLowerCase();

    // Specific Handling for Priority Queue vs Queue
    if (lower.includes('priority') || lower.includes('heap')) {
        document.getElementById('ds-pqueue')?.classList.add('active');
        return;
    }

    const dsMap = {
        'trie': 'ds-trie',
        'hashmap': 'ds-hashmap', 'hash': 'ds-hashmap',
        'decision': 'ds-tree', 'tree': 'ds-tree',
        'stack': 'ds-stack',
        'union': 'ds-unionfind',
        'graph': 'ds-graph',
        'linked': 'ds-linkedlist',
        'queue': 'ds-queue' // Matches 'queue' but not 'priority' (handled above)
    };

    for (const [key, id] of Object.entries(dsMap)) {
        if (lower.includes(key)) {
            document.getElementById(id)?.classList.add('active');
            break; // Stop after first match to prevent multiple highlights
        }
    }
}

// Products
function renderProducts() {
    elements.productList.innerHTML = PRODUCTS.map(p => `
        <div class="product-card" onclick="viewProduct('${p.id}')">
            <div class="product-image-container">
                <img src="${p.image}" alt="${escapeHtml(p.name)}" class="product-image">
            </div>
            <div class="product-card-details">
                <div class="product-text">
                    <span class="product-category">${p.category}</span>
                    <h3 class="product-name">${escapeHtml(p.name)}</h3>
                    <span class="product-price">₹${p.price.toLocaleString('en-IN')}</span>
                </div>
                <button class="add-btn-card" onclick="event.stopPropagation(); addToCart('${p.id}')">Add</button>
            </div>
             <button class="wish-btn-card ${state.wishlist.has(p.id) ? 'active' : ''}" onclick="event.stopPropagation(); toggleWishlist('${p.id}')">♡</button>
        </div>
    `).join('');
    highlightDS('HashMap');
}

function viewProduct(id) {
    const product = PRODUCTS.find(p => p.id === id);
    if (!product) return;
    state.recentlyViewed = state.recentlyViewed.filter(p => p.id !== id);
    state.recentlyViewed.unshift(product);
    if (state.recentlyViewed.length > 4) state.recentlyViewed.pop();
    renderRecentlyViewed();
    highlightDS('Linked List');
}

function renderRecentlyViewed() {
    if (state.recentlyViewed.length === 0) {
        elements.recentlyViewed.innerHTML = '<p class="empty-text">Click on products to see them here</p>';
        return;
    }
    elements.recentlyViewed.innerHTML = state.recentlyViewed.map(p => `
        <div class="recent-row">
            <span>${escapeHtml(p.name)}</span>
            <span class="product-price">₹${p.price.toLocaleString('en-IN')}</span>
        </div>
    `).join('');
}

function renderRecommendations() {
    const recs = [...PRODUCTS].map(p => ({ ...p, score: Math.floor(Math.random() * 30) + 70 }))
        .sort((a, b) => b.score - a.score).slice(0, 4);
    elements.recommendationsList.innerHTML = recs.map(p => `
        <div class="recommend-row">
            <span>${escapeHtml(p.name)} - ₹${p.price.toLocaleString('en-IN')}</span>
            <span class="score">${p.score}%</span>
        </div>
    `).join('');
    highlightDS('Priority Queue');
}

// Cart
function toggleCartDrawer() {
    state.cartOpen = !state.cartOpen;
    elements.cartDrawer.classList.toggle('open', state.cartOpen);
    elements.drawerOverlay.classList.toggle('open', state.cartOpen);
    if (state.cartOpen) highlightDS('HashMap');
}

function addToCart(id) {
    const product = PRODUCTS.find(p => p.id === id);
    if (!product) return;
    const existing = state.cart.items.find(i => i.id === id);
    if (existing) existing.quantity++;
    else state.cart.items.push({ ...product, quantity: 1 });
    updateCartUI();
    highlightDS('HashMap');
    if (!state.cartOpen) toggleCartDrawer();
}

function removeFromCart(id) {
    state.cart.items = state.cart.items.filter(i => i.id !== id);
    updateCartUI();
}

function updateQty(id, delta) {
    const item = state.cart.items.find(i => i.id === id);
    if (!item) return;
    item.quantity += delta;
    if (item.quantity <= 0) removeFromCart(id);
    else { updateCartUI(); }
}


function updateCartUI() {
    const count = state.cart.items.reduce((s, i) => s + i.quantity, 0);
    const total = state.cart.items.reduce((s, i) => s + i.price * i.quantity, 0);
    elements.cartCount.textContent = count;
    elements.cartTotal.textContent = `₹${total.toLocaleString('en-IN')}`;
    if (state.cart.items.length === 0) {
        elements.cartItems.innerHTML = '<div class="cart-empty">Cart is empty</div>';
    } else {
        elements.cartItems.innerHTML = state.cart.items.map(i => `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${escapeHtml(i.name)}</div>
                    <div class="cart-item-price">₹${i.price.toLocaleString('en-IN')}</div>
                </div>
                <div class="cart-item-qty">
                    <button class="qty-btn" onclick="updateQty('${i.id}', -1)">−</button>
                    <span>${i.quantity}</span>
                    <button class="qty-btn" onclick="updateQty('${i.id}', 1)">+</button>
                </div>
                <button class="cart-item-remove" onclick="removeFromCart('${i.id}')">Remove</button>
            </div>
        `).join('');
    }
}

// Wishlist
function toggleWishlist(id) {
    if (state.wishlist.has(id)) state.wishlist.delete(id);
    else state.wishlist.add(id);
    elements.wishlistCount.textContent = state.wishlist.size;
    renderProducts();
    highlightDS('HashMap');
}

// Checkout
function startCheckout() {
    if (state.cart.items.length === 0) return;
    state.checkoutStep = 1;
    elements.checkoutModal.classList.add('active');
    updateCheckoutUI();
    highlightDS('Queue');
}

function closeCheckoutModal(e) {
    if (e && e.target !== e.currentTarget) return;
    elements.checkoutModal.classList.remove('active');
}

function nextCheckoutStep() {
    if (state.checkoutStep < 4) { state.checkoutStep++; updateCheckoutUI(); }
    else { alert('Order placed! 🎉'); state.cart.items = []; updateCartUI(); closeCheckoutModal(); toggleCartDrawer(); }
}

function prevCheckoutStep() {
    if (state.checkoutStep > 1) { state.checkoutStep--; updateCheckoutUI(); }
}

function updateCheckoutUI() {
    const steps = ['Cart', 'Shipping', 'Payment', 'Confirm'];
    document.getElementById('checkout-steps').innerHTML = steps.map((s, i) => `
        <div class="checkout-step ${i + 1 === state.checkoutStep ? 'active' : ''} ${i + 1 < state.checkoutStep ? 'completed' : ''}">
            <div class="num">${i + 1}</div>
            <div class="label">${s}</div>
        </div>
    `).join('');
    document.getElementById('checkout-back').disabled = state.checkoutStep === 1;
    document.getElementById('checkout-next').textContent = state.checkoutStep === 4 ? 'Place Order' : 'Next';
    const content = [
        `<p>Items: ${state.cart.items.length}</p><p>Total: ₹${state.cart.items.reduce((s, i) => s + i.price * i.quantity, 0).toLocaleString('en-IN')}</p>`,
        '<p>123 Main Street, NY 10001</p>',
        '<p>Visa ending in 4242</p>',
        '<p>Ready to place your order!</p>'
    ];
    document.getElementById('checkout-content').innerHTML = content[state.checkoutStep - 1];
}

// Chat
function toggleChatWidget() {
    if (!hasChatElements) return;
    state.chatOpen = !state.chatOpen;
    elements.chatWidget.classList.toggle('open', state.chatOpen);
    elements.chatToggle?.classList.toggle('hidden', state.chatOpen);
    if (state.chatOpen) { elements.chatInput.focus(); highlightDS('Decision Tree'); }
}

function addMessage(text, isUser = false, meta = {}) {
    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    let html = `<div class="message-bubble">${text.split('\n').map(p => `<p>${escapeHtml(p)}</p>`).join('')}</div>`;
    if (!isUser && meta.next_actions?.length) {
        html += `<div class="quick-actions">${meta.next_actions.map(a => `<button onclick="sendMessage('${a.label.split(' ')[0].toLowerCase()}')">${a.label}</button>`).join('')}</div>`;
    }
    div.innerHTML = html;
    elements.chatMessages.appendChild(div);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    if (!isUser && meta.data_structure) highlightDS(meta.data_structure);
}

async function sendMessage(msg) {
    if (!hasChatElements) return;
    const text = msg || elements.chatInput.value.trim();
    if (state.isLoading || !text) return;
    state.isLoading = true;
    addMessage(text, true);
    elements.chatInput.value = '';

    // Typing indicator
    const typing = document.createElement('div');
    typing.className = 'message bot-message';
    typing.id = 'typing';
    typing.innerHTML = '<div class="message-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>';
    elements.chatMessages.appendChild(typing);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;

    try {
        const res = await fetch('/api/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, user_id: CONFIG.USER_ID })
        });
        const data = await res.json();
        document.getElementById('typing')?.remove();
        addMessage(data.response, false, { data_structure: data.data_structure, next_actions: data.next_actions || [] });
    } catch (e) {
        document.getElementById('typing')?.remove();
        addMessage('Sorry, an error occurred.', false);
    }
    state.isLoading = false;
}

// Modals
function openModal(type) {
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');
    let content = '';

    if (type === 'profile') {
        title.textContent = 'My Profile';
        content = `<div class="modal-ds-badge">HashMap</div>
            <div class="profile-field"><label>Name</label><div class="value">Aarush</div></div>
            <div class="profile-field"><label>Email</label><div class="value">aarushluthra@rvce.edu.in</div></div>`;
        highlightDS('HashMap');
    } else if (type === 'orders') {
        title.textContent = 'Order History';
        content = `<div class="modal-ds-badge">HashMap O(1)</div>
            <div class="order-item"><span class="order-id">ORD-12345</span> <span class="order-status shipped">Shipped</span><br><small>Wireless Headphones • ₹6,499</small></div>
            <div class="order-item"><span class="order-id">ORD-67890</span> <span class="order-status processing">Processing</span><br><small>Gaming Mouse • ₹4,999</small></div>
            <div class="order-item"><span class="order-id">ORD-11111</span> <span class="order-status delivered">Delivered</span><br><small>Keyboard • ₹9,999</small></div>`;
        highlightDS('HashMap');
    } else if (type === 'wishlist') {
        title.textContent = 'My Wishlist';
        const items = PRODUCTS.filter(p => state.wishlist.has(p.id));
        content = `<div class="modal-ds-badge">HashMap O(1)</div>` +
            (items.length ? items.map(i => `<div class="wishlist-item">${i.name} - ₹${i.price.toLocaleString('en-IN')} <button onclick="addToCart('${i.id}');closeModal()" style="float:right;padding:4px 8px;border:1px solid #ddd;border-radius:4px;cursor:pointer">Add to Cart</button></div>`).join('') : '<p class="empty-text">Wishlist is empty</p>');
        highlightDS('HashMap');
    }

    body.innerHTML = content;
    elements.modalOverlay.classList.add('active');
}

function closeModal(e) {
    if (e && e.target !== e.currentTarget) return;
    elements.modalOverlay.classList.remove('active');
}

// Event listeners
if (hasChatElements) {
    elements.chatInput.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); sendMessage(); } });
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') { closeModal(); closeCheckoutModal(); } });

// Init
function init() {
    console.log('ShopDS initialized');
    renderProducts();
    renderRecentlyViewed();
    renderRecommendations();
    updateCartUI();
}

document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', init) : init();
