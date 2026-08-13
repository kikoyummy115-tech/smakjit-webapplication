from extension import db

role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.String(36), db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('permission_id', db.String(36), db.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)