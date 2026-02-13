from flask import Flask, request, render_template_string, redirect, jsonify
import pymysql
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Database connection remains the same
def conn():
    return pymysql.connect(
        host="mysql-shipping",
        user="root",
        password="password",
        database="shippingdb"
    )

# Enhanced Shipping Template
SHIPPING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shipping - Kastro Store</title>
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
        
        .checkout-steps {
            background: white;
            padding: 1.5rem 5%;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
            display: flex;
            justify-content: center;
            gap: 3rem;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .step {
            display: flex;
            align-items: center;
            gap: 1rem;
            color: #a0aec0;
        }
        
        .step.active {
            color: #667eea;
        }
        
        .step-number {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            background: #e2e8f0;
        }
        
        .step.active .step-number {
            background: #667eea;
            color: white;
        }
        
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 5%;
        }
        
        .main-content {
            display: flex;
            gap: 2rem;
        }
        
        .shipping-form {
            flex: 2;
            background: white;
            border-radius: 15px;
            padding: 2rem;
        }
        
        .order-summary {
            flex: 1;
            background: white;
            border-radius: 15px;
            padding: 2rem;
            height: fit-content;
            position: sticky;
            top: 100px;
        }
        
        .section-header {
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .section-header h2 {
            color: #2d3748;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .form-row {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .form-group {
            flex: 1;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #2d3748;
            font-weight: 500;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .shipping-methods {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .shipping-method {
            flex: 1;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 1.5rem;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .shipping-method:hover {
            border-color: #667eea;
        }
        
        .shipping-method.selected {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }
        
        .shipping-method h4 {
            margin-bottom: 0.5rem;
            color: #2d3748;
        }
        
        .shipping-price {
            font-weight: 700;
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .shipping-estimate {
            font-size: 0.9rem;
            color: #4CAF50;
        }
        
        .form-actions {
            display: flex;
            justify-content: space-between;
            margin-top: 2rem;
        }
        
        .btn-back {
            padding: 0.8rem 2rem;
            background: #e2e8f0;
            color: #4a5568;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-continue {
            padding: 0.8rem 2rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s;
        }
        
        .btn-continue:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        .order-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .order-image {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
        }
        
        .order-details {
            flex: 1;
        }
        
        .order-price {
            font-weight: 600;
            color: #2d3748;
        }
        
        .summary-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            padding-bottom: 0.5rem;
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
        
        .delivery-options {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }
        
        .delivery-option {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
            padding: 1rem;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            border: 2px solid #e2e8f0;
        }
        
        .delivery-option.selected {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }
        
        .delivery-time {
            font-weight: 600;
            color: #4CAF50;
        }
        
        .address-suggestions {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
        }
        
        .suggestion {
            padding: 0.5rem 1rem;
            border-bottom: 1px solid #e2e8f0;
            cursor: pointer;
        }
        
        .suggestion:hover {
            background: white;
        }
        
        .map-preview {
            height: 200px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
    </style>
</head>
<body>
    <div class="checkout-steps">
        <div class="step active">
            <div class="step-number">1</div>
            <div>Cart</div>
        </div>
        <div class="step active">
            <div class="step-number">2</div>
            <div>Shipping</div>
        </div>
        <div class="step">
            <div class="step-number">3</div>
            <div>Payment</div>
        </div>
        <div class="step">
            <div class="step-number">4</div>
            <div>Confirmation</div>
        </div>
    </div>
    
    <div class="container">
        <div class="main-content">
            <form method="post" class="shipping-form">
                <div class="section-header">
                    <h2><i class="fas fa-shipping-fast"></i> Shipping Details</h2>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="firstName">First Name *</label>
                        <input type="text" id="firstName" name="firstName" required>
                    </div>
                    <div class="form-group">
                        <label for="lastName">Last Name *</label>
                        <input type="text" id="lastName" name="lastName" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="email">Email Address *</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="phone">Phone Number *</label>
                    <input type="tel" id="phone" name="phone" required>
                </div>
                
                <div class="form-group">
                    <label for="address">Street Address *</label>
                    <input type="text" id="address" name="address" required>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="city">City *</label>
                        <input type="text" id="city" name="city" required>
                    </div>
                    <div class="form-group">
                        <label for="state">State *</label>
                        <input type="text" id="state" name="state" required>
                    </div>
                    <div class="form-group">
                        <label for="zip">ZIP Code *</label>
                        <input type="text" id="zip" name="zip" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="country">Country *</label>
                    <select id="country" name="country" required>
                        <option value="">Select Country</option>
                        <option value="US">United States</option>
                        <option value="CA">Canada</option>
                        <option value="UK">United Kingdom</option>
                        <option value="AU">Australia</option>
                    </select>
                </div>
                
                <div class="delivery-options">
                    <h3>Delivery Options</h3>
                    <div class="delivery-option" onclick="selectDelivery(this, 'standard')">
                        <input type="radio" name="delivery" value="standard" checked style="display: none;">
                        <div style="flex: 1;">
                            <h4>Standard Delivery</h4>
                            <p>5-7 business days</p>
                        </div>
                        <div class="delivery-time">FREE</div>
                    </div>
                    
                    <div class="delivery-option" onclick="selectDelivery(this, 'express')">
                        <input type="radio" name="delivery" value="express" style="display: none;">
                        <div style="flex: 1;">
                            <h4>Express Delivery</h4>
                            <p>2-3 business days</p>
                        </div>
                        <div class="delivery-time">$9.99</div>
                    </div>
                    
                    <div class="delivery-option" onclick="selectDelivery(this, 'nextday')">
                        <input type="radio" name="delivery" value="nextday" style="display: none;">
                        <div style="flex: 1;">
                            <h4>Next Day Delivery</h4>
                            <p>Order by 2PM for next day</p>
                        </div>
                        <div class="delivery-time">$19.99</div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="instructions">Delivery Instructions (Optional)</label>
                    <textarea id="instructions" name="instructions" rows="3" placeholder="Leave at front door, ring bell, etc."></textarea>
                </div>
                
                <div class="address-suggestions">
                    <h4>Recent Addresses</h4>
                    <div class="suggestion" onclick="useSuggestion('123 Main St, New York, NY 10001')">
                        123 Main St, New York, NY 10001
                    </div>
                    <div class="suggestion" onclick="useSuggestion('456 Oak Ave, Brooklyn, NY 11201')">
                        456 Oak Ave, Brooklyn, NY 11201
                    </div>
                </div>
                
                <div class="map-preview">
                    <i class="fas fa-map-marked-alt"></i> Delivery Area Preview
                </div>
                
                <div class="form-actions">
                    <a href="/cart/" class="btn-back">
                        <i class="fas fa-arrow-left"></i> Back to Cart
                    </a>
                    <button type="submit" class="btn-continue">
                        Continue to Payment <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </form>
            
            <div class="order-summary">
                <div class="section-header">
                    <h2><i class="fas fa-receipt"></i> Order Summary</h2>
                </div>
                
                <div class="order-item">
                    <div class="order-image">💻</div>
                    <div class="order-details">
                        <strong>MacBook Pro 16"</strong>
                        <p>Qty: 1</p>
                    </div>
                    <div class="order-price">$3,149.99</div>
                </div>
                
                <div class="order-item">
                    <div class="order-image">🎧</div>
                    <div class="order-details">
                        <strong>Sony WH-1000XM5</strong>
                        <p>Qty: 1</p>
                    </div>
                    <div class="order-price">$339.99</div>
                </div>
                
                <div class="summary-row">
                    <span>Subtotal</span>
                    <span>$3,489.98</span>
                </div>
                <div class="summary-row">
                    <span>Shipping</span>
                    <span id="shippingCost">FREE</span>
                </div>
                <div class="summary-row">
                    <span>Tax</span>
                    <span>$279.20</span>
                </div>
                <div class="summary-total">
                    <span>Total</span>
                    <span id="totalCost">$3,769.18</span>
                </div>
                
                <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e2e8f0;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; color: #4CAF50; margin-bottom: 0.5rem;">
                        <i class="fas fa-shield-alt"></i>
                        <span>Secure checkout</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; color: #667eea; margin-bottom: 0.5rem;">
                        <i class="fas fa-undo"></i>
                        <span>30-day returns</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; color: #ff6b6b;">
                        <i class="fas fa-gift"></i>
                        <span>Free gift included</span>
                    </div>
                </div>
                
                <div style="margin-top: 2rem; text-align: center;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/320px-Flag_of_Europe.svg.png" 
                         style="height: 30px; margin: 0 5px; opacity: 0.7;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Visa_America.svg/320px-Visa_America.svg.png" 
                         style="height: 30px; margin: 0 5px; opacity: 0.7;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Mastercard_2019_logo.svg/320px-Mastercard_2019_logo.svg.png" 
                         style="height: 30px; margin: 0 5px; opacity: 0.7;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Stripe_Logo%2C_revised_2016.svg/320px-Stripe_Logo%2C_revised_2016.svg.png" 
                         style="height: 30px; margin: 0 5px; opacity: 0.7;">
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function selectDelivery(element, type) {
            document.querySelectorAll('.delivery-option').forEach(el => {
                el.classList.remove('selected');
            });
            element.classList.add('selected');
            
            let shippingCost = 0;
            let total = 3769.18; // Base total
            
            switch(type) {
                case 'standard':
                    shippingCost = 0;
                    break;
                case 'express':
                    shippingCost = 9.99;
                    break;
                case 'nextday':
                    shippingCost = 19.99;
                    break;
            }
            
            document.getElementById('shippingCost').textContent = 
                shippingCost === 0 ? 'FREE' : '$' + shippingCost.toFixed(2);
            
            const totalCost = total + shippingCost;
            document.getElementById('totalCost').textContent = '$' + totalCost.toFixed(2);
        }
        
        function useSuggestion(address) {
            document.getElementById('address').value = address;
        }
        
        // Simulate address auto-complete
        document.getElementById('address').addEventListener('input', function(e) {
            const value = e.target.value;
            if (value.length > 3) {
                // In a real app, this would call a geocoding API
                console.log('Searching for address:', value);
            }
        });
        
        // Initialize with standard delivery selected
        document.querySelector('.delivery-option').click();
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""
    
    if request.method == "POST":
        try:
            # Get all form data
            address = request.form.get("address", "")
            first_name = request.form.get("firstName", "")
            last_name = request.form.get("lastName", "")
            email = request.form.get("email", "")
            phone = request.form.get("phone", "")
            city = request.form.get("city", "")
            state = request.form.get("state", "")
            zip_code = request.form.get("zip", "")
            country = request.form.get("country", "")
            delivery = request.form.get("delivery", "standard")
            instructions = request.form.get("instructions", "")
            
            # Create full address string
            full_address = f"{first_name} {last_name}, {address}, {city}, {state} {zip_code}, {country}"
            
            db = conn()
            with db.cursor() as cur:
                cur.execute("INSERT INTO address (address, email, phone, delivery_method, instructions) VALUES (%s, %s, %s, %s, %s)",
                           (full_address, email, phone, delivery, instructions))
                db.commit()
            
            msg = "Shipping address saved successfully!"
            return redirect("/payment/")
            
        except Exception as e:
            msg = f"Error: {str(e)}"
    
    return render_template_string(SHIPPING_TEMPLATE, msg=msg)

@app.route("/view")
def view():
    db = conn()
    with db.cursor() as cur:
        cur.execute("SELECT address FROM address")
        rows = [r[0] for r in cur.fetchall()]
    return "<br>".join(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
