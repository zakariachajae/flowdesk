from fastapi import FastAPI, Form, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import FastAPI, Form, HTTPException, Depends, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import MetaData, Table, update
from sqlalchemy import MetaData, Table, update, select, asc, desc
from sqlalchemy.orm import Session
from datetime import timedelta
from sqlalchemy.exc import NoSuchTableError
from datetime import timedelta, datetime
from fastapi.staticfiles import StaticFiles
import time
import random
@@ -29,47 +30,37 @@ app.add_middleware(
    allow_headers=["*"],
)
# Load metadata and users table
# Load metadata and user table
metadata = MetaData()
users = Table('user', metadata, autoload_with=engine)
try:
    user_table = Table('user', metadata, autoload_with=engine)
except NoSuchTableError:
    print("Error: The table 'user' does not exist in the database.")
    raise
@app.post("/login")
async def login(response: Response, db=Depends(get_db), email: str = Form(...), password: str = Form(...)):
    print(f"Attempting to log in user: {email}") 
    query = users.select().where(users.c.email == email)
    query = user_table.select().where(user_table.c.email == email)
    result = db.execute(query).first()
    if result:
        print(f"User found: {result.email}")  
        print(f"Stored hashed password: {result.password}")  
        if verify_password(password, result.password):
            print(f"Password verified for user: {email}") 
            # Update last_login_at
            current_time = int(time.time())
            update_stmt = (
                update(users)
                .where(users.c.email == email)
                .values(last_login_at=current_time)
            )
            db.execute(update_stmt)
            db.commit()
            # Generate JWT token
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(data={"sub": email}, expires_delta=access_token_expires)
            response = RedirectResponse(url="/dashboard", status_code=303)
            response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
            return response
        else:
            print("Password verification failed")  
            print(f"Plain password: {password}")  
            print(f"Plain password (bytes): {password.encode('utf-8')}")  
            print(f"Hashed password (bytes): {result.password.encode('utf-8')}")  
            raise HTTPException(status_code=400, detail="Invalid credentials")
    if result and verify_password(password, result.password):
        current_time = int(time.time())
        update_stmt = (
            update(user_table)
            .where(user_table.c.email == email)
            .values(last_login_at=current_time)
        )
        db.execute(update_stmt)
        db.commit()
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(data={"sub": email}, expires_delta=access_token_expires)
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return response
    else:
        print("User not found")  
        raise HTTPException(status_code=400, detail="Invalid credentials")
@app.get("/", response_class=HTMLResponse)
async def get_login_form():
    with open('templates/login.html', 'r') as file:
@@ -90,26 +81,20 @@ async def forgot_password_form():
@app.post("/forgot_password")
async def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    query = users.select().where(users.c.email == email)
    query = user_table.select().where(user_table.c.email == email)
    result = db.execute(query).first()
    if result:
        # Generate a temporary password
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        print(temp_password)
        hashed_temp_password = hash_password(temp_password)
        # Update the user's password in the database
        update_stmt = (
            update(users)
            .where(users.c.email == email)
            update(user_table)
            .where(user_table.c.email == email)
            .values(password=hashed_temp_password, should_reset_password=1)
        )
        db.execute(update_stmt)
        db.commit()
        # Send the temporary password via email
        send_email(email, temp_password)
        return {"message": "A temporary password has been sent to your email address."}
        return JSONResponse(content={"message": "A temporary password has been sent to your email address."})
    else:
        raise HTTPException(status_code=400, detail="Email address not found")
@@ -118,12 +103,10 @@ def send_email(to_email, temp_password):
    email_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    msg = MIMEText(f"Your temporary password is: {temp_password}")
    msg['Subject'] = 'Password Reset'
    msg['From'] = from_email
    msg['To'] = to_email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, email_password)
