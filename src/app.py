"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import init_db, get_db, Activity, signups

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with their participants"""
    activities_list = db.query(Activity).all()
    
    result = {}
    for activity in activities_list:
        # Get participants for this activity
        participants_query = select(signups.c.participant_email).where(
            signups.c.activity_id == activity.id
        )
        participants = [row[0] for row in db.execute(participants_query)]
        
        result[activity.name] = activity.to_dict(participants)
    
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Validate activity exists
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get current participants
    participants_query = select(signups.c.participant_email).where(
        signups.c.activity_id == activity.id
    )
    participants = [row[0] for row in db.execute(participants_query)]

    # Validate student is not already signed up
    if email in participants:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student to signup table
    db.execute(
        signups.insert().values(
            activity_id=activity.id,
            participant_email=email
        )
    )
    db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    # Validate activity exists
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if student is signed up
    existing_signup = db.execute(
        select(signups).where(
            signups.c.activity_id == activity.id,
            signups.c.participant_email == email
        )
    ).first()
    
    if not existing_signup:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student from signup table
    db.execute(
        signups.delete().where(
            signups.c.activity_id == activity.id,
            signups.c.participant_email == email
        )
    )
    db.commit()
    
    return {"message": f"Unregistered {email} from {activity_name}"}
