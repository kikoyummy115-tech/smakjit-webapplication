from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required
from extension import db
from app.decorator import permission_required
from app.models import Category, Event, Location


event = Blueprint('event', __name__)


@event.route('/view')
@login_required
def view_event():
    
    return render_template('views/event.html')

@event.route('/manage')
@login_required
@permission_required(['manage_event'])
def manage_event():
    
    return render_template('views/event.html')


@event.route('/new', methods=["GET", 'POST'])
@login_required
@permission_required(['manage_event'])
def create_event():
    
    
    all_categories = Category.query.all()
    all_locations = Location.query.all()
    return render_template(
        'forms/add_event.html',
        categories=all_categories,
        locations=all_locations
    )