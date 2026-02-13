from flask import Flask, request, render_template_string, redirect, jsonify
import pymysql
import json
from datetime import datetime

app = Flask(__name__)

# Product database with more details
PRODUCTS = [
    {
        "id": 1,
        "name": "MacBook Pro 16\"",
        "description": "Apple M3 Max, 64GB RAM, 2TB SSD",
        "price": 3499.99,
        "category": "Laptops",
        "rating": 4.8,
        "reviews": 1243,
        "image": "💻",
        "in_stock": True,
        "discount": 10
    },
    {
        "id": 2,
        "name": "Sony WH-1000XM5",
        "description": "Noise Cancelling Wireless Headphones",
        "price": 399.99,
        "category": "Audio",
        "rating": 4.7,
        "reviews": 892,
        "image": "🎧",
        "in_stock": True,
        "discount": 15
    },
    {
        "id": 3,
        "name": "Apple Watch Series 9",
        "description": "GPS + Cellular, 45mm Midnight Aluminum",
        "price": 529.99,
        "category": "Wearables",
        "rating": 4.6,
        "reviews": 1567,
        "image": "⌚",
        "in_stock": True,
        "discount": 0
    },
    {
        "id": 4,
        "name": "Logitech MX Master 3S",
        "description": "Wireless Performance Mouse for Mac",
        "price": 99.99,
        "category": "Accessories",
        "rating": 4.5,
        "reviews": 2341,
        "image": "🖱️",
        "in_stock": True,
        "discount": 20
    },
    {
        "id": 5,
        "name": "Keychron K8 Pro",
        "description": "Mechanical Keyboard with RGB Backlight",
        "price": 119.99,
        "category": "Accessories",
        "rating": 4.4,
        "reviews": 876,
        "image": "⌨️",
        "in_stock": False,
        "discount": 25
    },
    {
        "id": 6,
        "name": "Samsung 4K Monitor",
        "description": "32\" 4K UHD Gaming Monitor, 144Hz",
        "price": 649.99,
        "category": "Monitors",
        "rating": 4.3,
        "reviews": 432,
        "image": "🖥️",
        "in_stock": True,
        "discount": 30
    }
]

# Database connection remains the same
def conn():
    return pymysql.connect(
        host="mysql-cart",
        user="root",
        password="password",
        database="cartdb"
    )

