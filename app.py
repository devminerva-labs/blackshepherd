import os 
from flask import Flask, render_template, request, redirect, url_for, flash, current_app, get_flashed_messages
from datetime import datetime, timezone
from models import db, Campaign, Transaction
from payments import initialize_paystack_payment, verify_paystack_payment, test_paystack_connection, handle_paystack_webhook, format_amount
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# PUBLIC ROUTES
@app.route('/')
def index():
    """Homepage with featured campaigns"""
    campaigns = Campaign.query.filter_by(is_active=True).limit(3).all()
    return render_template('index.html', campaigns=campaigns, config=Config)

@app.route('/about')
def about():
    """About page with mission and team"""
    return render_template('about.html', config=Config)

@app.route('/campaigns')
def campaigns():
    """All active campaigns"""
    all_campaigns = Campaign.query.filter_by(is_active=True).all()
    return render_template('campaigns.html', campaigns=all_campaigns, config=Config)

@app.route('/campaign/<int:id>')
def campaign(id):
    """Single campaign page with donation form"""
    campaign = Campaign.query.get_or_404(id)
    progress_percentage = (campaign.raised_amount / campaign.goal_amount) * 100 if campaign.goal_amount > 0 else 0
    return render_template('campaign.html', campaign=campaign, progress=progress_percentage, config=Config)

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html', config=Config)

# ADMIN/TESTING ROUTES (for development)
@app.route('/add-test-campaign')
def add_test_campaign():
    """Add a test campaign to verify database works"""
    # Check if campaign already exists
    existing = Campaign.query.filter_by(title='Clean Water Access Project').first()
    if existing:
        flash('Test campaign already exists!', 'info')
        return redirect(url_for('campaigns'))
    
    test_campaign = Campaign(
        title='Clean Water Access Project',
        description='Providing clean, safe drinking water to rural communities across Nigeria. Every donation helps us install water pumps, purification systems, and educate communities about water safety.',
        goal_amount=1000000.0,  # NGN 1,000,000
        raised_amount=125000.0,  # NGN 125,000 (starting progress)
        currency='NGN',
        image_filename='water.jpg'
    )
    
    db.session.add(test_campaign)
    db.session.commit()
    
    flash('Test campaign created successfully!', 'success')
    return redirect(url_for('campaigns'))

@app.route('/test-paystack')
def test_paystack():
    """Test Paystack connection"""
    result = test_paystack_connection()
    
    if result['success']:
        flash(f"Paystack connected successfully! {result['message']}", 'success')
    else:
        flash(f"Paystack connection failed: {result['message']}", 'error')
    
    return redirect(url_for('index'))

# DONATION PROCESSING ROUTES
@app.route('/process-donation', methods=['POST'])
def process_donation():
    """Handle donation form submission"""
    try:
        # Handle custom amount or preset amount
        if request.form.get('amount') == 'custom':
            amount = float(request.form.get('custom_amount', 0))
        else:
            amount = float(request.form.get('amount', 0))
            
        currency = request.form.get('currency', 'NGN')
        campaign_id = int(request.form.get('campaign_id'))
        
        # Validate input
        if amount <= 0:
            flash('Please enter a valid donation amount', 'error')
            return redirect(url_for('campaign', id=campaign_id))
        
        if currency == 'NGN' and amount < 100:
            flash('Minimum donation amount is ₦100', 'error')
            return redirect(url_for('campaign', id=campaign_id))
        
        # Create pending transaction record
        transaction = Transaction(
            amount=amount,
            currency=currency,
            campaign_id=campaign_id,
            status='pending',
            payment_method='paystack'
        )
        db.session.add(transaction)
        db.session.commit()
        
        # Initialize Paystack payment
        result = initialize_paystack_payment(transaction)
        
        if result['success']:
            # Update transaction with Paystack reference
            transaction.transaction_id = result['transaction_id']
            db.session.commit()
            
            current_app.logger.info(f"Redirecting to Paystack: {result['redirect_url']}")
            # Redirect to Paystack payment page
            return redirect(result['redirect_url'])
        else:
            current_app.logger.error(f"Payment initialization failed: {result.get('error')}")
            flash(f"Payment failed: {result.get('error', 'Unknown error')}", 'error')
            return redirect(url_for('donate_error'))
            
    except ValueError as e:
        current_app.logger.error(f"Invalid amount: {str(e)}")
        flash('Please enter a valid amount', 'error')
        return redirect(url_for('campaign', id=campaign_id))
    except Exception as e:
        current_app.logger.error(f"Donation processing error: {str(e)}")
        flash('An error occurred processing your donation. Please try again.', 'error')
        return redirect(url_for('donate_error'))

