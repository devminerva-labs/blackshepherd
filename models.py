from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Campaign(db.Model):
    """Campaign/Cause model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    goal_amount = db.Column(db.Float, nullable=False)
    raised_amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='NGN')
    is_active = db.Column(db.Boolean, default=True)
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to transactions
    transactions = db.relationship('Transaction', backref='campaign', lazy=True)
    
    def __repr__(self):
        return f'<Campaign {self.title}>'
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.goal_amount <= 0:
            return 0
        return min((self.raised_amount / self.goal_amount) * 100, 100)
    
    @property
    def image_url(self):
        """Get full image URL"""
        if self.image_filename:
            return f'/static/images/campaigns/{self.image_filename}'
        return '/static/images/campaigns/default.jpg'

class Transaction(db.Model):
    """Transaction/Donation model - completely anonymous"""
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    
    # Payment tracking
    transaction_id = db.Column(db.String(100), unique=True)
    payment_method = db.Column(db.String(20))  # 'stripe' or 'flutterwave'
    status = db.Column(db.String(20), default='pending')  # pending, success, failed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Transaction {self.currency}{self.amount} to {self.campaign.title}>'