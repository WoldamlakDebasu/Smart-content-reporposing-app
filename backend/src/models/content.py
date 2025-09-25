from src.models.user import db
from datetime import datetime
import json

class Content(db.Model):
    __tablename__ = 'content'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    original_content = db.Column(db.Text, nullable=False)
    content_format = db.Column(db.String(50), default='text')
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, error
    progress = db.Column(db.Float, default=0.0)
    
    # Analysis results stored as JSON
    analysis_results = db.Column(db.Text)  # JSON string
    
    # Repurposed content stored as JSON
    repurposed_outputs = db.Column(db.Text)  # JSON string
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, title, original_content, content_format='text'):
        self.title = title
        self.original_content = original_content
        self.content_format = content_format
        self.status = 'pending'
        self.progress = 0.0
    
    def set_analysis_results(self, results):
        """Store analysis results as JSON"""
        self.analysis_results = json.dumps(results)
    
    def get_analysis_results(self):
        """Retrieve analysis results from JSON"""
        if self.analysis_results:
            return json.loads(self.analysis_results)
        return {}
    
    def set_repurposed_outputs(self, outputs):
        """Store repurposed outputs as JSON"""
        self.repurposed_outputs = json.dumps(outputs)
    
    def get_repurposed_outputs(self):
        """Retrieve repurposed outputs from JSON"""
        if self.repurposed_outputs:
            return json.loads(self.repurposed_outputs)
        return {}
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'original_content': self.original_content,
            'content_format': self.content_format,
            'status': self.status,
            'progress': self.progress,
            'analysis_results': self.get_analysis_results(),
            'repurposed_outputs': self.get_repurposed_outputs(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DistributionLog(db.Model):
    __tablename__ = 'distribution_log'
    
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, posted, failed
    post_id = db.Column(db.String(255))  # Platform-specific post ID
    post_url = db.Column(db.String(500))  # URL to the posted content
    scheduled_time = db.Column(db.DateTime)
    posted_time = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, content_id, platform, user_id=None, scheduled_time=None):
        self.content_id = content_id
        self.platform = platform
        self.user_id = user_id
        self.scheduled_time = scheduled_time or datetime.utcnow()
        self.status = 'scheduled'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'content_id': self.content_id,
            'user_id': self.user_id,
            'platform': self.platform,
            'status': self.status,
            'post_id': self.post_id,
            'post_url': self.post_url,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'posted_time': self.posted_time.isoformat() if self.posted_time else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

