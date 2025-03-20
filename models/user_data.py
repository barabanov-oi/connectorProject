
from extensions import db
from datetime import datetime

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    settings = db.Column(db.JSON)
    
    user = db.relationship('User', backref=db.backref('user_data', lazy=True))
