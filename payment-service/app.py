from flask import Flask, request, render_template_string, redirect, jsonify
import pymysql
import time
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)

# Initialize database with proper schema
def init_db():
    try:
        conn = pymysql.connect(
            host="mysql-payment",
            user="root",
            password="password",
            database="paymentdb"
        )
        with conn.cursor() as cur:
            # Create table if it doesn't exist with proper columns
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pay (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    amount DECIMAL(10, 2),
                    status VARCHAR(50),
                    payment_method VARCHAR(50),
                    order_id VARCHAR(100),
                    transaction_id VARCHAR(100),
                    auth_code VARCHAR(100),
                    card_last_four VARCHAR(4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

# Initialize database on startup
init_db()

# Database connection
def conn():
    return pymysql.connect(
        host="mysql-payment",
        user="root",
        password="password",
        database="paymentdb"
    )

# Mock payment gateway that always succeeds
class MockPaymentGateway:
    @staticmethod
    def validate_card(card_number, card_name, expiry_date, cvv):
        """Always return success for demo purposes"""
        return True, "Card validated successfully (Demo Mode)"
    
    @staticmethod
    def process_payment(card_number, amount, currency="USD"):
        """Always return success for demo purposes"""
        return "success", "Payment processed successfully (Demo Mode)"
    
    @staticmethod
    def generate_transaction_id():
        """Generate a mock transaction ID"""
        return f"TXN{str(uuid.uuid4())[:8].upper()}"
    
    @staticmethod
    def generate_auth_code():
        """Generate a mock authorization code"""
        return f"AUTH{str(uuid.uuid4())[:6].upper()}"
    
    @staticmethod
    def detect_card_type(card_number):
        """Detect card type from number"""
        card_number = card_number.replace(' ', '')
        if card_number.startswith('4'):
            return 'Visa'
        elif card_number.startswith('5'):
            return 'Mastercard'
        elif card_number.startswith('34') or card_number.startswith('37'):
            return 'American Express'
        elif card_number.startswith('6011') or card_number.startswith('65'):
            return 'Discover'
        else:
            return 'Credit Card'

# Enhanced Payment Template with always-success mode
PAYMENT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Payment - Kastro Store</title>
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
        
        .demo-banner {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            text-align: center;
            padding: 10px;
            font-weight: 500;
            position: sticky;
            top: 0;
            z-index: 1001;
        }
        
        .demo-banner i {
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .checkout-steps {
            background: white;
            padding: 1.5rem 5%;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
            display: flex;
            justify-content: center;
            gap: 3rem;
            position: sticky;
            top: 40px;
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
        
        .step.completed .step-number {
            background: #4CAF50;
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
        
        .payment-form {
            flex: 2;
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .order-summary {
            flex: 1;
            background: white;
            border-radius: 15px;
            padding: 2rem;
            height: fit-content;
            position: sticky;
            top: 140px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
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
        
        .payment-methods {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .payment-method {
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 1.5rem;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        
        .payment-method:hover {
            border-color: #667eea;
        }
        
        .payment-method.selected {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }
        
        .payment-method i {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: #667eea;
        }
        
        .payment-method h4 {
            margin-bottom: 0.5rem;
            color: #2d3748;
        }
        
        .payment-method p {
            font-size: 0.9rem;
            color: #4a5568;
        }
        
        .form-row {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .form-group {
            flex: 1;
            position: relative;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #2d3748;
            font-weight: 500;
        }
        
        .form-group input,
        .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .card-preview {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            padding: 1.5rem;
            color: white;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            transition: all 0.3s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .card-preview:before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 20px 20px;
        }
        
        .card-chip {
            width: 40px;
            height: 30px;
            background: linear-gradient(45deg, #ffd700, #ffec8b);
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        
        .card-number {
            font-family: monospace;
            font-size: 1.2rem;
            letter-spacing: 2px;
            margin-bottom: 1rem;
            font-weight: 500;
        }
        
        .card-details {
            display: flex;
            justify-content: space-between;
        }
        
        .card-name {
            font-size: 0.9rem;
            opacity: 0.9;
            text-transform: uppercase;
        }
        
        .card-expiry {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .card-type {
            position: absolute;
            top: 15px;
            right: 15px;
            font-size: 0.8rem;
            opacity: 0.8;
            background: rgba(255,255,255,0.2);
            padding: 2px 8px;
            border-radius: 10px;
        }
        
        .installment-options {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }
        
        .installment-option {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            margin-bottom: 0.5rem;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            border: 2px solid #e2e8f0;
            transition: all 0.3s;
        }
        
        .installment-option:hover {
            border-color: #667eea;
        }
        
        .installment-option.selected {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }
        
        .installment-price {
            font-weight: 700;
            color: #667eea;
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
            transition: all 0.3s;
        }
        
        .btn-back:hover {
            background: #d1d9e6;
        }
        
        .btn-pay {
            padding: 0.8rem 2rem;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s;
            font-size: 1.1rem;
        }
        
        .btn-pay:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(76, 175, 80, 0.3);
            background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
        }
        
        .demo-instructions {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1.5rem;
            margin-top: 2rem;
            border-left: 4px solid #4CAF50;
        }
        
        .demo-instructions h4 {
            color: #2d3748;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .demo-card {
            display: flex;
            justify-content: space-between;
            padding: 0.8rem;
            border-bottom: 1px solid #e2e8f0;
            font-family: monospace;
            font-size: 0.95rem;
        }
        
        .demo-card:last-child {
            border-bottom: none;
        }
        
        .demo-tip {
            font-size: 0.9rem;
            color: #4a5568;
            margin-top: 0.5rem;
            font-style: italic;
        }
        
        .security-badges {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #e2e8f0;
        }
        
        .security-badge {
            text-align: center;
        }
        
        .security-badge i {
            font-size: 1.5rem;
            color: #4CAF50;
            margin-bottom: 0.5rem;
        }
        
        .security-badge span {
            font-size: 0.8rem;
            color: #4a5568;
        }
        
        .processing-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }
        
        .processing-card {
            background: white;
            padding: 3rem;
            border-radius: 15px;
            text-align: center;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .processing-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid #4CAF50;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1.5rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .countdown {
            font-size: 2rem;
            font-weight: 700;
            color: #4CAF50;
            margin: 1rem 0;
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
        
        .promo-section {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
        }
        
        .promo-input {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        
        .promo-input input {
            flex: 1;
            padding: 0.8rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
        }
        
        .promo-input button {
            padding: 0.8rem 1.5rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
        }
        
        .promo-message {
            margin-top: 0.5rem;
            font-size: 0.9rem;
        }
        
        .success-message {
            color: #4CAF50;
        }
        
        .error-message {
            color: #ff6b6b;
        }
    </style>
</head>
<body>
    <div class="demo-banner">
        <i class="fas fa-info-circle"></i>
        DEMO MODE: All payments will succeed with any card number
    </div>
    
    <div class="checkout-steps">
        <div class="step completed">
            <div class="step-number"><i class="fas fa-check"></i></div>
            <div>Cart</div>
        </div>
        <div class="step completed">
            <div class="step-number"><i class="fas fa-check"></i></div>
            <div>Shipping</div>
        </div>
        <div class="step active">
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
            <form method="post" class="payment-form" id="paymentForm">
                <input type="hidden" name="amount" value="3769.18">
                <input type="hidden" name="payment_method" id="paymentMethodInput" value="card">
                
                <div class="section-header">
                    <h2><i class="fas fa-credit-card"></i> Secure Your Payment</h2>
                    <p style="color: #4a5568; margin-top: 0.5rem;">Enter any card details - this is a demo</p>
                </div>
                
                <div class="payment-methods">
                    <div class="payment-method selected" onclick="selectPaymentMethod(this, 'card')">
                        <i class="fas fa-credit-card"></i>
                        <h4>Credit/Debit Card</h4>
                        <p>Any card will work in demo mode</p>
                    </div>
                    
                    <div class="payment-method" onclick="selectPaymentMethod(this, 'paypal')">
                        <i class="fab fa-paypal"></i>
                        <h4>PayPal</h4>
                        <p>Fast and secure payments</p>
                    </div>
                    
                    <div class="payment-method" onclick="selectPaymentMethod(this, 'apple')">
                        <i class="fab fa-apple"></i>
                        <h4>Apple Pay</h4>
                        <p>Pay with Face ID or Touch ID</p>
                    </div>
                </div>
                
                <div id="cardForm" class="payment-details">
                    <div class="card-preview" id="cardPreviewContainer">
                        <div class="card-type" id="cardTypeDisplay">VISA</div>
                        <div class="card-chip"></div>
                        <div class="card-number" id="cardPreview">•••• •••• •••• ••••</div>
                        <div class="card-details">
                            <div class="card-name" id="namePreview">YOUR NAME</div>
                            <div class="card-expiry" id="expiryPreview">MM/YY</div>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="cardNumber">Card Number *</label>
                            <input type="text" id="cardNumber" name="card_number" 
                                   placeholder="1234 5678 9012 3456" 
                                   maxlength="19" 
                                   oninput="formatCardNumber()" 
                                   onkeyup="updateCardPreview()"
                                   required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="cardName">Cardholder Name *</label>
                            <input type="text" id="cardName" name="card_name" 
                                   placeholder="John Doe" 
                                   onkeyup="updateCardPreview()"
                                   required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="expiryDate">Expiry Date (MM/YY) *</label>
                            <input type="text" id="expiryDate" name="expiry_date" 
                                   placeholder="12/28" 
                                   maxlength="5" 
                                   oninput="formatExpiryDate()" 
                                   onkeyup="updateCardPreview()"
                                   required>
                        </div>
                        <div class="form-group">
                            <label for="cvv">CVV *</label>
                            <input type="password" id="cvv" name="cvv" 
                                   placeholder="123" 
                                   maxlength="4" 
                                   required>
                        </div>
                    </div>
                    
                    <div class="demo-instructions">
                        <h4><i class="fas fa-vial"></i> Demo Instructions</h4>
                        <p>For demo purposes, you can use any card number. Examples:</p>
                        <div class="demo-card">
                            <span>4111 1111 1111 1111</span>
                            <span style="color: #4CAF50; font-weight: 500;">Visa</span>
                        </div>
                        <div class="demo-card">
                            <span>5555 5555 5555 4444</span>
                            <span style="color: #eb001b; font-weight: 500;">Mastercard</span>
                        </div>
                        <div class="demo-card">
                            <span>3782 822463 10005</span>
                            <span style="color: #2e77bb; font-weight: 500;">Amex</span>
                        </div>
                        <p class="demo-tip">All payments will succeed in this demo environment</p>
                    </div>
                    
                    <div class="installment-options">
                        <h3>Payment Options</h3>
                        <div class="installment-option selected" onclick="selectInstallment(this, 'full')">
                            <div>
                                <h4>Pay in Full</h4>
                                <p>One-time payment</p>
                            </div>
                            <div class="installment-price">$3,769.18</div>
                        </div>
                        
                        <div class="installment-option" onclick="selectInstallment(this, '3months')">
                            <div>
                                <h4>3 Monthly Payments</h4>
                                <p>No interest, no fees</p>
                            </div>
                            <div class="installment-price">$1,256.39/month</div>
                        </div>
                        
                        <div class="installment-option" onclick="selectInstallment(this, '6months')">
                            <div>
                                <h4>6 Monthly Payments</h4>
                                <p>No interest, no fees</p>
                            </div>
                            <div class="installment-price">$628.20/month</div>
                        </div>
                    </div>
                    
                    <div class="promo-section">
                        <h4>Promo Code (Optional)</h4>
                        <div class="promo-input">
                            <input type="text" id="promoCode" name="promo_code" placeholder="Enter promo code">
                            <button type="button" onclick="applyPromoCode()">Apply</button>
                        </div>
                        <div id="promoMessage" class="promo-message"></div>
                    </div>
                    
                    <div class="form-group">
                        <label style="display: flex; align-items: center; gap: 0.5rem;">
                            <input type="checkbox" id="saveCard" name="save_card" checked>
                            <span>Save this card for future purchases</span>
                        </label>
                    </div>
                </div>
                
                <div id="paypalForm" class="payment-details" style="display: none;">
                    <div style="text-align: center; padding: 2rem;">
                        <i class="fab fa-paypal" style="font-size: 4rem; color: #003087;"></i>
                        <p style="margin-top: 1rem;">You will be redirected to PayPal to complete your payment</p>
                    </div>
                </div>
                
                <div class="form-actions">
                    <a href="/shipping/" class="btn-back">
                        <i class="fas fa-arrow-left"></i> Back to Shipping
                    </a>
                    <button type="button" class="btn-pay" id="payButton" onclick="processPayment()">
                        <i class="fas fa-lock"></i> Complete Secure Payment
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
                    <span>FREE</span>
                </div>
                <div class="summary-row">
                    <span>Tax</span>
                    <span>$279.20</span>
                </div>
                <div class="summary-row" id="discountRow" style="display: none;">
                    <span>Discount</span>
                    <span id="discountAmount" style="color: #4CAF50;">-$0.00</span>
                </div>
                <div class="summary-total">
                    <span>Total</span>
                    <span id="orderTotal">$3,769.18</span>
                </div>
                
                <div class="security-badges">
                    <div class="security-badge">
                        <i class="fas fa-shield-alt"></i>
                        <span>SSL Secure</span>
                    </div>
                    <div class="security-badge">
                        <i class="fas fa-lock"></i>
                        <span>256-bit Encryption</span>
                    </div>
                    <div class="security-badge">
                        <i class="fas fa-user-shield"></i>
                        <span>PCI Compliant</span>
                    </div>
                </div>
                
                <div style="margin-top: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                    <p style="font-size: 0.9rem; color: #4a5568; margin-bottom: 0.5rem;">
                        <i class="fas fa-info-circle" style="color: #667eea;"></i>
                        This is a demo environment. No real payments are processed.
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="processing-overlay" id="processingOverlay">
        <div class="processing-card">
            <div class="processing-spinner"></div>
            <h2>Processing Demo Payment</h2>
            <p id="processingMessage">Simulating payment processing...</p>
            <div class="countdown" id="countdown">3</div>
        </div>
    </div>
    
    <script>
        let currentMethod = 'card';
        let totalAmount = 3769.18;
        let discountApplied = 0;
        
        function selectPaymentMethod(element, method) {
            document.querySelectorAll('.payment-method').forEach(el => {
                el.classList.remove('selected');
            });
            element.classList.add('selected');
            currentMethod = method;
            document.getElementById('paymentMethodInput').value = method;
            
            document.querySelectorAll('.payment-details').forEach(el => {
                el.style.display = 'none';
            });
            document.getElementById(method + 'Form').style.display = 'block';
        }
        
        function selectInstallment(element, plan) {
            document.querySelectorAll('.installment-option').forEach(el => {
                el.classList.remove('selected');
            });
            element.classList.add('selected');
            
            let monthly = totalAmount - discountApplied;
            switch(plan) {
                case '3months':
                    monthly = (totalAmount - discountApplied) / 3;
                    break;
                case '6months':
                    monthly = (totalAmount - discountApplied) / 6;
                    break;
            }
            
            if (plan === 'full') {
                document.getElementById('payButton').innerHTML = 
                    '<i class="fas fa-lock"></i> Pay $' + (totalAmount - discountApplied).toFixed(2);
            } else {
                document.getElementById('payButton').innerHTML = 
                    '<i class="fas fa-lock"></i> Start Installment Plan';
            }
        }
        
        function formatCardNumber() {
            let input = document.getElementById('cardNumber');
            let value = input.value.replace(/\D/g, '');
            let formatted = '';
            
            for (let i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) {
                    formatted += ' ';
                }
                formatted += value[i];
            }
            
            input.value = formatted.substring(0, 19);
            updateCardPreview();
        }
        
        function formatExpiryDate() {
            let input = document.getElementById('expiryDate');
            let value = input.value.replace(/\D/g, '');
            
            if (value.length >= 2) {
                input.value = value.substring(0, 2) + '/' + value.substring(2, 4);
            } else {
                input.value = value;
            }
        }
        
        function updateCardPreview() {
            const cardNumber = document.getElementById('cardNumber').value;
            const cardName = document.getElementById('cardName').value;
            const expiryDate = document.getElementById('expiryDate').value;
            
            // Update card preview
            if (cardNumber) {
                const lastFour = cardNumber.replace(/\s/g, '').slice(-4);
                const masked = '•••• •••• •••• ' + (lastFour || '••••');
                document.getElementById('cardPreview').textContent = masked;
                
                // Detect card type
                const cleanNumber = cardNumber.replace(/\s/g, '');
                let cardType = 'VISA';
                
                if (cleanNumber.startsWith('4')) cardType = 'VISA';
                else if (cleanNumber.startsWith('5')) cardType = 'MASTERCARD';
                else if (cleanNumber.startsWith('34') || cleanNumber.startsWith('37')) cardType = 'AMEX';
                else if (cleanNumber.startsWith('6011') || cleanNumber.startsWith('65')) cardType = 'DISCOVER';
                else cardType = 'CARD';
                
                document.getElementById('cardTypeDisplay').textContent = cardType;
                
                // Change card color based on type
                const preview = document.getElementById('cardPreviewContainer');
                switch(cardType) {
                    case 'VISA':
                        preview.style.background = 'linear-gradient(135deg, #1a1f71 0%, #ff5f00 100%)';
                        break;
                    case 'MASTERCARD':
                        preview.style.background = 'linear-gradient(135deg, #eb001b 0%, #f79e1b 100%)';
                        break;
                    case 'AMEX':
                        preview.style.background = 'linear-gradient(135deg, #2e77bb 0%, #006fcf 100%)';
                        break;
                    case 'DISCOVER':
                        preview.style.background = 'linear-gradient(135deg, #ff6000 0%, #ffa500 100%)';
                        break;
                    default:
                        preview.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                }
            } else {
                document.getElementById('cardPreview').textContent = '•••• •••• •••• ••••';
                document.getElementById('cardTypeDisplay').textContent = 'VISA';
                document.getElementById('cardPreviewContainer').style.background = 
                    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            }
            
            document.getElementById('namePreview').textContent = 
                cardName.toUpperCase() || 'YOUR NAME';
            document.getElementById('expiryPreview').textContent = 
                expiryDate || 'MM/YY';
        }
        
        function applyPromoCode() {
            const code = document.getElementById('promoCode').value.toUpperCase();
            const message = document.getElementById('promoMessage');
            const discountRow = document.getElementById('discountRow');
            const discountAmount = document.getElementById('discountAmount');
            const orderTotal = document.getElementById('orderTotal');
            
            const validCodes = {
                'WELCOME20': 0.20,
                'SAVE10': 0.10,
                'FREESHIP': 9.99,
                'FLASH50': 0.50,
                'DEMO100': 0.00  // Special demo code
            };
            
            if (validCodes[code]) {
                let discount = 0;
                if (code === 'FREESHIP') {
                    discount = 9.99;
                    message.innerHTML = '<span class="success-message">Free shipping applied! ($9.99 off)</span>';
                } else if (code === 'DEMO100') {
                    discount = totalAmount; // 100% off for demo
                    message.innerHTML = '<span class="success-message">🎉 DEMO100: Full discount applied! Total: $0.00</span>';
                } else {
                    discount = totalAmount * validCodes[code];
                    message.innerHTML = `<span class="success-message">${code}: ${validCodes[code]*100}% discount applied!</span>`;
                }
                
                discountApplied = discount;
                discountRow.style.display = 'flex';
                discountAmount.textContent = '-$' + discount.toFixed(2);
                orderTotal.textContent = '$' + (totalAmount - discount).toFixed(2);
                
                // Update the pay button
                document.querySelector('.installment-option.selected').click();
            } else if (code) {
                message.innerHTML = '<span class="error-message">Invalid promo code. Try WELCOME20 for 20% off</span>';
                discountRow.style.display = 'none';
                discountApplied = 0;
                orderTotal.textContent = '$' + totalAmount.toFixed(2);
            }
        }
        
        function processPayment() {
            // Basic validation
            const cardNumber = document.getElementById('cardNumber').value;
            const cardName = document.getElementById('cardName').value;
            const expiryDate = document.getElementById('expiryDate').value;
            const cvv = document.getElementById('cvv').value;
            
            if (!cardNumber || !cardName || !expiryDate || !cvv) {
                alert('Please fill in all required fields');
                return;
            }
            
            // Show processing overlay
            document.getElementById('processingOverlay').style.display = 'flex';
            const processingMessage = document.getElementById('processingMessage');
            
            // Simulate payment processing steps
            const steps = [
                'Validating demo card...',
                'Connecting to demo payment gateway...',
                'Processing demo transaction...',
                'Authorizing payment...',
                'Finalizing transaction...'
            ];
            
            let stepIndex = 0;
            const stepInterval = setInterval(() => {
                if (stepIndex < steps.length) {
                    processingMessage.textContent = steps[stepIndex];
                    stepIndex++;
                } else {
                    clearInterval(stepInterval);
                    
                    // Countdown before form submission
                    let count = 3;
                    const countdownElement = document.getElementById('countdown');
                    const countdownInterval = setInterval(() => {
                        countdownElement.textContent = count;
                        count--;
                        
                        if (count < 0) {
                            clearInterval(countdownInterval);
                            // Submit the form
                            document.getElementById('paymentForm').submit();
                        }
                    }, 1000);
                }
            }, 800);
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            selectInstallment(document.querySelector('.installment-option'), 'full');
            updateCardPreview();
            
            // Auto-fill demo data for easier testing
            document.getElementById('cardNumber').value = '4111 1111 1111 1111';
            document.getElementById('cardName').value = 'Demo Customer';
            document.getElementById('expiryDate').value = '12/28';
            document.getElementById('cvv').value = '123';
            updateCardPreview();
            
            // Add demo code suggestion
            document.getElementById('promoCode').placeholder = 'Try: WELCOME20 or DEMO100';
        });
    </script>
</body>
</html>
"""

SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Successful - Kastro Store</title>
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
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .demo-banner {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            text-align: center;
            padding: 10px;
            font-weight: 500;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1001;
        }
        
        .success-card {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 90%;
            animation: slideUp 0.5s ease-out;
            margin-top: 40px;
        }
        
        @keyframes slideUp {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .success-icon {
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
        
        h1 {
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
        
        .detail-item:last-child {
            border-bottom: none;
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
        
        .confetti {
            position: fixed;
            width: 10px;
            height: 10px;
            background: #ff6b6b;
            border-radius: 50%;
            animation: confetti-fall 3s linear infinite;
        }
        
        @keyframes confetti-fall {
            0% { transform: translateY(-100px) rotate(0deg); opacity: 1; }
            100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
        }
        
        .transaction-details {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin-top: 2rem;
            text-align: left;
            border: 2px solid #e2e8f0;
        }
        
        .transaction-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .transaction-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }
        
        .status-badge {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .status-success {
            background: #d4edda;
            color: #155724;
        }
        
        .security-note {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            font-size: 0.9rem;
            color: #4a5568;
            border-left: 4px solid #4CAF50;
        }
        
        .demo-note {
            background: #fff3cd;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            font-size: 0.9rem;
            color: #856404;
            border-left: 4px solid #ffc107;
        }
    </style>
</head>
<body>
    <div class="demo-banner">
        <i class="fas fa-check-circle"></i>
        DEMO TRANSACTION - This is a simulated payment
    </div>
    
    <div class="success-card">
        <div class="success-icon">🎉</div>
        <h1>Payment Successful!</h1>
        <p>Thank you for your purchase. Your order has been confirmed and is being processed.</p>
        
        <div class="demo-note">
            <i class="fas fa-info-circle"></i>
            This was a demo transaction. No real payment was processed.
        </div>
        
        <div class="transaction-details">
            <div class="transaction-header">
                <h3>Transaction Details</h3>
                <span class="status-badge status-success">SUCCESS</span>
            </div>
            <div class="transaction-item">
                <span>Transaction ID:</span>
                <span><strong>{{ transaction_id }}</strong></span>
            </div>
            <div class="transaction-item">
                <span>Authorization Code:</span>
                <span><strong>{{ auth_code }}</strong></span>
            </div>
            <div class="transaction-item">
                <span>Order ID:</span>
                <span><strong>{{ order_id }}</strong></span>
            </div>
            <div class="transaction-item">
                <span>Payment Method:</span>
                <span><strong>{{ payment_method }}</strong></span>
            </div>
            <div class="transaction-item">
                <span>Amount:</span>
                <span><strong>${{ amount }}</strong></span>
            </div>
            <div class="transaction-item">
                <span>Date & Time:</span>
                <span><strong>{{ timestamp }}</strong></span>
            </div>
        </div>
        
        <div class="order-details">
            <div class="detail-item">
                <span>Estimated Delivery:</span>
                <span><strong>{{ delivery_date }}</strong></span>
            </div>
            <div class="detail-item">
                <span>Tracking Number:</span>
                <span><strong>{{ tracking_number }}</strong></span>
            </div>
            <div class="detail-item">
                <span>Shipping Address:</span>
                <span><strong>123 Demo Street, Demo City</strong></span>
            </div>
            <div class="detail-item">
                <span>Customer Support:</span>
                <span><strong>support@kastrostore.com</strong></span>
            </div>
        </div>
        
        <div class="security-note">
            <i class="fas fa-shield-alt"></i> In a real transaction, a confirmation email would be sent to your registered email address.
        </div>
        
        <div class="buttons">
            <a href="/" class="btn btn-primary">
                <i class="fas fa-home"></i> Back to Home
            </a>
            <a href="#" class="btn btn-secondary" onclick="downloadInvoice()">
                <i class="fas fa-download"></i> Download Invoice
            </a>
            <a href="#" class="btn btn-secondary">
                <i class="fas fa-shopping-cart"></i> Continue Shopping
            </a>
        </div>
    </div>
    
    <script>
        // Create confetti effect
        function createConfetti() {
            const colors = ['#667eea', '#764ba2', '#ff6b6b', '#4CAF50', '#ffd700'];
            for (let i = 0; i < 50; i++) {
                const confetti = document.createElement('div');
                confetti.className = 'confetti';
                confetti.style.left = Math.random() * 100 + 'vw';
                confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.animationDelay = Math.random() * 2 + 's';
                document.body.appendChild(confetti);
                
                setTimeout(() => {
                    confetti.remove();
                }, 3000);
            }
        }
        
        function downloadInvoice() {
            alert('Demo invoice downloaded! Check your downloads folder.');
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            createConfetti();
            
            // Create more confetti every 2 seconds
            setInterval(() => {
                if (Math.random() > 0.7) {
                    createConfetti();
                }
            }, 2000);
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""
    
    if request.method == "POST":
        try:
            # Get form data
            amount = request.form.get("amount", "3769.18")
            payment_method = request.form.get("payment_method", "card")
            card_number = request.form.get("card_number", "").replace(' ', '')
            card_name = request.form.get("card_name", "")
            expiry_date = request.form.get("expiry_date", "")
            cvv = request.form.get("cvv", "")
            promo_code = request.form.get("promo_code", "")
            
            # Always succeed in demo mode
            print(f"Demo payment received: {card_name}, {card_number[-4:] if card_number else 'N/A'}")
            
            # Generate transaction details
            transaction_id = MockPaymentGateway.generate_transaction_id()
            auth_code = MockPaymentGateway.generate_auth_code()
            order_id = f"KASTRO{str(uuid.uuid4())[:8].upper()}"
            
            # Apply promo code if any
            final_amount = float(amount)
            valid_codes = {
                'WELCOME20': 0.20,
                'SAVE10': 0.10,
                'FREESHIP': 9.99,
                'FLASH50': 0.50,
                'DEMO100': 1.00  # 100% off
            }
            
            if promo_code.upper() in valid_codes:
                discount = valid_codes[promo_code.upper()]
                if promo_code.upper() == 'FREESHIP':
                    final_amount -= 9.99
                elif promo_code.upper() == 'DEMO100':
                    final_amount = 0.00  # Free for demo
                else:
                    final_amount *= (1 - discount)
            
            # Save to database (always succeeds)
            db = conn()
            try:
                with db.cursor() as cur:
                    cur.execute("""
                        INSERT INTO pay (amount, status, payment_method, order_id, 
                                        transaction_id, auth_code, card_last_four) 
                        VALUES (%s, 'completed', %s, %s, %s, %s, %s)
                    """, (final_amount, payment_method, order_id, transaction_id, 
                          auth_code, card_number[-4:] if card_number else 'DEMO'))
                    db.commit()
            except Exception as db_error:
                print(f"Database error (non-critical in demo): {db_error}")
                # Continue anyway since this is a demo
            
            # Redirect to success page
            return redirect(f"/success?order_id={order_id}&transaction_id={transaction_id}" +
                          f"&auth_code={auth_code}&amount={final_amount}" +
                          f"&payment_method={payment_method}")
            
        except Exception as e:
            print(f"Error in payment processing: {e}")
            # Even if there's an error, redirect to success in demo mode
            return redirect(f"/success?order_id=KASTRODEMO&transaction_id=TXN{str(uuid.uuid4())[:8].upper()}" +
                          f"&auth_code=AUTHDEMO&amount=3769.18&payment_method=card")
    
    return render_template_string(PAYMENT_TEMPLATE, msg=msg)

@app.route("/success")
def success():
    # Get transaction details from URL parameters or generate defaults
    order_id = request.args.get('order_id', f"KASTRO{str(uuid.uuid4())[:8].upper()}")
    transaction_id = request.args.get('transaction_id', MockPaymentGateway.generate_transaction_id())
    auth_code = request.args.get('auth_code', MockPaymentGateway.generate_auth_code())
    amount = request.args.get('amount', '3769.18')
    payment_method = request.args.get('payment_method', 'Credit Card')
    
    # Format payment method display
    if payment_method == 'card':
        payment_method_display = 'Credit Card (Demo)'
    elif payment_method == 'paypal':
        payment_method_display = 'PayPal (Demo)'
    else:
        payment_method_display = f'{payment_method.capitalize()} (Demo)'
    
    # Generate delivery details
    delivery_date = (datetime.now() + timedelta(days=3)).strftime("%B %d, %Y")
    tracking_number = f"TRK{str(uuid.uuid4())[:8].upper()}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template_string(SUCCESS_TEMPLATE,
                                 order_id=order_id,
                                 transaction_id=transaction_id,
                                 auth_code=auth_code,
                                 payment_method=payment_method_display,
                                 amount=amount,
                                 delivery_date=delivery_date,
                                 tracking_number=tracking_number,
                                 timestamp=timestamp)

if __name__ == "__main__":
    # Initialize database on startup
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
