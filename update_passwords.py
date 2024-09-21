from sqlalchemy.orm import Session
from sqlalchemy import update
from database import engine
from utils import hash_password
from main import users

def update_existing_passwords():
    db = Session(bind=engine)
    # Fetch all users
    result = db.execute(users.select()).fetchall()
    for user in result:
        # Check if the password is already hashed (bcrypt hashes start with "$2b$")
        if not user.password.startswith("$2b$"):
            print(f"Updating password for user: {user.email}")  # Debugging statement
            hashed_password = hash_password(user.password)
            update_stmt = (
                update(users)
                .where(users.c.email == user.email)
                .values(password=hashed_password)
            )
            db.execute(update_stmt)
            db.commit()
    db.close()

if __name__ == "__main__":
    update_existing_passwords()
