from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required, current_user

from app.decorator import permission_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('main.dashboard'))
    
@main.route('/dashboard')
@login_required
def dashboard():

    return render_template('views/dashboard.html')

@main.route('/admin')
@login_required
def admin():
    "Display the admin panel"
    return "Admin Page"