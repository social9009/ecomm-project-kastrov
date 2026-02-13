from flask import Flask, render_template_string, redirect, jsonify, session
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ecommerce_secret_key_2024'

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kastro's Online Store - Premium E-commerce</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .notification-bar {
            background: #ff6b6b;
            color: white;
            text-align: center;
            padding: 8px;
            font-size: 14px;
            font-weight: 500;
        }
        
        .navbar {
            background: white;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
            padding: 1rem 5%;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.8rem;
            font-weight: 700;
            color: #4a5568;
        }
        
        .logo i {
            color: #667eea;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        
        .nav-links a {
            text-decoration: none;
            color: #4a5568;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #667eea;
        }
        
        .hero {
            text-align: center;
            padding: 6rem 5%;
            color: white;
        }
        
        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .hero p {
            font-size: 1.2rem;
            max-width: 600px;
            margin: 0 auto 2rem;
            opacity: 0.9;
        }
        
        .cta-button {
            background: white;
            color: #667eea;
            border: none;
            padding: 1rem 3rem;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            text-decoration: none;
            display: inline-block;
        }
        
        .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        .features {
            display: flex;
            justify-content: center;
            gap: 2rem;
            padding: 3rem 5%;
            background: white;
            border-radius: 20px 20px 0 0;
            margin-top: -50px;
            flex-wrap: wrap;
        }
        
        .feature-card {
            flex: 1;
            min-width: 250px;
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            transition: transform 0.3s;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
        }
        
        .feature-card i {
            font-size: 2.5rem;
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .feature-card h3 {
            margin-bottom: 0.5rem;
            color: #2d3748;
        }
        
        .realtime-stats {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            font-size: 0.9rem;
        }
        
        .stats-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }
        
        .count {
            font-weight: 600;
            color: #667eea;
        }
        
        .marquee {
            background: rgba(255,255,255,0.1);
            padding: 10px;
            margin: 1rem 0;
            border-radius: 5px;
            overflow: hidden;
        }
        
        .marquee-content {
            display: inline-block;
            white-space: nowrap;
            animation: marquee 30s linear infinite;
        }
        
        @keyframes marquee {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        
        .flash-deal {
            background: linear-gradient(45deg, #ff6b6b, #ffa8a8);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(255,107,107,0.4); }
            70% { box-shadow: 0 0 0 10px rgba(255,107,107,0); }
            100% { box-shadow: 0 0 0 0 rgba(255,107,107,0); }
        }
    </style>
</head>
<body>
    <div class="notification-bar">
        🎉 Free shipping on all orders over $50! Limited time offer.
    </div>
    
    <nav class="navbar">
        <div class="logo">
            <i class="fas fa-store"></i>
            Kastro Store
        </div>
        <div class="nav-links">
            <a href="#"><i class="fas fa-gift"></i> Deals</a>
            <a href="#"><i class="fas fa-tags"></i> Categories</a>
            <a href="#"><i class="fas fa-question-circle"></i> Help</a>
        </div>
    </nav>
    
    <div class="hero">
        <h1>Welcome to Kastro's Online Store</h1>
        <p>Discover premium products with lightning-fast delivery and 24/7 customer support. Join thousands of satisfied customers!</p>
        
        <div class="marquee">
            <div class="marquee-content">
                🚚 Order now and get it delivered in 2 hours! • ⭐⭐⭐⭐⭐ 4.9/5 from 10,000+ reviews • 🔒 100% Secure Checkout • 📦 Free returns within 30 days •
            </div>
        </div>
        
        <div class="flash-deal">
            <i class="fas fa-bolt"></i> FLASH DEAL: Use code WELCOME20 for 20% off your first order!
        </div>
        
        <a href="/users/" class="cta-button">
            <i class="fas fa-user-plus"></i> Start Shopping →
        </a>
    </div>
    
    <div class="features">
        <div class="feature-card">
            <i class="fas fa-shipping-fast"></i>
            <h3>Free Shipping</h3>
            <p>Free delivery on orders over $50</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-shield-alt"></i>
            <h3>Secure Payment</h3>
            <p>100% secure SSL encryption</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-headset"></i>
            <h3>24/7 Support</h3>
            <p>Round-the-clock customer service</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-undo"></i>
            <h3>Easy Returns</h3>
            <p>30-day return policy</p>
        </div>
    </div>
    
    <div class="realtime-stats">
        <div class="stats-item">
            <span>Online Now:</span>
            <span class="count">{{ stats.online }}</span>
        </div>
        <div class="stats-item">
            <span>Orders Today:</span>
            <span class="count">{{ stats.orders }}</span>
        </div>
        <div class="stats-item">
            <span>Products Sold:</span>
            <span class="count">{{ stats.sold }}</span>
        </div>
    </div>
    
    <script>
        // Real-time stats update
        function updateStats() {
            const stats = document.querySelectorAll('.count');
            stats.forEach(stat => {
                const current = parseInt(stat.textContent);
                const change = Math.floor(Math.random() * 3);
                stat.textContent = current + change;
            });
        }
        
        setInterval(updateStats, 5000);
        
        // Live time update
        function updateTime() {
            const now = new Date();
            document.getElementById('liveTime').textContent = 
                now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
        }
        
        setInterval(updateTime, 1000);
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    # Generate random stats for demo
    import random
    stats = {
        'online': random.randint(850, 1200),
        'orders': random.randint(2500, 3200),
        'sold': random.randint(45000, 50000)
    }
    return render_template_string(HOME_TEMPLATE, stats=stats)

@app.route("/success")
def success():
    SUCCESS_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Order Successful - Kastro Store</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .success-card {
                background: white;
                padding: 3rem;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                width: 90%;
            }
            
            .checkmark {
                font-size: 5rem;
                color: #4CAF50;
                margin-bottom: 1rem;
                animation: scale 0.5s ease-in-out;
            }
            
            @keyframes scale {
                0% { transform: scale(0); }
                70% { transform: scale(1.2); }
                100% { transform: scale(1); }
            }
            
            h2 {
                color: #2d3748;
                margin-bottom: 1rem;
                font-size: 2.5rem;
            }
            
            p {
                color: #4a5568;
                margin-bottom: 2rem;
                line-height: 1.6;
            }
            
            .order-details {
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 2rem 0;
                text-align: left;
            }
            
            .detail-item {
                display: flex;
                justify-content: space-between;
                margin-bottom: 0.5rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid #e2e8f0;
            }
            
            .buttons {
                display: flex;
                gap: 1rem;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .btn {
                padding: 0.8rem 2rem;
                border-radius: 50px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .btn-primary {
                background: #667eea;
                color: white;
            }
            
            .btn-secondary {
                background: #e2e8f0;
                color: #4a5568;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>
        <div class="success-card">
            <div class="checkmark">🎉</div>
            <h2>Order Successful!</h2>
            <p>Your order has been placed successfully and will be delivered soon.</p>
            
            <div class="order-details">
                <div class="detail-item">
                    <span>Order ID:</span>
                    <span>#{{ order_id }}</span>
                </div>
                <div class="detail-item">
                    <span>Estimated Delivery:</span>
                    <span>{{ delivery_date }}</span>
                </div>
                <div class="detail-item">
                    <span>Tracking Number:</span>
                    <span>{{ tracking_number }}</span>
                </div>
            </div>
            
            <div class="buttons">
                <a href="/" class="btn btn-primary">
                    <i class="fas fa-home"></i> Back to Home
                </a>
                <a href="#" class="btn btn-secondary">
                    <i class="fas fa-download"></i> Download Invoice
                </a>
                <a href="#" class="btn btn-secondary">
                    <i class="fas fa-truck"></i> Track Order
                </a>
            </div>
        </div>
        
        <script>
            // Generate random order details
            document.addEventListener('DOMContentLoaded', function() {
                const orderId = 'KASTRO' + Math.floor(Math.random() * 1000000);
                const deliveryDate = new Date();
                deliveryDate.setDate(deliveryDate.getDate() + 3);
                
                document.querySelectorAll('.detail-item')[0].children[1].textContent = orderId;
                document.querySelectorAll('.detail-item')[1].children[1].textContent = 
                    deliveryDate.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
                document.querySelectorAll('.detail-item')[2].children[1].textContent = 
                    'TRK' + Math.floor(Math.random() * 1000000000);
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(SUCCESS_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
