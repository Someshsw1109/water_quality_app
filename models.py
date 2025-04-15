from datetime import datetime
from flask_login import UserMixin
from myapp import db
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyses = db.relationship('Analysis', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(255), nullable=False)
    copper_concentration = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(50), nullable=False)
    analysis_data = db.Column(db.Text, nullable=True)  # JSON string with detailed analysis data

    def __repr__(self):
        return f'<Analysis {self.id}>'
    
    def get_analysis_data(self):
        """Parse the JSON string and return as a dictionary"""
        if self.analysis_data:
            try:
                return json.loads(self.analysis_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def get_risk_color(self):
        """Return the appropriate color for the risk level"""
        risk_colors = {
            'safe': 'success',
            'normal': 'info',
            'elevated': 'warning',
            'risky': 'danger',
            'hazardous': 'danger'
        }
        return risk_colors.get(self.risk_level.lower(), 'secondary')
    
    def get_formatted_timestamp(self):
        """Return a formatted timestamp string"""
        return self.timestamp.strftime("%b %d, %Y at %H:%M")
