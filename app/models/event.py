from extension import db
from datetime import datetime
import enum
import uuid

class RequestStatus(enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

# Junction table for many-to-many relationship between Event and Category
event_categories = db.Table('event_categories',
    db.Column('category_id', db.String(36), db.ForeignKey('categories.id'), primary_key=True),
    db.Column('event_id', db.String(36), db.ForeignKey('events.id'), primary_key=True)
)

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    events = db.relationship('Event', backref='location', lazy=True)
        
    def __repr__(self):
        return f"<Role {self.name}>"


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    icons = db.Column(db.String(255))

    def __repr__(self):
        return f"<Role {self.name}>"


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())) 
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    img_url = db.Column(db.String(255))
    
    # Date fields (Saved without timezone by default in SQLAlchemy)
    date = db.Column(db.DateTime, nullable=True)
    from_time = db.Column(db.DateTime, nullable=False)
    to_time = db.Column(db.DateTime, nullable=False)
    
    # Timestamps (Automatically populated when created or modified)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    views = db.Column(db.Integer, default=0)
    
    # Foreign Keys
    location_id = db.Column(db.String(36), db.ForeignKey('locations.id'), nullable=True)
    author_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Many-to-Many relationship
    categories = db.relationship('Category', secondary=event_categories, backref=db.backref('events', lazy='dynamic'))
    # One-to-Many relationships
    volunteer_requests = db.relationship('VolunteerRequest', backref='event', lazy=True)
    vendor_spots = db.relationship('VendorSpot', backref='event', lazy=True)
    ratings = db.relationship('Rate', backref='event', lazy=True)
    
    def __repr__(self):
        return f"<Event {self.title}>"



class VolunteerRequest(db.Model):
    __tablename__ = 'volunteer_requests'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    event_id = db.Column(db.String(36), db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    status = db.Column(db.Enum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<VolunteerRequest {self.user_id}>"

    
class VendorSpot(db.Model):
    __tablename__ = 'vendor_spots'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = db.Column(db.String(36), db.ForeignKey('events.id'), nullable=False)
    spot_name = db.Column(db.String(255), nullable=False) # e.g., "Booth A1"
    price = db.Column(db.Integer, nullable=False)
    
    # Links availability directly to the booking manifest
    booking = db.relationship('BookVendor', backref='spot', uselist=False, lazy=True)
    
    def __repr__(self):
        return f"<Vendor {self.spot_name}>"


class BookVendor(db.Model):
    __tablename__ = 'book_vendors'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_spot_id = db.Column(db.String(36), db.ForeignKey('vendor_spots.id'), unique=True, nullable=False)
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<BookVendor {self.vendor_spot_id}>"


class Rate(db.Model):
    __tablename__ = 'rates'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scores = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.String(36), db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    def average_score(self):
        """Calculates average from the loaded relationship."""
        if not self.rates:
            return 0.0
        return round(sum(rate.scores for rate in self.rates) / len(self.rates), 2)
    
    def __repr__(self):
        return f"<Rate {self.scores}>"