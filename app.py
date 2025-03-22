import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
from atm import ATM

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_atm_secret_key")

# Initialize ATM
atm = ATM()

@app.route('/')
def index():
    if 'account_number' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    account_number = request.form.get('account_number')
    pin = request.form.get('pin')
    
    # Validate login
    if atm.authenticate(account_number, pin):
        session['account_number'] = account_number
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid account number or PIN!', 'danger')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'account_number' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('index'))
    
    account_number = session['account_number']
    balance = atm.check_balance(account_number)
    return render_template('dashboard.html', 
                           account_number=account_number, 
                           balance=balance)

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'account_number' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('index'))
    
    amount = float(request.form.get('amount', 0))
    
    if amount <= 0:
        flash('Please enter a valid amount!', 'danger')
    else:
        result = atm.withdraw(session['account_number'], amount)
        if result['success']:
            flash(f'Successfully withdrew ${amount:.2f}', 'success')
        else:
            flash(result['message'], 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/deposit', methods=['POST'])
def deposit():
    if 'account_number' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('index'))
    
    amount = float(request.form.get('amount', 0))
    
    if amount <= 0:
        flash('Please enter a valid amount!', 'danger')
    else:
        result = atm.deposit(session['account_number'], amount)
        if result['success']:
            flash(f'Successfully deposited ${amount:.2f}', 'success')
        else:
            flash(result['message'], 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/history')
def history():
    if 'account_number' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('index'))
    
    transactions = atm.get_transactions(session['account_number'])
    return render_template('history.html', 
                           account_number=session['account_number'], 
                           transactions=transactions)

@app.route('/change-pin', methods=['GET', 'POST'])
def change_pin():
    if 'account_number' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        current_pin = request.form.get('current_pin')
        new_pin = request.form.get('new_pin')
        confirm_pin = request.form.get('confirm_pin')
        
        # Validate input
        if not current_pin or not new_pin or not confirm_pin:
            flash('All fields are required!', 'danger')
        elif new_pin != confirm_pin:
            flash('New PIN and confirmation do not match!', 'danger')
        else:
            # Attempt to change PIN
            result = atm.change_pin(session['account_number'], current_pin, new_pin)
            if result['success']:
                flash(result['message'], 'success')
                return redirect(url_for('dashboard'))
            else:
                flash(result['message'], 'danger')
    
    return render_template('change_pin.html', account_number=session['account_number'])

@app.route('/logout')
def logout():
    session.pop('account_number', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('login.html'), 404

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'account_number' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        to_account = request.form.get('to_account')
        amount_str = request.form.get('amount')
        
        # Validate inputs
        if not to_account or not amount_str:
            flash('All fields are required!', 'danger')
            return render_template('transfer.html', account_number=session['account_number'])
        
        try:
            amount = float(amount_str)
        except ValueError:
            flash('Amount must be a valid number!', 'danger')
            return render_template('transfer.html', account_number=session['account_number'])
        
        if amount <= 0:
            flash('Amount must be greater than zero!', 'danger')
            return render_template('transfer.html', account_number=session['account_number'])
        
        # Process transfer
        result = atm.transfer(session['account_number'], to_account, amount)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('transfer.html', account_number=session['account_number'])

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('login.html'), 500
