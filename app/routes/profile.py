import cloudinary.uploader
from flask import redirect, render_template, url_for, request, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.models import User
from extension import db
from app.routes import main


@main.route('/profile', methods=['GET'])
@login_required
def profile():
    "View the profile page for the current user."
    return render_template('views/profile.html')



@main.route('/profile/upload-image', methods=['POST'])
@login_required
def upload_image():
    file_to_upload = request.files.get('file')
    
    if not file_to_upload or file_to_upload.filename == '':
        flash("No file Selected or invalid input", 'error')
        return redirect(url_for('main.profile'))

    try:
        upload_result = cloudinary.uploader.upload(
            file_to_upload,
            resource_type="auto"
        )
        
        secure_url = upload_result.get("secure_url")
        current_user.img_url = secure_url
        db.session.commit()
        flash("Profile image updated successfull", "success")
    except Exception as e:
        print(str(e))
        flash("Could not upload image, Please try again!", "error")
        
    return redirect(url_for('main.profile'))


@main.route('/profile/remove-image', methods=['POST'])
@login_required
def remove_image():
    
    if not current_user.img_url:
        flash('No profile image to remove.', 'warning')
        return redirect(url_for('main.profile'))
        
    try:
        
        url_parts = current_user.img_url.split('/')
        upload_index = url_parts.index('upload')
        
        public_id_with_ext = '/'.join(url_parts[upload_index + 2:])
        public_id = public_id_with_ext.rsplit('.', 1)[0]

        deletion_result = cloudinary.uploader.destroy(public_id)
        
        if deletion_result.get('result') == 'ok' or deletion_result.get('result') == 'not_found':
            current_user.img_url = None
            db.session.commit()
            flash('Profile image removed successfully!', 'success')
        else:
            flash('Cloudinary could not remove the image file.', 'danger')
            
    except Exception as e:
        flash(f'Error removing image: {str(e)}', 'danger')

    return redirect(url_for('main.profile'))


@main.route('/profile/edit', methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        username = request.form.get('username').strip()
        email_input = request.form.get('email').strip()
        gender = request.form.get('gender')
        date_str = request.form.get('date_of_birth')        
        
        if not username or not email_input:
            flash("Username and email are required", 'error')
            return redirect(url_for('main.edit_profile'))

        existing_user = User.query.filter_by(email=email_input).first()
        if existing_user and existing_user.id != current_user.id:
            flash("Email already exists", "error")
            return redirect(url_for('main.edit_profile'))
        
        # Core updates
        current_user.username = username
        current_user.email = email_input
        
        current_user.gender = gender if gender else None

        if date_str:
            try:
                current_user.date_of_birth = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Invalid date format", "error")
                return redirect(url_for('main.edit_profile'))
        else:
            current_user.date_of_birth = None
            
        try:
            db.session.commit()
            flash("Updated user successfully", "success")
            return redirect(url_for('main.profile'))
        except Exception as e:
            db.session.rollback()
            flash("Could not save your changes. Try again", "error")

    return render_template('forms/edit_profile.html')


@main.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    
    if request.method == 'POST':        
        old_password = request.form.get('old_password').strip()
        new_password = request.form.get('new_password').strip()
        
        
        if current_user.verify_password(old_password) != True:
            flash("Incorrect old password", "error")
            return redirect(url_for('main.change_password'))
        
        
        if old_password == new_password:
            flash("Required different password")
            return redirect(url_for('main.change_password'))
        
        try:
            current_user.password = new_password
            db.session.commit()   
            flash("Successfully save changes password", 'success')
            return redirect(url_for('main.profile'))
        except Exception as e:
            db.session.rollback()
            flash("Could not save your changes. Please try again", "error")
        
    return render_template('forms/change_password.html')
