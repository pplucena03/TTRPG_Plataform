from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    game_system = Column(String, nullable=False)
    
    # One-to-Many relationship: A campaign has many sessions
    sessions = relationship("Session", back_populates="campaign", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    title = Column(String, nullable=False)
    raw_notes = Column(String, nullable=False)
    # Storing lists (like hooks) as JSON is efficient in SQLite/Postgres
    unresolved_hooks = Column(JSON, nullable=False) 
    
    campaign = relationship("Campaign", back_populates="sessions")
    # One-to-Many relationship: A session extracts many entities
    entities = relationship("Entity", back_populates="session", cascade="all, delete-orphan")

class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    category = Column(String, nullable=False)
    status_or_detail = Column(String, nullable=False)
    
    session = relationship("Session", back_populates="entities")