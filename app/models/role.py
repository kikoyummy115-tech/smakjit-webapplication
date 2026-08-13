import uuid
from extension import db
from .association import role_permissions

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(64), unique=True, index=True, default='user')
    
    users = db.relationship('User', backref='role', lazy='dynamic')
    permissions = db.relationship('Permission', secondary=role_permissions, backref='roles', lazy='select')
    
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions.append(perm)
    
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions.remove(perm)
        
    def reset_permissions(self):
        self.permissions = []
        
    def has_permission(self, perm):
        if isinstance(perm, str):
            return any(p.name == perm for p in self.permissions)
        return perm in self.permissions
    
    def __repr__(self):
        return f"<Role {self.name}>"
    