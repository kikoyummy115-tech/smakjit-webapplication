import pytest
from datetime import datetime, timedelta
from app.models import User, Event, VolunteerRequest, VendorSpot, BookVendor, RequestStatus

def test_create_event():
    current_time = datetime.utcnow()
    end_time = current_time + timedelta(hours=3)
    
    event = Event(
        title='Tech Conference 2026',
        description='A grand tech meetup.',
        from_time=current_time,
        to_time=end_time,
        author_id='mock-organizer-uuid-123'
    )
    
    assert event.title == 'Tech Conference 2026'
    assert event.description == 'A grand tech meetup.'
    assert event.from_time == current_time
    assert event.to_time == end_time
    assert event.author_id == 'mock-organizer-uuid-123'
    assert event.views == 0  


def test_create_volunteer_request_default_status():
    request = VolunteerRequest(
        event_id='mock-event-uuid-456',
        user_id='mock-volunteer-uuid-789'
    )
    
    assert request.event_id == 'mock-event-uuid-456'
    assert request.user_id == 'mock-volunteer-uuid-789'
    assert request.status == RequestStatus.PENDING 


def test_update_volunteer_request_status():
    request = VolunteerRequest(
        event_id='mock-event-uuid-456',
        user_id='mock-volunteer-uuid-789',
        status=RequestStatus.PENDING
    )
    
    request.status = RequestStatus.APPROVED
    assert request.status == RequestStatus.APPROVED
    
    request.status = RequestStatus.REJECTED
    assert request.status == RequestStatus.REJECTED
    
    
def test_create_vendor_spot():
    spot = VendorSpot(
        event_id='mock-event-uuid-456',
        spot_name='Booth A1',
        price=150
    )
    
    assert spot.event_id == 'mock-event-uuid-456'
    assert spot.spot_name == 'Booth A1'
    assert spot.price == 150


def test_book_vendor_spot():
    spot = VendorSpot(id='spot-123', event_id='event-456', spot_name='Booth A1', price=150)
    
    booking = BookVendor(
        vendor_spot_id=spot.id,
        user_id='mock-vendor-uuid-999'
    )
    
    spot.booking = booking
    
    assert spot.booking is not None
    assert spot.booking.vendor_spot_id == 'spot-123'
    assert spot.booking.user_id == 'mock-vendor-uuid-999'
