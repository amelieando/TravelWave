from database import db
from datetime import datetime

class TripItinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    travelers = db.Column(db.Integer, nullable=False, default=1)
    budget = db.Column(db.String(50), nullable=True)
    interests = db.Column(db.Text, nullable=True)
    accommodation_type = db.Column(db.String(100), nullable=True)
    transportation = db.Column(db.String(100), nullable=True)
    itinerary_content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TripItinerary {self.destination}>'