# Paystack callback routes
@app.route('/paystack/callback')
def paystack_callback():
    """Handle Paystack payment callback"""
    reference = request.args.get('reference')
    
    if not reference:
        flash('Invalid payment response', 'error')
        return redirect(url_for('donate_error'))
    
    current_app.logger.info(f"Processing Paystack callback for reference: {reference}")
    
    # Verify payment with Paystack
    result = verify_paystack_payment(reference)
    
    if result['success']:
        # Find our transaction record
        transaction_db_id = result.get('transaction_db_id')
        
        if transaction_db_id:
            try:
                transaction = db.session.get(Transaction, int(transaction_db_id))
                if transaction and transaction.status != 'success':
                    # Update transaction status
                    transaction.status = 'success'
                    transaction.completed_at = datetime.now(timezone.utc)
                    
                    # Update campaign total
                    campaign = db.session.get(Campaign, transaction.campaign_id)
                    campaign.raised_amount += transaction.amount
                    
                    db.session.commit()
                    
                    current_app.logger.info(f"Transaction {reference} completed successfully")
                    return redirect(url_for('donate_success', transaction_id=reference))
                else:
                    current_app.logger.warning(f"Transaction {reference} already processed or not found")
                    return redirect(url_for('donate_success', transaction_id=reference))
            except Exception as e:
                current_app.logger.error(f"Database error processing transaction: {str(e)}")
                db.session.rollback()
    
    # If verification failed
    current_app.logger.error(f"Payment verification failed for reference: {reference}")
    flash('Payment verification failed', 'error')
    return redirect(url_for('donate_error'))

@app.route('/paystack/webhook', methods=['POST'])
def paystack_webhook():
    """Handle Paystack webhook notifications"""
    try:
        current_app.logger.info("Received Paystack webhook")
        result = handle_paystack_webhook(request)
        
        if result['success']:
            # Find and update transaction
            transaction_db_id = result.get('transaction_db_id')
            
            if transaction_db_id:
                transaction = db.session.get(Transaction, int(transaction_db_id))
                if transaction and transaction.status != 'success':
                    transaction.status = 'success'
                    transaction.completed_at = datetime.now(timezone.utc)
                    
                    # Update campaign total
                    campaign = db.session.get(Campaign, transaction.campaign_id)
                    campaign.raised_amount += transaction.amount
                    
                    db.session.commit()
                    current_app.logger.info(f"Webhook processed successfully for reference: {result.get('reference')}")
        
        return 'OK', 200
        
    except Exception as e:
        current_app.logger.error(f"Webhook error: {str(e)}")
        return 'Error', 400

@app.route('/donate/success/<transaction_id>')
def donate_success(transaction_id):
    """Payment success page"""
    # Find transaction by Paystack reference
    transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
    
    if not transaction:
        flash('Transaction not found', 'error')
        return redirect(url_for('index'))
    
    campaign = db.session.get(Campaign, transaction.campaign_id)
    return render_template('donate_success.html', transaction=transaction, campaign=campaign, config=Config)

@app.route('/donate/error')
def donate_error():
    """Payment error page"""
    return render_template('donate_error.html', config=Config)

# ERROR HANDLERS
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', config=Config), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', config=Config), 500

# TEMPLATE FILTERS
@app.template_filter('currency')
def currency_filter(amount, currency='NGN'):
    """Format currency for templates"""
    return format_amount(amount, currency)

@app.template_filter('percentage')
def percentage_filter(value, decimals=1):
    """Format percentage for templates"""
    return f"{value:.{decimals}f}%"

# TEMPLATE GLOBALS
@app.template_global()
def get_flashed_messages_with_categories():
    """Get flashed messages with categories for templates"""
    return get_flashed_messages(with_categories=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("🗄️  Database tables created successfully!")
        print("💳 Paystack integration ready (Direct HTTP)!")
        print("🌐 Supports NGN + international cards!")
        print("🎨 Modern responsive templates loaded!")
        print("🚀 Starting server...")
    
    # Production settings for Render
    port = int(os.environ.get('PORT', 5000))  # ← This needs 'os'
    debug_mode = os.environ.get('FLASK_ENV') != 'production'  # ← This too
    app.run(debug=debug_mode, host='0.0.0.0', port=port)    




rg&gp#h6(eog(@aw*@%)ve^+@%y=ov5!^bb*p-pq!h!r1q01%e