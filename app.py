import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from datetime import datetime
from config import Config

# Import payment functions from your existing payments.py
from payments import (
    initialize_paystack_payment, 
    verify_paystack_payment, 
    test_paystack_connection,
    format_amount
)

app = Flask(__name__)
app.config.from_object(Config)

# Static campaign data (no database needed)
CAMPAIGNS = {
    1: {
        'id': 1,
        'title': 'Kubwa Hospital Outreach',
        'description': 'Shining a Light in Kubwa: Compassionate hospital outreach providing medical supplies, settling hospital bills, and supporting pregnant and nursing mothers with essential food items.',
        'long_description': '''
        On October 26, 2024, the Blak Shepherd Foundation embarked on a compassionate outreach program at Kubwa Hospital in Abuja, Nigeria. This initiative addressed the pressing needs of pregnant and nursing mothers as well as the broader community.
        
        Our team settled outstanding hospital bills for over 20 mothers, distributed hundreds of bags containing essential food items, and provided medical supplies to families facing financial hardships. The outreach created meaningful connections between our foundation team, healthcare workers, and families, enhancing community solidarity.
        
        This program alleviated immediate financial burdens and food insecurity while fostering hope and dignity among vulnerable mothers and families.
        ''',
        'goal_amount': 4000000,  # ₦4,000,000
        'raised_amount': 1950000,  # ₦1,950,000
        'currency': 'NGN',
        'main_image': 'campaigns/kubwa-hospital-outreach/main.jpg',
        'gallery_images': [
            'campaigns/kubwa-hospital-outreach/gallery-1.jpg',
            'campaigns/kubwa-hospital-outreach/gallery-2.jpg',
            'campaigns/kubwa-hospital-outreach/gallery-3.jpg',
            'campaigns/kubwa-hospital-outreach/gallery-4.jpg',
            'campaigns/kubwa-hospital-outreach/gallery-5.jpg'
        ],
        'impact_stats': {
            'families_helped': 50,
            'bills_settled': 20,
            'food_bags_distributed': 200,
            'mothers_supported': 45
        },
        'date': datetime(2024, 10, 26),
        'location': 'Kubwa Hospital, Abuja'
    },
    2: {
        'id': 2,
        'title': 'Utako Food Drive',
        'description': 'Christmas a time for giving: Annual Christmas Food Drive bringing joy and sustenance to underprivileged families during the festive season with food packs and hygiene care packages.',
        'long_description': '''
        The Christmas Food Drive organized by the Blak Shepherd Foundation took place at the Utako Community Square on December 25, 2024, aiming to bring joy and sustenance to underprivileged families during the festive season.
        
        With a focus on ensuring that everyone in the community could celebrate Christmas with dignity, the event provided not only food packs but also hygiene care packages. Children participated in educational competitions including spelling contests, receiving gifts such as painting supplies and coloring books.
        
        The involvement of community leaders and the Nigerian Police Force Utako Division was instrumental in ensuring a smooth and safe experience for all participants. The event successfully attracted diverse attendees and strengthened community ties through shared experiences of joy and giving.
        ''',
        'goal_amount': 1500000,  # ₦1,500,000
        'raised_amount': 1050000,  # ₦1,050,000
        'currency': 'NGN',
        'main_image': 'campaigns/utako-food-drive/main.jpg',
        'gallery_images': [
            'campaigns/utako-food-drive/gallery-1.jpg',
            'campaigns/utako-food-drive/gallery-2.jpg',
            'campaigns/utako-food-drive/gallery-3.jpg',
            'campaigns/utako-food-drive/gallery-4.jpg',
            'campaigns/utako-food-drive/gallery-5.jpg'
        ],
        'impact_stats': {
            'families_served': 150,
            'food_packs_distributed': 200,
            'children_participated': 75,
            'hygiene_packages': 100
        },
        'date': datetime(2024, 12, 25),
        'location': 'Utako Community Square, Abuja'
    },
    3: {
        'id': 3,
        'title': 'SS3 Students Scholarship Program',
        'description': 'Sensitization and Scholarship Program for SS3 Students: Empowering young women through education, mentorship, and financial assistance for WAEC and NECO examinations.',
        'long_description': '''
        Blak Shepherd Foundation, in collaboration with The Voice Against Gun Violence and LVP Ventures, launched a comprehensive program for SS3 students at Federal Government Girls' College, Bwari.
        
        This initiative focuses on Sexual Assault Awareness and Prevention during April - Sexual Assault Awareness Month. The program provides sensitization on awareness, prevention strategies, reporting mechanisms, and available support systems.
        
        In addition to sensitization efforts, we provide financial assistance by sponsoring West African Examinations Council (WAEC) and National Examinations Council (NECO) fees for eligible SS3 students, along with essential supplies such as toiletries to enhance their welfare.
        
        Our goal is to make a lasting impact on the lives of these young women through education, mentorship, and targeted welfare initiatives.
        ''',
        'goal_amount': 2500000,  # ₦2,500,000
        'raised_amount': 1000000,  # ₦1,000,000
        'currency': 'NGN',
        'main_image': 'campaigns/ss3-scholarship-program/main.jpg',
        'gallery_images': [
            'campaigns/ss3-scholarship-program/gallery-1.jpg',
            'campaigns/ss3-scholarship-program/gallery-2.jpg',
            'campaigns/ss3-scholarship-program/gallery-3.jpg',
            'campaigns/ss3-scholarship-program/gallery-4.jpg',
            'campaigns/ss3-scholarship-program/gallery-5.jpg'
        ],
        'impact_stats': {
            'students_supported': 120,
            'exam_fees_sponsored': 85,
            'sensitization_sessions': 12,
            'toiletries_distributed': 150
        },
        'date': datetime(2024, 4, 15),
        'location': 'Federal Government Girls\' College, Bwari'
    }
}

