from app.models import User, Permission, Role
# Test create new user


def test_create_user():
    user = User(username='testuser', email='testuser@example.com')
    user.password = 'password'
    
    assert user.username == 'testuser'
    assert user.email == 'testuser@example.com'
    assert user.verify_password('password') is True
    assert user.password_hash is not None
    assert user.role is None  # Assuming no role is assigned by default
    assert user.password_hash != 'password'  #Ensure password is hashed

def test_create_role():
    role = Role(name='admin')
    
    assert role.name == 'admin'
    assert role.users.count() == 0  # Assuming no users are assigned by default
    assert role.permissions == []  # Assuming no permissions are assigned by default
    

def test_create_permission():
    permission = Permission(name='view_dashboard')
    assert permission.name == 'view_dashboard'
    

def test_add_permission_to_role():
    role = Role(name='admin')
    permission = Permission(name='view_dashboard')

    role.add_permission(permission)
    assert role.permissions == [permission]


def test_add_multiple_permissions_to_role():
    role = Role(name='admin')
    permission1 = Permission(name='view_dashboard')
    permission2 = Permission(name='edit_user')
    
    role.add_permission(permission1)
    role.add_permission(permission2)
    assert role.permissions == [permission1, permission2]

def test_remove_permission_from_role():
    role = Role(name='admin')
    permission = Permission(name='view_dashboard')
    
    role.add_permission(permission)
    assert role.permissions == [permission]
    
    role.remove_permission(permission)
    assert role.permissions == []


def test_reset_permissions():
    role = Role(name='admin')
    permission1 = Permission(name='view_dashboard')
    permission2 = Permission(name='edit_user')
    
    role.add_permission(permission1)
    role.add_permission(permission2)
    
    assert role.permissions == [permission1, permission2]
    role.reset_permissions()
    assert role.permissions == []
    

def test_has_permission():
    role = Role(name='admin')
    permission = Permission(name='view_dashboard')
    
    role.add_permission(permission)
    assert role.has_permission(permission) is True
    
    # Test with a permission not assigned to the role
    permission2 = Permission(name='edit_user')
    assert role.has_permission(permission2) is False