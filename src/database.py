"""
Database configuration and models for the High School Management System.
"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os
from pathlib import Path

# Database setup
DATABASE_DIR = Path(__file__).parent / "data"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/school.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Association table for many-to-many relationship between activities and participants
signups = Table(
    'signups',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('activity_id', Integer, ForeignKey('activities.id')),
    Column('participant_email', String, nullable=False)
)


class Activity(Base):
    """Activity model representing extracurricular activities"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    schedule = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)

    def to_dict(self, participants=None):
        """Convert activity to dictionary format"""
        return {
            "description": self.description,
            "schedule": self.schedule,
            "max_participants": self.max_participants,
            "participants": participants or []
        }


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with tables and seed data"""
    Base.metadata.create_all(bind=engine)
    
    # Seed initial data if database is empty
    db = SessionLocal()
    try:
        if db.query(Activity).count() == 0:
            initial_activities = [
                {
                    "name": "Chess Club",
                    "description": "Learn strategies and compete in chess tournaments",
                    "schedule": "Fridays, 3:30 PM - 5:00 PM",
                    "max_participants": 12,
                    "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
                },
                {
                    "name": "Programming Class",
                    "description": "Learn programming fundamentals and build software projects",
                    "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                    "max_participants": 20,
                    "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
                },
                {
                    "name": "Gym Class",
                    "description": "Physical education and sports activities",
                    "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                    "max_participants": 30,
                    "participants": ["john@mergington.edu", "olivia@mergington.edu"]
                },
                {
                    "name": "Soccer Team",
                    "description": "Join the school soccer team and compete in matches",
                    "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                    "max_participants": 22,
                    "participants": ["liam@mergington.edu", "noah@mergington.edu"]
                },
                {
                    "name": "Basketball Team",
                    "description": "Practice and play basketball with the school team",
                    "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                    "max_participants": 15,
                    "participants": ["ava@mergington.edu", "mia@mergington.edu"]
                },
                {
                    "name": "Art Club",
                    "description": "Explore your creativity through painting and drawing",
                    "schedule": "Thursdays, 3:30 PM - 5:00 PM",
                    "max_participants": 15,
                    "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
                },
                {
                    "name": "Drama Club",
                    "description": "Act, direct, and produce plays and performances",
                    "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
                    "max_participants": 20,
                    "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
                },
                {
                    "name": "Math Club",
                    "description": "Solve challenging problems and participate in math competitions",
                    "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
                    "max_participants": 10,
                    "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
                },
                {
                    "name": "Debate Team",
                    "description": "Develop public speaking and argumentation skills",
                    "schedule": "Fridays, 4:00 PM - 5:30 PM",
                    "max_participants": 12,
                    "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
                }
            ]
            
            for activity_data in initial_activities:
                participants = activity_data.pop("participants", [])
                activity = Activity(**activity_data)
                db.add(activity)
                db.flush()  # Get the activity ID
                
                # Add initial participants
                for email in participants:
                    db.execute(
                        signups.insert().values(
                            activity_id=activity.id,
                            participant_email=email
                        )
                    )
            
            db.commit()
            print("Database initialized with seed data")
    finally:
        db.close()
