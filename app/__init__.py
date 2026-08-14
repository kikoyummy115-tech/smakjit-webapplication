import cloudinary
from flask import Flask
from config import config
from extension import db, login_manager, migrate, mail
from app.models import User, Role, Permission

login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(config['default'])

    cloudinary.config(
        cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET'],
        secure=True
    )

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    with app.app_context():
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
            
        if not Role.query.filter_by(name='user').first():
            db.session.add(Role(name='user'))
            
        db.session.commit() 
  
        required_permissions = [
            'manage_role',
            'manage_event',
            'manage_post',      
            'manage_report',    
            'manage_service',
            'view_function',
            'view_analytic',
            'view_dashboard',
            'view_users'
        ]
    
        existing_perms = {p.name for p in Permission.query.filter(Permission.name.in_(required_permissions)).all()}        
        missing_perms = [name for name in required_permissions if name not in existing_perms]
    
        if missing_perms:
            new_permissions_objects = [Permission(name=name) for name in missing_perms]
            db.session.add_all(new_permissions_objects)
            db.session.commit()
            print(f"Successfully added missing permissions: {missing_perms}")
            
        manage_role_perm = Permission.query.filter_by(name='manage_role').first()
        if manage_role_perm and admin_role and (manage_role_perm not in admin_role.permissions):
            admin_role.permissions.append(manage_role_perm)
            db.session.commit()
            print("Successfully assigned 'manage_role' permission to the 'admin' role.")

    from app.routes import auth, main, event
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(main)
    app.register_blueprint(event, url_prefix='/event')    
    
    return app

