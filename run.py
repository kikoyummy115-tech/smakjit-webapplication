from flask import render_template
from flask_login import current_user
from datetime import datetime, timezone
from app import create_app
from app.models import User, Role, Permission
from extension import db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Role=Role,
        Permission=Permission,
    )


@app.before_request
def before_request():
     if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

with app.app_context():
    db.create_all()

@app.errorhandler(403)
def forbidden_found(e):
    return render_template('error/forbidden.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500




if __name__ == "__main__":
    app.run(debug=True)