import uuid
from extension import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from datetime import timezone, datetime


from .permission import Permission
from .role import Role

class User(UserMixin ,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(100), index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(256))
    
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id'))
    img_url = db.Column(db.String(256), default=None)
    
    gender = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True) 
    
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # Automatically assign the default 'user' role if none is specified
        if self.role_id is None:
            default_role = Role.query.filter_by(name='user').first()
            if default_role:
                self.role_id = default_role.id

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
     
    def has_permission(self, perm):
        if self.role is None:
            return False
        return self.role.has_permission(perm)
    
    def is_online(self):
        if self.last_seen is None:
            return False
        current_time = datetime.now(timezone.utc)
        time_difference = (current_time - self.last_seen.replace(tzinfo=timezone.utc)).total_seconds()
        return time_difference < 300  

    
    def __repr__(self):
        return f"<User {self.username}>"


class AnonymousUser(AnonymousUserMixin):
    def can(self):
        return False
    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))