import uuid
from extension import db

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., 'write_post', 'delete_user'
    
    def _repr__(self):
        return f"<Permission {self.name}>"