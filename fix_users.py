from app import create_app
from database.db import db
from database.models import User
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt()

with app.app_context():
    try:
        # 1. Delete the old broken users first
        # We use db.session.query to ensure we are using the active session
        db.session.query(User).filter(User.username.in_(['admin', 'Abhishek'])).delete(synchronize_session=False)
        
        # 2. Generate a REAL valid hash for 'password123'
        valid_hash = bcrypt.generate_password_hash('password123').decode('utf-8')
        
        # 3. Add the admin back with the correct hash
        admin_user = User(username='admin', password=valid_hash, role='admin')
        db.session.add(admin_user)
        
        # 4. Add Abhishek back as a regular user
        abhishek_user = User(username='Abhishek', password=valid_hash, role='user')
        db.session.add(abhishek_user)
        
        # 5. Save changes to MySQL (CORRECTED LINE)
        db.session.commit()
        
        print("Database Updated Successfully!")
        print("You can now login with username: admin and password: password123")
        
    except Exception as e:
        db.session.rollback() # Undo changes if there is an error
        print(f"An error occurred: {e}")