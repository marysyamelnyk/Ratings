import hashlib
from app import app, db, User

def sha256_email(email):
    return hashlib.sha256(email.encode()).hexdigest()

with app.app_context():
    users = User.query.all()
    for user in users:
        if user.email and not user.email_sha256:
            user.email_sha256 = sha256_email(user.email)

    db.session.commit()
    print("✅ Email SHA256 hashes updated.")
