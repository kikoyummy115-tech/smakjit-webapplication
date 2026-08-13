from flask import redirect, render_template, url_for, request, flash
from flask_login import login_required
from app.models import User, Role, Permission
from extension import db
from app.routes import main
from app.decorator import permission_required

@main.route('/manage-role')
@login_required
@permission_required(['manage_role'])
def manage_role():
    search_query = request.args.get('search', '').strip()
    selected_role = request.args.get('role', '').strip()
    page = request.args.get('page', 1, type=int)
    PER_PAGE = 15
    
    query = db.session.query(User, Role.name).join(Role, User.role_id == Role.id)
    
    if search_query:
        query = query.filter(
            (User.username.ilike(f"%{search_query}%")) |
            (User.email.ilike(f"%{search_query}%"))
        )
    
    if selected_role:
        query = query.filter(
            Role.name==selected_role
        )   
        
    pagination = db.paginate(query, page=page, per_page=PER_PAGE, error_out=False)
    all_roles = db.session.query(Role.name).distinct().all()

    return render_template(
        'views/manage.html',
        pagination=pagination,
        selected_role=selected_role,
        search_query=search_query, 
        roles=all_roles
    )

@main.route('/manage-role/roles', methods=['GET', 'POST'])
@login_required
@permission_required(['manage_role'])
def role_permission():    
    roles= Role.query.all()
    
    if request.method == "POST":
        role = request.form.get('role', '').strip()
        
        if not role:
            return redirect(url_for('main.role_permission'))
            
        existing_role = Role.query.filter_by(name=role).first()
        
        if existing_role:
            flash("Role already Exist", 'error')
            return redirect(url_for('main.role_permission'))
        
        new_role = Role(
            name=role
        )
        
        db.session.add(new_role)
        db.session.commit()
        flash("Role createed successfully", 'success')
        return redirect(url_for('main.role_permission'))    
    return render_template(
        'forms/role.html',
        roles=roles,
    )


@main.route('/manage-role/delete/<role_id>')
@login_required
@permission_required(['manage_role'])
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)

    if not role:
        flash("Role does not exist", 'error')
        return redirect(url_for('main.role_permission'))
    
    if role.name == "admin":
        flash('Cannot delete admin role', 'error')
        return redirect(url_for('main.role_permission'))
    
    db.session.delete(role)
    db.session.commit()
    flash(f"Successfull delete {role.name}", "success")
    return redirect(url_for('main.role_permission'))

@main.route('/manage-role/edit/<role_id>', methods=["GET", "POST"])
@login_required
@permission_required(['manage_role'])
def edit_role(role_id):
    roles = Role.query.all()
    role = Role.query.get_or_404(role_id)

    if request.method == "POST":
        name = request.form.get('name').strip()
    
        if not name:
            flash("Role is required", 'error')
            return redirect(url_for('main.edit_role', role_id=role.id))
        
        existing_role = Role.query.filter(Role.name == name, Role.id != role.id).first()
        if existing_role:
            flash("Role already exists", 'warning')
            return redirect(url_for('main.edit_role', role_id=role.id))
            
        role.name = name
        db.session.commit()
        flash(f"Successfully updated {role.name}", "success")
        return redirect(url_for('main.role_permission'))
    
    return render_template('forms/edit_role.html', roles=roles, role=role)

@main.route('/manage-role/permission/<role_id>', methods=['GET', 'POST'])
@login_required
@permission_required(['manage_role'])
def manage_permission(role_id):
    
    role = Role.query.get_or_404(role_id)
    role_permissions = Permission.query.join(Permission.roles).where(Role.id == role_id)
    all_permissions = Permission.query.all()
    
    return render_template(
        'forms/permission.html',
        role=role,
        role_permissions=role_permissions,
        all_permissions=all_permissions
    )

@main.route('/manage-role/permission/<role_id>/assigned/<perm_id>', methods=["POST"])
@login_required
@permission_required(['manage_role'])
def assign_permission(role_id, perm_id):
    if request.method == "POST":        
        role = Role.query.get_or_404(role_id)
        perm = Permission.query.get_or_404(perm_id)
        if perm in role.permissions:
            flash(f"Permission already exist in {perm.name}", "warning")
            return redirect(url_for('main.manage_permission', role_id=role_id))
            
        role.add_permission(perm)
        db.session.commit()
        flash(f"Success fully assigned {perm.name}", 'success')
    return redirect(url_for('main.manage_permission', role_id=role_id))


@main.route('/manage-role/permission/<role_id>/unassigned/<perm_id>', methods=["POST"])
@login_required
@permission_required(['manage_role'])
def unassign_permission(role_id, perm_id):
    if request.method == "POST":        
        role = Role.query.get_or_404(role_id)
        perm = Permission.query.get_or_404(perm_id)
        role.remove_permission(perm)
        db.session.commit()
        flash(f"Success fully unassigned {perm.name}", 'success')
    return redirect(url_for('main.manage_permission', role_id=role_id))


@main.route('/manage-role/permission/assign-role/<user_id>', methods=['POST'])
def assign_role(user_id):
    user = User.query.get_or_404(user_id)
    selected_role_name = request.form.get('role')
    
    if not selected_role_name:
        flash('Please select a valid role.', 'error')
        return redirect(url_for('main.manage_role'))
        
    role = Role.query.filter_by(name=selected_role_name).first()
    
    if role:
        user.role_id = role.id 
        db.session.commit()
        flash(f'Successfully updated {user.username} to {role.name}.', 'success')
    else:
        flash('Selected role does not exist.', 'error')
    return redirect(url_for('main.manage_role'))