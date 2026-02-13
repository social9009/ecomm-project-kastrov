from flask import Flask, request, render_template_string, redirect, jsonify
import pymysql
import time
from datetime import datetime

app = Flask(__name__)

# Database connection function remains the same
def conn():
    return pymysql.connect(
        host="mysql-users",
        user="root",
        password="password",
        database="usersdb"
    )

# Enhanced User Registration Template
USER_REGISTRATION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Account - Kastro Store</title>
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
        
        .container {
            display: flex;
            max-width: 1200px;
            width: 100%;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .left-panel {
            flex: 1;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .right-panel {
            flex: 1;
            padding: 3rem;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 2rem;
        }
        
        .logo i {
            font-size: 2.5rem;
        }
        
        .benefits {
            list-style: none;
            margin-top: 2rem;
        }
        
        .benefits li {
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .benefits i {
            color: #4CAF50;
        }
        
        .registration-form {
            width: 100%;
        }
        
        .form-header {
            margin-bottom: 2rem;
        }
        
        .form-header h1 {
            color: #2d3748;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .form-header p {
            color: #4a5568;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #2d3748;
            font-weight: 500;
        }
        
        .input-with-icon {
            position: relative;
        }
        
        .input-with-icon i {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #a0aec0;
        }
        
        .input-with-icon input,
        .input-with-icon select {
            width: 100%;
            padding: 12px 15px 12px 45px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        
        .input-with-icon input:focus,
        .input-with-icon select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .form-row {
            display: flex;
            gap: 1rem;
        }
        
        .form-row .form-group {
            flex: 1;
        }
        
        .password-strength {
            height: 4px;
            background: #e2e8f0;
            border-radius: 2px;
            margin-top: 5px;
            overflow: hidden;
        }
        
        .strength-bar {
            height: 100%;
            width: 0%;
            transition: width 0.3s, background 0.3s;
        }
        
        .terms {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 2rem;
        }
        
        .terms input {
            width: 18px;
            height: 18px;
        }
        
        .btn-submit {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }
        
        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .login-link {
            text-align: center;
            margin-top: 1.5rem;
            color: #4a5568;
        }
        
        .login-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .social-login {
            margin-top: 2rem;
            text-align: center;
        }
        
        .social-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 1rem;
        }
        
        .social-btn {
            flex: 1;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-weight: 500;
        }
        
        .social-btn:hover {
            border-color: #667eea;
            transform: translateY(-2px);
        }
        
        .message {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            display: none;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .progress-steps {
            display: flex;
            justify-content: space-between;
            margin-bottom: 2rem;
            position: relative;
        }
        
        .progress-steps:before {
            content: '';
            position: absolute;
            top: 15px;
            left: 0;
            right: 0;
            height: 2px;
            background: #e2e8f0;
            z-index: 1;
        }
        
        .step {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            z-index: 2;
        }
        
        .step-circle {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: white;
            border: 2px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            color: #a0aec0;
            margin-bottom: 0.5rem;
        }
        
        .step.active .step-circle {
            background: #667eea;
            border-color: #667eea;
            color: white;
        }
        
        .step-label {
            font-size: 0.8rem;
            color: #a0aec0;
        }
        
        .step.active .step-label {
            color: #667eea;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="left-panel">
            <div class="logo">
                <i class="fas fa-store"></i>
                Kastro's Store
            </div>
            
            <h2>Join Our Community</h2>
            <p>Become part of 100,000+ satisfied customers</p>
            
            <ul class="benefits">
                <li><i class="fas fa-check-circle"></i> Exclusive member-only deals</li>
                <li><i class="fas fa-check-circle"></i> Faster checkout process</li>
                <li><i class="fas fa-check-circle"></i> Order tracking & history</li>
                <li><i class="fas fa-check-circle"></i> Early access to sales</li>
                <li><i class="fas fa-check-circle"></i> Personalized recommendations</li>
            </ul>
            
            <div style="margin-top: auto;">
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                    <p style="font-size: 0.9rem; opacity: 0.9;">
                        <i class="fas fa-lock"></i> Your information is secured with 256-bit SSL encryption
                    </p>
                </div>
            </div>
        </div>
        
        <div class="right-panel">
            <div class="progress-steps">
                <div class="step active">
                    <div class="step-circle">1</div>
                    <div class="step-label">Account</div>
                </div>
                <div class="step">
                    <div class="step-circle">2</div>
                    <div class="step-label">Profile</div>
                </div>
                <div class="step">
                    <div class="step-circle">3</div>
                    <div class="step-label">Preferences</div>
                </div>
                <div class="step">
                    <div class="step-circle">4</div>
                    <div class="step-label">Complete</div>
                </div>
            </div>
            
            <div class="form-header">
                <h1>Create Your Account</h1>
                <p>Fill in your details to get started</p>
            </div>
            
            {% if msg %}
            <div class="message success" id="message">
                {{ msg }} <i class="fas fa-check-circle"></i>
            </div>
            {% endif %}
            
            <form method="post" class="registration-form" onsubmit="return validateForm()">
                <div class="form-row">
                    <div class="form-group">
                        <label for="firstName">First Name *</label>
                        <div class="input-with-icon">
                            <i class="fas fa-user"></i>
                            <input type="text" id="firstName" name="firstName" placeholder="John" required>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="lastName">Last Name *</label>
                        <div class="input-with-icon">
                            <i class="fas fa-user"></i>
                            <input type="text" id="lastName" name="lastName" placeholder="Doe" required>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="username">Username *</label>
                    <div class="input-with-icon">
                        <i class="fas fa-at"></i>
                        <input type="text" id="username" name="username" placeholder="johndoe" required>
                    </div>
                    <small id="usernameHelp" style="color: #a0aec0; display: block; margin-top: 5px;">
                        This will be your public display name
                    </small>
                </div>
                
                <div class="form-group">
                    <label for="email">Email Address *</label>
                    <div class="input-with-icon">
                        <i class="fas fa-envelope"></i>
                        <input type="email" id="email" name="email" placeholder="john@example.com" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="password">Password *</label>
                    <div class="input-with-icon">
                        <i class="fas fa-lock"></i>
                        <input type="password" id="password" name="password" placeholder="••••••••" required 
                               onkeyup="checkPasswordStrength()">
                    </div>
                    <div class="password-strength">
                        <div class="strength-bar" id="strengthBar"></div>
                    </div>
                    <small id="passwordHelp" style="color: #a0aec0; display: block; margin-top: 5px;">
                        Must be at least 8 characters with letters and numbers
                    </small>
                </div>
                
                <div class="form-group">
                    <label for="phone">Phone Number</label>
                    <div class="input-with-icon">
                        <i class="fas fa-phone"></i>
                        <input type="tel" id="phone" name="phone" placeholder="+1 (555) 123-4567">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="country">Country</label>
                    <div class="input-with-icon">
                        <i class="fas fa-globe"></i>
                        <select id="country" name="country">
                            <option value="">Select Country</option>
                            <option value="US">United States</option>
                            <option value="CA">Canada</option>
                            <option value="UK">United Kingdom</option>
                            <option value="AU">Australia</option>
                        </select>
                    </div>
                </div>
                
                <div class="terms">
                    <input type="checkbox" id="terms" name="terms" required>
                    <label for="terms">
                        I agree to the <a href="#" style="color: #667eea;">Terms of Service</a> and 
                        <a href="#" style="color: #667eea;">Privacy Policy</a>
                    </label>
                </div>
                
                <div class="terms">
                    <input type="checkbox" id="newsletter" name="newsletter" checked>
                    <label for="newsletter">
                        Send me exclusive offers and updates via email
                    </label>
                </div>
                
                <button type="submit" class="btn-submit">
                    <i class="fas fa-user-plus"></i> Create Account
                </button>
            </form>
            
            <div class="social-login">
                <p style="color: #a0aec0; margin-bottom: 1rem;">Or sign up with</p>
                <div class="social-buttons">
                    <button type="button" class="social-btn">
                        <i class="fab fa-google" style="color: #DB4437;"></i> Google
                    </button>
                    <button type="button" class="social-btn">
                        <i class="fab fa-facebook-f" style="color: #4267B2;"></i> Facebook
                    </button>
                </div>
            </div>
            
            <div class="login-link">
                Already have an account? <a href="#">Sign in here</a>
            </div>
        </div>
    </div>
    
    <script>
        function checkPasswordStrength() {
            const password = document.getElementById('password').value;
            const bar = document.getElementById('strengthBar');
            let strength = 0;
            
            if (password.length >= 8) strength += 25;
            if (/[A-Z]/.test(password)) strength += 25;
            if (/[0-9]/.test(password)) strength += 25;
            if (/[^A-Za-z0-9]/.test(password)) strength += 25;
            
            bar.style.width = strength + '%';
            
            if (strength < 50) bar.style.background = '#ff6b6b';
            else if (strength < 75) bar.style.background = '#ffa500';
            else bar.style.background = '#4CAF50';
        }
        
        function validateForm() {
            const password = document.getElementById('password').value;
            const terms = document.getElementById('terms').checked;
            
            if (password.length < 8) {
                alert('Password must be at least 8 characters long');
                return false;
            }
            
            if (!terms) {
                alert('You must agree to the terms and conditions');
                return false;
            }
            
            // Simulate registration
            document.querySelector('.step:nth-child(1)').classList.remove('active');
            document.querySelector('.step:nth-child(2)').classList.add('active');
            
            // Show message if any
            const message = document.getElementById('message');
            if (message) {
                message.style.display = 'block';
            }
            
            return true;
        }
        
        // Real-time username availability check (simulated)
        document.getElementById('username').addEventListener('input', function(e) {
            const username = e.target.value;
            if (username.length > 2) {
                // Simulate API call
                setTimeout(() => {
                    const helpText = document.getElementById('usernameHelp');
                    if (username.toLowerCase().includes('admin')) {
                        helpText.textContent = 'Username not available';
                        helpText.style.color = '#ff6b6b';
                    } else {
                        helpText.textContent = 'Username available ✓';
                        helpText.style.color = '#4CAF50';
                    }
                }, 500);
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        c = conn()
        with c.cursor() as cur:
            cur.execute("INSERT INTO users (username) VALUES (%s)", (username,))
            c.commit()
        msg = "Welcome to Kastro Store! Your account has been created successfully!"
    return render_template_string(USER_REGISTRATION_TEMPLATE, msg=msg)

@app.route("/cart-direct")
def cart_direct():
    return redirect("/cart/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