# Foundation statistics
FOUNDATION_STATS = {
    'total_campaigns': 3,
    'total_raised': 4000000,  # ₦4,000,000
    'lives_impacted': 320,    # Sum of all people helped across campaigns
    'communities_served': 3,
    'active_volunteers': 25
}

# Partner organizations
PARTNERS = [
    {
        'name': 'LVP Ventures',
        'logo': 'partners/lvp-ventures.png',
        'description': 'Strategic partner supporting educational initiatives',
        'location': 'USA'
    },
    {
        'name': 'The Voice Against Gun Violence',
        'logo': 'partners/voice-against-gun-violence.png',
        'description': 'Collaborative partner in awareness and advocacy programs',
        'location': 'Nigeria'
    }
]

# HOME PAGE
@app.route('/')
def index():
    """Homepage with featured campaigns and foundation overview"""
    # Get featured campaigns (limit to 3 for homepage)
    featured_campaigns = []
    for campaign in list(CAMPAIGNS.values())[:3]:
        # Add progress_percentage to each campaign
        campaign_with_progress = campaign.copy()
        campaign_with_progress['progress_percentage'] = (campaign['raised_amount'] / campaign['goal_amount']) * 100 if campaign['goal_amount'] > 0 else 0
        featured_campaigns.append(campaign_with_progress)
    
    return render_template('index.html', 
                         campaigns=featured_campaigns, 
                         stats=FOUNDATION_STATS)

# ABOUT PAGE
@app.route('/about')
def about():
    """About page with mission, team, and partner information"""
    return render_template('about.html', 
                         partners=PARTNERS,
                         stats=FOUNDATION_STATS)

# CAMPAIGNS LISTING PAGE
@app.route('/campaigns')
def campaigns():
    """All campaigns listing page"""
    all_campaigns = []
    for campaign in CAMPAIGNS.values():
        # Add progress_percentage to each campaign
        campaign_with_progress = campaign.copy()
        campaign_with_progress['progress_percentage'] = (campaign['raised_amount'] / campaign['goal_amount']) * 100 if campaign['goal_amount'] > 0 else 0
        all_campaigns.append(campaign_with_progress)
    
    # Calculate additional stats for campaigns page
    total_goal = sum(campaign['goal_amount'] for campaign in all_campaigns)
    total_raised = sum(campaign['raised_amount'] for campaign in all_campaigns)
    total_supporters = sum(campaign['impact_stats'].get('families_helped', 0) + 
                          campaign['impact_stats'].get('families_served', 0) +
                          campaign['impact_stats'].get('students_supported', 0) 
                          for campaign in all_campaigns)
    
    campaigns_stats = {
        'total_campaigns': len(all_campaigns),
        'total_goal': total_goal,
        'total_raised': total_raised,
        'total_supporters': total_supporters
    }
    
    return render_template('campaigns.html', 
                         campaigns=all_campaigns,
                         stats=campaigns_stats)

