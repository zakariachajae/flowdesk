from fastapi import FastAPI, Form, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse,FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import MetaData, Table, update, select, func, delete, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError  # Add this import
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import time
import smtplib
from email.mime.text import MIMEText
from datetime import timedelta, datetime
from typing import Optional
from pydantic import BaseModel
import os
import random
import string  # Added to avoid missing import
from starlette.staticfiles import StaticFiles  # Importing StaticFiles
from typing import List
import pickle
from database import engine, get_db
from utils import create_access_token, verify_password, hash_password
# Load users for assignment
from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime



app = FastAPI()



metadata = MetaData()

# Middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for JS and CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load user and ticket tables
user_table = Table('user', metadata, autoload_with=engine)
ticket_table = Table('ticket', metadata, autoload_with=engine)
meeting_table = Table('meetings', metadata, autoload_with=engine)
participation_table = Table('participation', metadata, autoload_with=engine)


SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = './credentials.json'
TOKEN_FILE = './token.pickle'


class MeetingCreateRequest(BaseModel):
    subject: str
    start_date: str
    participantIds : List[str]

def get_credentials():
    """Get credentials from token.pickle or perform OAuth 2.0 flow."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_local_server(port=8000)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds



def create_event_data(subject, start_date):
    start_datetime = datetime.fromisoformat(start_date)
    end_datetime = start_datetime + timedelta(hours=1)  # Set duration to 1 hour

    return {
        'summary': subject,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
        'conferenceData': {
            'createRequest': {
                'requestId': 'unique-string',  # Ensure this is a unique string for each request
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                }
            }
        }
    }

@app.post("/create_meeting")
async def create_meeting(request: MeetingCreateRequest, db: Session = Depends(get_db)):
    """Create a Google Meet event and update meeting/participation tables."""
    try:
        # Get Google Calendar API credentials and create a service
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)

        # Create Google Calendar event data
        event = create_event_data(request.subject, request.start_date)

        # Insert the event into Google Calendar
        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        # Get the Google Meet link
        meet_link = created_event.get('hangoutLink')

        if not meet_link:
            raise HTTPException(status_code=400, detail="Google Meet link not generated.")

        # Update `meeting` table with the event link and other details
        meeting_insert = meeting_table.insert().values(
            subject=request.subject,
            date=request.start_date,
            link=meet_link,  # Assuming you have this column in your meeting_table
            created_at=func.now(),
            updated_at=func.now()
        )
        result = db.execute(meeting_insert)
        meeting_id = result.inserted_primary_key[0]  # Get the newly inserted meeting's ID

        # Now, link the participants to the meeting in the `participation` table
        for participant_email in request.participantIds:
            # Assuming you have a `user_table` and participation_table with user_id and meeting_id
            user_query = db.query(user_table).filter(user_table.c.email == participant_email).first()
            if user_query:
                participation_insert = participation_table.insert().values(
                    user_id=user_query.id,
                    meeting_id=meeting_id,
                    created_at=func.now(),
                    updated_at=func.now()
                )
                db.execute(participation_insert)
                send_email(participant_email, f"You have been invited to join this meeting: {request.subject}" f"\nlink to meeting: {meet_link}")
        # Commit the changes to the database
        db.commit()

        # Return the event details, including the Google Meet link
        return JSONResponse(content={"eventLink": meet_link}, status_code=200)

    except HttpError as error:
        print(f'Error occurred: {error}')
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/meetings")
async def list_meetings(db: Session = Depends(get_db)):
    query = select(
        meeting_table.c.id,
        meeting_table.c.subject,
        meeting_table.c.link,
        meeting_table.c.date,
        meeting_table.c.created_at,   # Include created_at
        meeting_table.c.updated_at    # Include updated_at
    )

    result = db.execute(query).fetchall()

    meeting_list = [
        {
            "id": meeting.id,
            "subject": meeting.subject,
            "link": meeting.link,
            "date": meeting.date.isoformat(),
            "created_at": meeting.created_at.isoformat() if isinstance(meeting.created_at, datetime) else meeting.created_at,
            "updated_at": meeting.updated_at.isoformat() if isinstance(meeting.updated_at, datetime) else meeting.updated_at
        
        }
        for meeting in result
    ]
    return JSONResponse(content=meeting_list)

@app.get("/user_meetings")
async def list_user_meetings(user_id: int, db: Session = Depends(get_db)):
    print(user_id)
    # Query to fetch meetings where the user is participating
    query = (
        select(
            meeting_table.c.id,
            meeting_table.c.subject,
            meeting_table.c.link,
            meeting_table.c.date,
            meeting_table.c.created_at,
            meeting_table.c.updated_at
        )
        .join(participation_table, participation_table.c.meeting_id == meeting_table.c.id)
        .where(participation_table.c.user_id == user_id)
    )

    result = db.execute(query).fetchall()

    meeting_list = [
        {
            "id": meeting.id,
            "subject": meeting.subject,
            "link": meeting.link,
            "date": meeting.date.isoformat(),
            "created_at": meeting.created_at.isoformat() if isinstance(meeting.created_at, datetime) else meeting.created_at,
            "updated_at": meeting.updated_at.isoformat() if isinstance(meeting.updated_at, datetime) else meeting.updated_at
        }
        for meeting in result
    ]
    return JSONResponse(content=meeting_list)


# Root route for the login page
@app.get("/", response_class=HTMLResponse)
async def get_login_form():
    with open('templates/login.html', 'r') as file:
        login_html = file.read()
    return HTMLResponse(content=login_html)

# Login route
@app.post("/login")
async def login(response: Response, db: Session = Depends(get_db), email: str = Form(...), password: str = Form(...)):
    query = user_table.select().where(user_table.c.email == email)
    result = db.execute(query).first()

    if result and verify_password(password, result.password):
        # Update the updated_at column with current timestamp
        update_query = (
            user_table.update()
            .where(user_table.c.email == email)
            .values(updated_at=func.now())
        )
        db.execute(update_query)
        db.commit()

        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(data={"sub": email}, expires_delta=access_token_expires)

        # Redirect based on whether the user is admin or not
        if result.is_admin:
            response = RedirectResponse(url="/admin_dashboard", status_code=303)
        else:
            response = RedirectResponse(url="/user_dashboard", status_code=303)

        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return response
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")


# Admin Dashboard route
@app.get("/admin_dashboard", response_class=HTMLResponse)
async def admin_dashboard():
    with open('templates/admin_dashboard.html', 'r') as file:
        return HTMLResponse(content=file.read())

@app.get("/get_admin_dashboard")
async def admin_dashboard():
    return FileResponse("templates/admin_dashboard.html")

@app.get("/manage_tickets")
async def manage_tickets():
    return FileResponse("templates/manage_ticket.html")

@app.get("/archives")
async def manage_tickets():
    return FileResponse("templates/archives.html")

@app.get("/meeting")
async def manage_tickets():
    return FileResponse("templates/manage_meets.html")
# User Dashboard route
@app.get("/user_dashboard", response_class=HTMLResponse)
async def user_dashboard():
    with open('templates/user_dashboard.html', 'r') as file:
        return HTMLResponse(content=file.read())

@app.get("/user_meeting", response_class=HTMLResponse)
async def user_dashboard():
    with open('templates/user_meetings.html', 'r') as file:
        return HTMLResponse(content=file.read())



@app.get("/users")
async def list_users(db: Session = Depends(get_db)):
    query = select(
        user_table.c.id,
        user_table.c.firstname,
        user_table.c.lastname,
        user_table.c.email,
        user_table.c.created_at,   # Include created_at
        user_table.c.updated_at    # Include updated_at
    ).where(user_table.c.is_deleted == 0)

    result = db.execute(query).fetchall()

    users_list = [
        {
            "id": user.id,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,  # Convert datetime to ISO format
            "updated_at": user.updated_at.isoformat() if user.updated_at else None   # Convert datetime to ISO format
        }
        for user in result
    ]
    return JSONResponse(content=users_list)



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
        .values(firstname=firstname, lastname=lastname, email=email, is_active=is_active, updated_at=func.now())
    )
    db.execute(update_stmt)
    db.commit()
    return JSONResponse(content={"message": "User updated successfully"})

@app.post("/update_ticket")
async def update_ticket_endpoint(
    id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    assigned_user_id: Optional[int] = Form(None),
    priorite: str = Form(...),
    db: Session = Depends(get_db)
):
    print(f"Update request received for ticket ID: {id}")

    # Check if the ticket already exists with the same title but a different ID
    query = ticket_table.select().where(ticket_table.c.title == title).where(ticket_table.c.id != id)
    result = db.execute(query).first()
    if result:
        raise HTTPException(status_code=400, detail="Ticket with this title already exists")

    # Create the update statement
    update_stmt = (
        update(ticket_table)
        .where(ticket_table.c.id == id)
        .values(
            title=title,
            description=description,
            assigned_user_id=assigned_user_id,
            priorite=priorite,
            updated_at=func.now()
        )
    )
    
    # Execute the update statement
    db.execute(update_stmt)
    db.commit()

    return JSONResponse(content={"message": "Ticket updated successfully"})



@app.post("/user_update_ticket")
async def user_update_ticket_endpoint(
    id: int = Form(...),
    status: str = Form(...),  # Accept the 'status' field
    db: Session = Depends(get_db)
):
    print(f"Update request received for ticket ID: {id} with new status: {status}")

    # Check if the ticket exists
    query = ticket_table.select().where(ticket_table.c.id == id)
    ticket = db.execute(query).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Update the ticket's status
    update_stmt = (
        update(ticket_table)
        .where(ticket_table.c.id == id)
        .values(
            status=status,               # Update the status field
            updated_at=func.now()   # Update the timestamp
        )
    )

    # Execute the update statement
    db.execute(update_stmt)
    db.commit()

    # Retrieve emails of users with is_admin = 1
    email_query = text("SELECT email FROM user WHERE is_admin = 1")
    admin_emails = db.execute(email_query).fetchall()

    # Send an email notification to each admin
    for email in admin_emails:
        send_email(email[0], f"Ticket ID {id} status changed to {status}")

    return JSONResponse(content={"message": "Ticket updated and admins notified successfully"})



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
        .values(password=hashed_temp_password, should_reset_password=1, updated_at=func.now())
    )
    db.execute(update_stmt)
    db.commit()
    send_email(result.email, temp_password)
    return JSONResponse(content={"message": "Password reset successfully"})

@app.post("/delete_user")
async def delete_user_endpoint(id: int = Form(...), db: Session = Depends(get_db)):
    print(f"Delete request received for user ID: {id}")
    update_stmt = (
        update(user_table)
        .where(user_table.c.id == id)
        .values(is_deleted=1, updated_at=func.now())
    )
    db.execute(update_stmt)
    db.commit()
    return JSONResponse(content={"message": "User deleted successfully"})



@app.post("/delete_ticket")
async def delete_ticket_endpoint(id: int = Form(...), db: Session = Depends(get_db)):
    print(f"Delete request received for ticket ID: {id}")
    
    # Hard delete the ticket from the database
    delete_stmt = delete(ticket_table).where(ticket_table.c.id == id)
    
    # Execute the delete statement
    db.execute(delete_stmt)
    db.commit()
    
    return JSONResponse(content={"message": "Ticket deleted successfully"})


# Create user route
@app.post("/create_user")
async def create_user(firstname: str = Form(...), lastname: str = Form(...), email: str = Form(...), is_admin: bool = Form(False), db: Session = Depends(get_db)):
    query = user_table.select().where(user_table.c.email == email)
    result = db.execute(query).first()
    if result:
        return JSONResponse(content={"message": "Email already exists"}, status_code=400)

    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    hashed_password = hash_password(password)
    new_user = user_table.insert().values(
        email=email,
        password=hashed_password,
        firstname=firstname,
        lastname=lastname,
        is_admin=is_admin,
        created_at=func.now(),
        updated_at=int(time.time())
    )
    db.execute(new_user)
    db.commit()

    # Send email with the generated password
    send_email(email, f"Your account has been created. Your password is: {password}")

    return JSONResponse(content={"message": "User created successfully"})

@app.post("/create_ticket")
async def create_ticket(
    title: str = Form(...),
    description: str = Form(...),
    assigned_user_id: Optional[int] = Form(None),  # Optional field for assigned_user_id
    created_by_user_id: int = Form(...), 
    priorite: str = Form(...), # ID of the user creating the ticket
    db: Session = Depends(get_db)
):
    current_time = int(time.time())  # Get the current timestamp

    try:
        # Create the ticket with or without assigned_user_id
        new_ticket = ticket_table.insert().values(
            title=title,
            description=description,
            status="To Do",  # Default status
            assigned_user_id=assigned_user_id if assigned_user_id is not None else None,
            created_by_user_id=created_by_user_id,
            created_at=func.now(),
            priorite=priorite
            
        )

        db.execute(new_ticket)  # Insert the ticket into the database
        db.commit()

        # If the ticket is assigned, send an email to the assigned user
        if assigned_user_id:
            assigned_user_query = user_table.select().where(user_table.c.id == assigned_user_id)
            assigned_user = db.execute(assigned_user_query).first()
            if assigned_user:
                send_email(assigned_user.email, f"You have been assigned a new ticket: {title}" f"\ndescription: {description}")

        return JSONResponse(content={"message": "Ticket created successfully"})
    
    except Exception as e:
        db.rollback()  # Roll back in case of any error
        return JSONResponse(content={"message": f"Error creating ticket: {str(e)}"}, status_code=500)



# List tickets for the user dashboard
@app.get("/tickets_user")
async def list_tickets(user_id: int, db: Session = Depends(get_db)):
    
    query = select(
        ticket_table.c.id,
        ticket_table.c.title,
        ticket_table.c.description,
        ticket_table.c.status,
        ticket_table.c.assigned_user_id
    ).where(ticket_table.c.assigned_user_id == user_id)

    result = db.execute(query).fetchall()

    tickets_list = [
        {
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status,
        }
        for ticket in result
    ]
    return JSONResponse(content=tickets_list)

@app.get("/tickets_admin")
async def list_tickets(user_id: int, db: Session = Depends(get_db)):
    try:
        # Query to join tickets with users to get the username
        query = select(
            ticket_table.c.id,
            ticket_table.c.title,
            ticket_table.c.description,
            ticket_table.c.status,
            ticket_table.c.priorite,
            ticket_table.c.assigned_user_id,
           func.concat(user_table.c.firstname, ' ', user_table.c.lastname).label("assigned_user_fullname")  # Concatenate firstname and lastname
        ).select_from(
            ticket_table.join(user_table, ticket_table.c.assigned_user_id == user_table.c.id, isouter=True)  # Left join to include tickets with null assigned_user_id
        )

        result = db.execute(query).fetchall()

        tickets_list = [
            {
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "status": ticket.status,
                "assigned_user_id": ticket.assigned_user_id,
                "assigned_user_fullname": ticket.assigned_user_fullname,
                "priorite": ticket.priorite,  # Include the username in the response
            }
            for ticket in result
        ]
        print(tickets_list)
        return JSONResponse(content=tickets_list)
    except SQLAlchemyError as e:
        return JSONResponse(content={"message": f"Error fetching tickets: {str(e)}"}, status_code=500)

@app.get("/tickets_admin_archive")
async def list_tickets(user_id: int, db: Session = Depends(get_db)):
    try:
        # Query to join tickets with users to get the username
        query = select(
            ticket_table.c.id,
            ticket_table.c.title,
            ticket_table.c.description,
            ticket_table.c.status,
            ticket_table.c.assigned_user_id,
            ticket_table.c.created_at,
            ticket_table.c.updated_at,
            ticket_table.c.priorite,
           func.concat(user_table.c.firstname, ' ', user_table.c.lastname).label("assigned_user_fullname")  # Concatenate firstname and lastname
        ).select_from(
            ticket_table.join(user_table, ticket_table.c.assigned_user_id == user_table.c.id, isouter=True)  # Left join to include tickets with null assigned_user_id
        ).where(ticket_table.c.status == "done")

        result = db.execute(query).fetchall()

        tickets_list = [
            {
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "status": ticket.status,
                "assigned_user_id": ticket.assigned_user_id,
                "assigned_user_fullname": ticket.assigned_user_fullname,
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "updated_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "priorite": ticket.priorite,  # Include the username in the response
            }
            for ticket in result
        ]
        return JSONResponse(content=tickets_list)
    except SQLAlchemyError as e:
        return JSONResponse(content={"message": f"Error fetching tickets: {str(e)}"}, status_code=500)

@app.get("/forgot_password", response_class=HTMLResponse)
async def forgot_password_form():
    with open('templates/forgot_password.html', 'r') as file:
        forgot_password_html = file.read()
    return HTMLResponse(content=forgot_password_html)

@app.post("/forgot_password")
async def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    query = user_table.select().where(user_table.c.email == email)
    result = db.execute(query).first()
    if result:
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        hashed_temp_password = hash_password(temp_password)
        update_stmt = (
            update(user_table)
            .where(user_table.c.email == email)
            .values(password=hashed_temp_password, should_reset_password=1)
        )
        db.execute(update_stmt)
        db.commit()
        send_email(email, temp_password)
        return JSONResponse(content={"message": "A temporary password has been sent to your email address."})
    else:
        raise HTTPException(status_code=400, detail="Email address not found")


# Logout route
@app.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

# Helper function to send emails
def send_email(to_email, message):
    from_email = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    msg = MIMEText(message)
    msg['Subject'] = 'Notification'
    msg['From'] = from_email
    msg['To'] = to_email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, email_password)
        server.sendmail(from_email, to_email, msg.as_string())
