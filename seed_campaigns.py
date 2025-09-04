"""
Black Shepherd Foundation - Update Campaigns Script
This script will:
1. Delete all existing campaigns
2. Add only 3 specific campaigns
3. Distribute ₦4 million total raised amount
"""

from app import app, db
from models import Campaign
from datetime import datetime

def update_campaigns():
    """Update database to have only 3 campaigns with ₦4M total raised"""
    
    with app.app_context():
        # Step 1: Delete all existing campaigns
        print("🗑️  Removing all existing campaigns...")
        Campaign.query.delete()
        db.session.commit()
        print("✅ All campaigns removed\n")
        
        # Step 2: Add the 3 specific campaigns with distributed amounts
        print("📝 Adding 3 campaigns with ₦4 million total raised...\n")
        
        campaigns = [
            {
                'title': 'Clean Water Access Project',
                'description': '''Providing clean, safe drinking water to rural communities across Nigeria. 
                Every donation helps us install water pumps, purification systems, and educate communities 
                about water safety. Our goal is to reach 50 villages by the end of 2025, ensuring that 
                over 10,000 families have access to clean water. Each well costs approximately ₦200,000 
                and can serve up to 500 people for over 20 years. Your support brings life-saving water 
                to communities that need it most.''',
                'goal_amount': 5000000.0,  # ₦5 million goal
                'raised_amount': 1500000.0,  # ₦1.5 million raised
                'currency': 'NGN',
                'image_filename': 'water.jpg',
                'is_active': True
            },
            {
                'title': 'Girls Education Initiative',
                'description': '''Breaking barriers to education for girls in underserved communities. 
                We provide scholarships, school supplies, uniforms, and mentorship programs to keep 
                girls in school. Education is the most powerful tool to break the cycle of poverty. 
                Your donation covers tuition fees, textbooks, uniforms, and transportation for girls 
                who would otherwise be unable to attend school. Just ₦50,000 sponsors one girl for 
                a full academic year, giving her the chance to build a brighter future.''',
                'goal_amount': 3000000.0,  # ₦3 million goal
                'raised_amount': 1000000.0,  # ₦1 million raised (as you specified)
                'currency': 'NGN',
                'image_filename': 'education.jpg',
                'is_active': True
            },
            {
                'title': 'Rural Healthcare Outreach',
                'description': '''Bringing essential healthcare services to remote villages without access 
                to medical facilities. Our mobile clinics provide vaccinations, maternal health services, 
                and basic medical care. We conduct monthly medical outreaches, providing free consultations, 
                medications, and health education. Each outreach costs ₦500,000 and reaches approximately 
                1,000 people. Help us expand healthcare access to the most vulnerable communities 
                across Nigeria.''',
                'goal_amount': 4000000.0,  # ₦4 million goal
                'raised_amount': 1500000.0,  # ₦1.5 million raised
                'currency': 'NGN',
                'image_filename': 'healthcare.jpg',
                'is_active': True
            }
        ]
        
        # Add each campaign
        for campaign_data in campaigns:
            campaign = Campaign(
                title=campaign_data['title'],
                description=campaign_data['description'],
                goal_amount=campaign_data['goal_amount'],
                raised_amount=campaign_data['raised_amount'],
                currency=campaign_data['currency'],
                image_filename=campaign_data['image_filename'],
                is_active=campaign_data['is_active']
            )
            
            db.session.add(campaign)
            
            # Calculate and display progress
            progress = (campaign_data['raised_amount'] / campaign_data['goal_amount']) * 100
            print(f"✅ Added: {campaign_data['title']}")
            print(f"   Goal: ₦{campaign_data['goal_amount']:,.0f}")
            print(f"   Raised: ₦{campaign_data['raised_amount']:,.0f}")
            print(f"   Progress: {progress:.1f}%")
            print()
        
        # Commit all changes
        db.session.commit()
        
        # Step 3: Display summary
        print("=" * 60)
        print("🎉 CAMPAIGN UPDATE COMPLETE!")
        print("=" * 60)
        
        # Fetch and display final statistics
        all_campaigns = Campaign.query.all()
        total_goal = sum(c.goal_amount for c in all_campaigns)
        total_raised = sum(c.raised_amount for c in all_campaigns)
        total_campaigns = len(all_campaigns)
        
        print(f"\n📊 Final Database Summary:")
        print(f"   Total Campaigns: {total_campaigns}")
        print(f"   Total Goal Amount: ₦{total_goal:,.0f}")
        print(f"   Total Raised: ₦{total_raised:,.0f}")
        print(f"   Overall Progress: {(total_raised/total_goal*100):.1f}%")
        
        print("\n💰 Breakdown of ₦4,000,000 raised:")
        for campaign in all_campaigns:
            percentage_of_total = (campaign.raised_amount / total_raised) * 100
            print(f"   • {campaign.title}: ₦{campaign.raised_amount:,.0f} ({percentage_of_total:.0f}%)")
        
        print("\n✨ Your website now shows:")
        print("   - 3 Active Campaigns")
        print("   - ₦4,000,000 Total Raised")
        print("   - 0 Total Donations (no transactions yet)")
        print("\n🌐 Visit http://localhost:5000/campaigns to see the updated campaigns")

if __name__ == '__main__':
    # Run the update
    update_campaigns()