# INDIVIDUAL CAMPAIGN PAGE
@app.route('/campaign/<int:campaign_id>')
def campaign(campaign_id):
    """Individual campaign page with image gallery and donation form"""
    if campaign_id not in CAMPAIGNS:
        abort(404)
    
    campaign_data = CAMPAIGNS[campaign_id]
    
    # Calculate progress percentage
    progress = (campaign_data['raised_amount'] / campaign_data['goal_amount']) * 100 if campaign_data['goal_amount'] > 0 else 0
    
    return render_template('campaign.html', 
                         campaign=campaign_data,
                         progress=progress)

# CONTACT PAGE
@app.route('/contact')
def contact():
    """Contact page with foundation contact information"""
    contact_info = {
        'phone': '+234 912 421 1336',
        'email': 'blakshepherdwef@gmail.com',
        'instagram': {
            'handle': '@blakshepardwef',
            'url': 'https://www.instagram.com/blakshepardwef?utm_source=ig_web_button_share_sheet&igsh=MWIyNXpkazd1M2NkeQ=='
        },
        'address': {
            'street': '123 Foundation Street',
            'city': 'Garki, Abuja FCT',
            'country': 'Nigeria'
        },
        'office_hours': {
            'weekdays': 'Monday - Friday: 9:00 AM - 5:00 PM',
            'saturday': 'Saturday: 10:00 AM - 2:00 PM',
            'sunday': 'Sunday: Closed'
        }
    }
    
    return render_template('contact.html', contact=contact_info)

# PAYMENT PROCESSING - FIXED VERSION
@app.route('/process-donation', methods=['POST'])
def process_donation():
    """Handle donation form submission and redirect to Paystack"""
    try:
        # Get form data
        campaign_id = int(request.form.get('campaign_id'))
        email = request.form.get('email')  # Get email from form
        
        # Validate email
        if not email:
            flash('Email address is required for donation receipt', 'error')
            return redirect(url_for('campaign', campaign_id=campaign_id))
        
        # Handle custom amount or preset amount
        if request.form.get('amount') == 'custom':
            amount = float(request.form.get('custom_amount', 0))
        else:
            amount = float(request.form.get('amount', 0))
            
        currency = request.form.get('currency', 'NGN')
        
        # Validate campaign exists
        if campaign_id not in CAMPAIGNS:
            flash('Invalid campaign selected', 'error')
            return redirect(url_for('campaigns'))
        
        # Validate input
        if amount <= 0:
            flash('Please enter a valid donation amount', 'error')
            return redirect(url_for('campaign', campaign_id=campaign_id))
        
        if currency == 'NGN' and amount < 100:
            flash('Minimum donation amount is ₦100', 'error')
            return redirect(url_for('campaign', campaign_id=campaign_id))
        
        # Get campaign info
        campaign_data = CAMPAIGNS[campaign_id]
        
        # Create donation data dictionary (NOT Transaction object)
        donation_data = {
            'amount': amount,
            'currency': currency,
            'campaign_id': campaign_id,
            'campaign_title': campaign_data['title'],
            'email': email,
            'callback_url': url_for('paystack_callback', _external=True)
        }
        
        # Initialize Paystack payment (using your existing function)
        result = initialize_paystack_payment(donation_data)
        
        if result['success']:
            app.logger.info(f"Redirecting to Paystack: {result.get('authorization_url')}")
            return redirect(result['authorization_url'])
        else:
            app.logger.error(f"Payment initialization failed: {result.get('error')}")
            flash(f"Payment failed: {result.get('error', 'Unknown error')}", 'error')
            return redirect(url_for('donate_error'))
            
    except ValueError as e:
        app.logger.error(f"Invalid amount: {str(e)}")
        flash('Please enter a valid amount', 'error')
        return redirect(url_for('campaign', campaign_id=campaign_id))
    except Exception as e:
        app.logger.error(f"Donation processing error: {str(e)}")
        flash('An error occurred processing your donation. Please try again.', 'error')
        return redirect(url_for('donate_error'))

