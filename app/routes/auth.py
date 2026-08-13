from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user
from extension import db
from app.models import User
from app.utils import otp_verification, password_reset
import random


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    "Login in user required username and password"

    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()

        user = User.query.filter_by(email=email).first()
        
        if user and user.verify_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    "Register a new user and otp verify"
    
    if request.method == 'POST':
        username = request.form.get('username').strip() 
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()

        if not username or not email or not password:
            flash('Please fill out all fields', 'danger')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash('Password be at least 8 character', 'warning')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User already Exist', 'danger')
            return redirect(url_for('auth.register'))
        
        otp = random.randint(100000, 999999)
        
        session['register_user'] = {
            'username': username,
            'email': email,
            'password': password
        }
        
        session['register_otp'] = otp
        
        # 3. Send OTP by function
        try:
            otp_verification(email=email, otp=otp)
            flash('A 6 digit verification code has been sent to your email.', 'info')
            return redirect(url_for('auth.verify_otp'))
        except Exception as e:
            session.pop('register_user', None)
            session.pop('register_otp', None)
            flash('Failed to send verification email. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
        
    return render_template('auth/register.html')


@auth.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    "Verify the 6 digit OTP and instantly log the user in"
    
    if "register_user" not in session or 'register_otp' not in session:
        flash('Please register first.', 'warning')
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        user_otp = request.form.get('otp', '').strip()
    
        if user_otp and int(user_otp) == session.get('register_otp'): 
            user_date = session.get('register_user')           
            
        
            new_user = User(username=user_date['username'], email=user_date['email']) 
            new_user.password = user_date['password']    

            try:
                db.session.add(new_user)
                db.session.commit()
                
                # Clear temporary session storage
                session.pop('register_user', None)
                session.pop('register_otp', None)
                
                flash('Registration successful and email verify!', 'success')            
                return redirect(url_for('main.dashboard'))        
            except Exception as e:
                flash(f"Failed to register new user {str(e)}", "error")
        else:
            flash('invalid verification code. Please try again.', 'danger')
        
    return render_template('auth/verify_otp.html')


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        
        flash('If the email exists, a 6-digit reset code has been sent.', 'info')

        if user:
            reset_otp = random.randint(100000, 999999)
            
            # Store target user ID and OTP in session
            session['reset_user_id'] = user.id
            session['reset_otp'] = reset_otp
            try:
                password_reset(email=email, otp=reset_otp)
            except:
                pass        
        return redirect(url_for('auth.verify_reset_otp'))
    return render_template('auth/forgot_password.html')



@auth.route('/verify-reset-otp', methods=['GET', 'POST'])
def verify_reset_otp():
    "Verify the 6-digit password reset code"
    if 'reset_user_id' not in session or 'reset_otp' not in session:
        flash('Please request a password reset code first.', 'warning')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        user_otp = request.form.get('otp', '').strip()

        if user_otp and int(user_otp) == session.get('reset_otp'):
            # Code matches; unlock password reset access marker
            session['reset_verified'] = True
            session.pop('reset_otp', None)  # Consume code so it cannot be reused
            return redirect(url_for('auth.reset_password'))
        else:
            flash('Invalid reset code. Please try again.', 'danger')

    return render_template('auth/verify_reset_otp.html')


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    "Set the new password after OTP is successfully verified"
    if not session.get('reset_verified') or 'reset_user_id' not in session:
        flash('Unauthorized access. Please verify your OTP code first.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if len(new_password) < 8:
            flash("Password must be at least 8 characters", 'warning')
            return redirect(url_for('auth.reset_password'))
            
        if not new_password or new_password != confirm_password:
            flash('Passwords do not match or are empty.', 'danger')
            return render_template('auth/reset_password.html')

        # Retrieve user and update password
        user = User.query.get(session['reset_user_id'])
        if user:
            user.password = new_password  # Triggers hashing function inside your model
            db.session.commit()
            flash('Your password has been reset successfully. Please login.', 'success')
        else:
            flash('User account not found.', 'danger')

        # Clear remaining reset variables from session
        session.pop('reset_user_id', None)
        session.pop('reset_verified', None)
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')


@auth.route('/logout')
def logout():    
    logout_user()
    flash("Successfully logout account", 'success')
    return redirect(url_for('auth.login'))