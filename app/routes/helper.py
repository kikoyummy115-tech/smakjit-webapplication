import cloudinary.uploader

from flask import redirect, render_template, url_for, request, flash
from flask_login import login_required, current_user
from datetime import datetime

from app.routes import main

@main.route('/help')
@login_required
def help():
    return render_template('views/help.html')