# PAYMENT CALLBACK (using your existing callback logic)
@app.route('/paystack/callback')
def paystack_callback():
    """Handle Paystack payment callback"""
    reference = request.args.get('reference')
    
    if not reference:
        flash('Invalid payment response', 'error')
        return redirect(url_for('donate_error'))
    
    app.logger.info(f"Processing Paystack callback for reference: {reference}")
    
    # Verify payment with Paystack (using your existing function)
    result = verify_paystack_payment(reference)
    
    if result['success']:
        app.logger.info(f"Transaction {reference} completed successfully")
        return redirect(url_for('donate_success', transaction_id=reference))
    else:
        app.logger.error(f"Payment verification failed for reference: {reference}")
        flash('Payment verification failed', 'error')
        return redirect(url_for('donate_error'))

# SUCCESS PAGE
# SUCCESS PAGE - FIXED VERSION
@app.route('/donate/success/<transaction_id>')
def donate_success(transaction_id):
    """Payment success page with real transaction data"""
    
    # Verify the payment again to get actual transaction details
    verification_result = verify_paystack_payment(transaction_id)
    
    if verification_result['success']:
        # Use real transaction data from Paystack
        transaction_info = {
            'transaction_id': transaction_id,
            'amount': verification_result['amount'],  # Real amount from Paystack
            'currency': verification_result['currency'],
            'completed_at': datetime.now(),  # You could also use verification_result['transaction_date']
            'status': 'success'
        }
        
        # Get the correct campaign using the campaign_id from metadata
        campaign_id = verification_result.get('campaign_id')
        if campaign_id and int(campaign_id) in CAMPAIGNS:
            campaign_data = CAMPAIGNS[int(campaign_id)]
        else:
            # Fallback to first campaign if no campaign_id found
            campaign_data = list(CAMPAIGNS.values())[0]
        
        return render_template('donate_success.html', 
                             transaction=transaction_info,
                             campaign=campaign_data)
    else:
        # If verification fails, redirect to error page
        app.logger.error(f"Transaction verification failed for success page: {transaction_id}")
        flash('Unable to verify transaction details', 'error')
        return redirect(url_for('donate_error'))
    
# PAYMENT ERROR PAGE
@app.route('/donate/error')
def donate_error():
    """Payment error page"""
    return render_template('donate_error.html')

# TEST PAYSTACK CONNECTION (using your existing function)
@app.route('/test-paystack')
def test_paystack():
    """Test Paystack connection"""
    result = test_paystack_connection()
    
    if result['success']:
        flash(f"Paystack connected successfully! {result['message']}", 'success')
    else:
        flash(f"Paystack connection failed: {result['message']}", 'error')
    
    return redirect(url_for('index'))

# ERROR HANDLERS
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}")
    return render_template('404.html'), 500

# TEMPLATE FILTERS (using your existing format_amount function)
@app.template_filter('currency')
def currency_filter(amount, currency='NGN'):
    """Format currency for templates"""
    return format_amount(amount, currency)

@app.template_filter('percentage')
def percentage_filter(value, decimals=1):
    """Format percentage for templates"""
    if value is None or value == '':
        return "0.0%"
    try:
        return f"{float(value):.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.0%"

# TEMPLATE GLOBALS
@app.template_global()
def get_foundation_stats():
    """Make foundation stats available to all templates"""
    return FOUNDATION_STATS

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print("🌟 Blak Shepherd Foundation Server Starting...")
    print(f"📊 {FOUNDATION_STATS['total_campaigns']} campaigns loaded")
    print(f"💰 ₦{FOUNDATION_STATS['total_raised']:,} total raised")
    print(f"👥 {FOUNDATION_STATS['lives_impacted']} lives impacted")
    print(f"🤝 {len(PARTNERS)} partner organizations")
    print("💳 Paystack integration ready (Direct HTTP)")
    print("🚀 Server ready!")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)