@@ -134,22 +117,99 @@ async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response
"""
def create_user(db: Session, email: str, password: str):
@app.get("/users")
async def list_users(db: Session = Depends(get_db)):
    try:
        query = select(
            user_table.c.id,
            user_table.c.firstname,
            user_table.c.lastname,
            user_table.c.email,
            user_table.c.is_active,
            user_table.c.created_at,
            user_table.c.last_login_at
        ).where(user_table.c.is_deleted == 0)
        result = db.execute(query).fetchall()
        users_list = [
            {
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "is_active": user.is_active,
                "created_at": datetime.utcfromtimestamp(user.created_at).strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
                "last_login_at": datetime.utcfromtimestamp(user.last_login_at).strftime('%Y-%m-%d %H:%M:%S') if user.last_login_at else None
            }
            for user in result
        ]
        return JSONResponse(content=users_list)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
@app.post("/create_user")
async def create_user_endpoint(firstname: str = Form(...), lastname: str = Form(...), email: str = Form(...), is_active: bool = Form(False), db: Session = Depends(get_db)):
    query = user_table.select().where(user_table.c.email == email)
    result = db.execute(query).first()
    if result:
        return JSONResponse(content={"message": "Email already exists"}, status_code=400)
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    create_user(db, email, password, firstname, lastname, is_active)
    if is_active:
        send_email(email, password)
    return JSONResponse(content={"message": "User created successfully"})
def create_user(db: Session, email: str, password: str, firstname: str, lastname: str, is_active: bool):
    hashed_password = hash_password(password)
    new_user = users.insert().values(email=email, password=hashed_password)
    new_user = user_table.insert().values(email=email, password=hashed_password, firstname=firstname, lastname=lastname, is_active=is_active, created_at=int(time.time()))
    db.execute(new_user)
    db.commit()
@app.post("/update_user")
async def update_user_endpoint(id: int = Form(...), firstname: str = Form(...), lastname: str = Form(...), email: str = Form(...), is_active: bool = Form(False), db: Session = Depends(get_db)):
    print(f"Update request received for user ID: {id}")
    query = user_table.select().where(user_table.c.email == email).where(user_table.c.id != id)
    result = db.execute(query).first()
    if result:
        raise HTTPException(status_code=400, detail="Email address already exists")
    update_stmt = (
        update(user_table)
        .where(user_table.c.id == id)
        .values(firstname=firstname, lastname=lastname, email=email, is_active=is_active, updated_at=int(time.time()))
    )
    db.execute(update_stmt)
    db.commit()
    return JSONResponse(content={"message": "User updated successfully"})
@app.post("/delete_user")
async def delete_user_endpoint(id: int = Form(...), db: Session = Depends(get_db)):
    print(f"Delete request received for user ID: {id}")
    update_stmt = (
        update(user_table)
        .where(user_table.c.id == id)
        .values(is_deleted=1, updated_at=int(time.time()))
    )
    db.execute(update_stmt)
    db.commit()
    return JSONResponse(content={"message": "User deleted successfully"})
# Example usage to create a user
@app.post("/create_user")
async def create_user_endpoint(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    try:
        print(f"Creating user: {email}")  
        create_user(db, email, password)
        return {"message": "User created successfully"}
    except Exception as e:
        print(f"Error creating user: {e}")  
        raise HTTPException(status_code=500, detail="Internal Server Error")
"""
@app.post("/reset_password")
async def reset_password_endpoint(id: int = Form(...), db: Session = Depends(get_db)):
    print(f"Reset password request received for user ID: {id}")
    query = user_table.select().where(user_table.c.id == id)
    result = db.execute(query).first()
    if not result:
        raise HTTPException(status_code=400, detail="User not found")
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    hashed_temp_password = hash_password(temp_password)
    update_stmt = (
        update(user_table)
        .where(user_table.c.id == id)
        .values(password=hashed_temp_password, should_reset_password=1, updated_at=int(time.time()))
    )
    db.execute(update_stmt)
    db.commit()
    send_email(result.email, temp_password)
    return JSONResponse(content={"message": "Password reset successfully"})