# Enhanced Product Catalog Template
PRODUCT_CATALOG_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Products - Kastro Store</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: #f8f9fa;
            color: #333;
        }
        
        .navbar {
            background: white;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
            padding: 1rem 5%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.5rem;
            font-weight: 700;
            color: #4a5568;
            text-decoration: none;
        }
        
        .cart-indicator {
            position: relative;
        }
        
        .cart-count {
            position: absolute;
            top: -8px;
            right: -8px;
            background: #ff6b6b;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem 5%;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .header h1 {
            font-size: 2.5rem;
            color: #2d3748;
            margin-bottom: 1rem;
        }
        
        .header p {
            color: #4a5568;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .filters {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .filter-group {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 0.5rem 1.5rem;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
        }
        
        .filter-btn.active {
            background: #667eea;
            border-color: #667eea;
            color: white;
        }
        
        .search-box {
            flex: 1;
            max-width: 400px;
            position: relative;
        }
        
        .search-box input {
            width: 100%;
            padding: 0.8rem 1rem 0.8rem 3rem;
            border: 2px solid #e2e8f0;
            border-radius: 25px;
            font-size: 1rem;
        }
        
        .search-box i {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: #a0aec0;
        }
        
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .product-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s;
            position: relative;
        }
        
        .product-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }
        
        .product-image {
            height: 200px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 4rem;
            color: white;
        }
        
        .product-badge {
            position: absolute;
            top: 15px;
            right: 15px;
            background: #ff6b6b;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .product-content {
            padding: 1.5rem;
        }
        
        .product-category {
            color: #667eea;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: block;
        }
        
        .product-title {
            font-size: 1.2rem;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }
        
        .product-description {
            color: #4a5568;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            line-height: 1.5;
        }
        
        .product-rating {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .stars {
            color: #ffd700;
        }
        
        .rating-count {
            color: #a0aec0;
            font-size: 0.9rem;
        }
        
        .product-price {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .current-price {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2d3748;
        }
        
        .original-price {
            font-size: 1rem;
            color: #a0aec0;
            text-decoration: line-through;
        }
        
        .discount {
            color: #4CAF50;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .product-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .btn-add-to-cart {
            flex: 1;
            padding: 0.8rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .btn-add-to-cart:hover {
            background: #5a67d8;
        }
        
        .btn-wishlist {
            width: 45px;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .btn-wishlist:hover {
            border-color: #ff6b6b;
            color: #ff6b6b;
        }
        
        .out-of-stock {
            background: #e2e8f0;
            color: #a0aec0;
            cursor: not-allowed;
        }
        
        .notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 1rem;
            transform: translateX(150%);
            transition: transform 0.3s;
            z-index: 1001;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification-icon {
            width: 40px;
            height: 40px;
            background: #4CAF50;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.2rem;
        }
        
        .cart-summary {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-top: 3rem;
        }
        
        .cart-summary h2 {
            margin-bottom: 1.5rem;
            color: #2d3748;
        }
        
        .summary-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .summary-total {
            display: flex;
            justify-content: space-between;
            font-size: 1.2rem;
            font-weight: 700;
            color: #2d3748;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 2px solid #e2e8f0;
        }
        
        .btn-proceed {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            margin-top: 1.5rem;
            transition: all 0.3s;
        }
        
        .btn-proceed:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">
            <i class="fas fa-store"></i>
            Kastro Store
        </a>
        
        <div class="cart-indicator">
            <a href="/cart/view" style="text-decoration: none; color: inherit;">
                <i class="fas fa-shopping-cart" style="font-size: 1.5rem;"></i>
                <span class="cart-count" id="cartCount">0</span>
            </a>
        </div>
    </nav>
    
    <div class="container">
        <div class="header">
            <h1>Our Premium Collection</h1>
            <p>Discover the latest technology and accessories with exclusive discounts</p>
        </div>
        
        <div class="filters">
            <div class="filter-group">
                <button class="filter-btn active" onclick="filterProducts('all')">All Products</button>
                <button class="filter-btn" onclick="filterProducts('Laptops')">Laptops</button>
                <button class="filter-btn" onclick="filterProducts('Audio')">Audio</button>
                <button class="filter-btn" onclick="filterProducts('Wearables')">Wearables</button>
                <button class="filter-btn" onclick="filterProducts('Accessories')">Accessories</button>
            </div>
            
            <div class="search-box">
                <i class="fas fa-search"></i>
                <input type="text" id="searchInput" placeholder="Search products..." onkeyup="searchProducts()">
            </div>
        </div>
        
        <div class="products-grid" id="productsGrid">
            {% for product in products %}
            <div class="product-card" data-category="{{ product.category }}" data-name="{{ product.name|lower }}">
                {% if product.discount > 0 %}
                <div class="product-badge">-{{ product.discount }}% OFF</div>
                {% endif %}
                
                <div class="product-image">
                    {{ product.image }}
                </div>
                
                <div class="product-content">
                    <span class="product-category">{{ product.category }}</span>
                    <h3 class="product-title">{{ product.name }}</h3>
                    <p class="product-description">{{ product.description }}</p>
                    
                    <div class="product-rating">
                        <div class="stars">
                            {% for i in range(5) %}
                                {% if i < product.rating|int %}
                                    <i class="fas fa-star"></i>
                                {% else %}
                                    <i class="far fa-star"></i>
                                {% endif %}
                            {% endfor %}
                        </div>
                        <span class="rating-count">({{ product.reviews }} reviews)</span>
                    </div>
                    
                    <div class="product-price">
                        {% set discounted_price = product.price * (1 - product.discount/100) %}
                        <span class="current-price">${{ "%.2f"|format(discounted_price) }}</span>
                        {% if product.discount > 0 %}
                            <span class="original-price">${{ "%.2f"|format(product.price) }}</span>
                            <span class="discount">Save ${{ "%.2f"|format(product.price - discounted_price) }}</span>
                        {% endif %}
                    </div>
                    
                    <div class="product-actions">
                        <button class="btn-add-to-cart {% if not product.in_stock %}out-of-stock{% endif %}" 
                                onclick="addToCart({{ product.id }}, '{{ product.name }}')"
                                {% if not product.in_stock %}disabled{% endif %}>
                            <i class="fas fa-shopping-cart"></i>
                            {% if product.in_stock %}Add to Cart{% else %}Out of Stock{% endif %}
                        </button>
                        <button class="btn-wishlist" onclick="toggleWishlist({{ product.id }})">
                            <i class="far fa-heart"></i>
                        </button>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        {% if msg %}
        <div class="notification" id="notification">
            <div class="notification-icon">
                <i class="fas fa-check"></i>
            </div>
            <div>
                <strong>Item Added!</strong>
                <p>{{ msg }}</p>
            </div>
        </div>
        {% endif %}
        
        <div class="cart-summary">
            <h2>Order Summary</h2>
            <div class="summary-item">
                <span>Subtotal</span>
                <span id="subtotal">$0.00</span>
            </div>
            <div class="summary-item">
                <span>Shipping</span>
                <span id="shipping">$0.00</span>
            </div>
            <div class="summary-item">
                <span>Tax</span>
                <span id="tax">$0.00</span>
            </div>
            <div class="summary-total">
                <span>Total</span>
                <span id="total">$0.00</span>
            </div>
            
            <form action="/shipping/" method="get">
                <button type="submit" class="btn-proceed" id="proceedBtn" disabled>
                    <i class="fas fa-arrow-right"></i> Proceed to Shipping
                </button>
            </form>
            
            <form action="/cart/view" method="get" style="margin-top: 1rem;">
                <button type="submit" class="btn-proceed" style="background: #e2e8f0; color: #4a5568;">
                    <i class="fas fa-shopping-cart"></i> View Cart Details
                </button>
            </form>
        </div>
    </div>
    
    <script>
        let cartItems = [];
        let cartCount = 0;
        
        function addToCart(productId, productName) {
            const product = products.find(p => p.id === productId);
            if (!product) return;
            
            cartItems.push(product);
            cartCount++;
            updateCartUI();
            
            showNotification(`Added ${productName} to cart`);
            
            // Send to server (simulated)
            fetch('/add-to-cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ productId: productId })
            });
        }
        
        function updateCartUI() {
            document.getElementById('cartCount').textContent = cartCount;
            
            let subtotal = 0;
            cartItems.forEach(item => {
                const price = item.price * (1 - item.discount/100);
                subtotal += price;
            });
            
            const shipping = subtotal > 50 ? 0 : 9.99;
            const tax = subtotal * 0.08;
            const total = subtotal + shipping + tax;
            
            document.getElementById('subtotal').textContent = '$' + subtotal.toFixed(2);
            document.getElementById('shipping').textContent = '$' + shipping.toFixed(2);
            document.getElementById('tax').textContent = '$' + tax.toFixed(2);
            document.getElementById('total').textContent = '$' + total.toFixed(2);
            
            document.getElementById('proceedBtn').disabled = cartCount === 0;
        }
        
        function showNotification(message) {
            const notification = document.getElementById('notification') || createNotification();
            notification.querySelector('p').textContent = message;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
        
        function createNotification() {
            const div = document.createElement('div');
            div.className = 'notification';
            div.innerHTML = `
                <div class="notification-icon">
                    <i class="fas fa-check"></i>
                </div>
                <div>
                    <strong>Item Added!</strong>
                    <p></p>
                </div>
            `;
            document.body.appendChild(div);
            return div;
        }
        
        function filterProducts(category) {
            const buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            const products = document.querySelectorAll('.product-card');
            products.forEach(product => {
                if (category === 'all' || product.dataset.category === category) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        }
        
        function searchProducts() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const products = document.querySelectorAll('.product-card');
            
            products.forEach(product => {
                const productName = product.dataset.name;
                if (productName.includes(searchTerm)) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        }
        
        function toggleWishlist(productId) {
            const button = event.target.closest('.btn-wishlist');
            const icon = button.querySelector('i');
            
            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                icon.style.color = '#ff6b6b';
                showNotification('Added to wishlist');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                icon.style.color = '';
                showNotification('Removed from wishlist');
            }
        }
        
        // Initialize products data for JavaScript
        const products = {{ products|tojson }};
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""
    
    if request.method == "POST":
        selected = request.form.getlist("items")
        if selected:
            c = conn()
            with c.cursor() as cur:
                for item in selected:
                    cur.execute("INSERT INTO cart (item) VALUES (%s)", (item,))
                c.commit()
            msg = f"Added {len(selected)} items to cart successfully!"
        else:
            msg = "No items selected"
    
    return render_template_string(PRODUCT_CATALOG_TEMPLATE, products=PRODUCTS, msg=msg)

@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    try:
        data = request.get_json()
        product_id = data.get('productId')
        
        c = conn()
        with c.cursor() as cur:
            # Find product by ID
            product = next((p for p in PRODUCTS if p["id"] == product_id), None)
            if product:
                cur.execute("INSERT INTO cart (item) VALUES (%s)", (product["name"],))
                c.commit()
                return jsonify({"success": True, "message": f"Added {product['name']} to cart"})
            else:
                return jsonify({"success": False, "message": "Product not found"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/view")
@app.route("/cart/view")
def view():
    CART_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Cart - Kastro Store</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                background: #f8f9fa;
            }
            
            .navbar {
                background: white;
                box-shadow: 0 2px 15px rgba(0,0,0,0.1);
                padding: 1rem 5%;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .container {
                max-width: 1200px;
                margin: 2rem auto;
                padding: 0 5%;
            }
            
            .cart-header {
                background: white;
                padding: 2rem;
                border-radius: 15px;
                margin-bottom: 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .cart-items {
                background: white;
                border-radius: 15px;
                padding: 2rem;
                margin-bottom: 2rem;
            }
            
            .cart-item {
                display: flex;
                align-items: center;
                padding: 1.5rem;
                border-bottom: 1px solid #e2e8f0;
                gap: 2rem;
            }
            
            .cart-item:last-child {
                border-bottom: none;
            }
            
            .item-image {
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                color: white;
            }
            
            .item-details {
                flex: 1;
            }
            
            .item-price {
                font-size: 1.2rem;
                font-weight: 700;
                color: #2d3748;
            }
            
            .quantity-controls {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .quantity-btn {
                width: 30px;
                height: 30px;
                border: 2px solid #e2e8f0;
                border-radius: 50%;
                background: white;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .quantity-btn:hover {
                border-color: #667eea;
                color: #667eea;
            }
            
            .remove-btn {
                color: #ff6b6b;
                cursor: pointer;
                padding: 0.5rem;
            }
            
            .cart-summary {
                background: white;
                border-radius: 15px;
                padding: 2rem;
            }
            
            .btn-checkout {
                width: 100%;
                padding: 1rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                margin-top: 1.5rem;
                transition: all 0.3s;
            }
            
            .empty-cart {
                text-align: center;
                padding: 4rem 2rem;
            }
            
            .empty-cart i {
                font-size: 4rem;
                color: #e2e8f0;
                margin-bottom: 1rem;
            }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <a href="/" style="text-decoration: none; color: inherit; display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-store"></i>
                <span style="font-size: 1.5rem; font-weight: 700;">Kastro Store</span>
            </a>
            <a href="/" style="color: #667eea; text-decoration: none;">
                <i class="fas fa-arrow-left"></i> Continue Shopping
            </a>
        </nav>
        
        <div class="container">
            {% if cart %}
            <div class="cart-header">
                <h1>Your Shopping Cart ({{ cart|length }} items)</h1>
                <a href="/shipping/" style="text-decoration: none;">
                    <button class="btn-checkout" style="width: auto; padding: 0.8rem 2rem;">
                        <i class="fas fa-arrow-right"></i> Proceed to Checkout
                    </button>
                </a>
            </div>
            
            <div class="cart-items">
                {% for item in cart %}
                <div class="cart-item">
                    <div class="item-image">📦</div>
                    <div class="item-details">
                        <h3>{{ item }}</h3>
                        <p>Premium quality product with warranty</p>
                    </div>
                    <div class="item-price">$199.99</div>
                    <div class="quantity-controls">
                        <button class="quantity-btn">-</button>
                        <span>1</span>
                        <button class="quantity-btn">+</button>
                    </div>
                    <div class="remove-btn">
                        <i class="fas fa-trash"></i>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="cart-summary">
                <!-- Summary content here -->
            </div>
            {% else %}
            <div class="empty-cart">
                <i class="fas fa-shopping-cart"></i>
                <h2>Your cart is empty</h2>
                <p>Add some amazing products to get started!</p>
                <a href="/" style="text-decoration: none;">
                    <button class="btn-checkout" style="width: auto; padding: 0.8rem 2rem; margin-top: 2rem;">
                        <i class="fas fa-store"></i> Start Shopping
                    </button>
                </a>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    
    c = conn()
    with c.cursor() as cur:
        cur.execute("SELECT item FROM cart")
        data = [r[0] for r in cur.fetchall()]
    
    return render_template_string(CART_TEMPLATE, cart=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
