from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    analyses = relationship("PostAnalysis", back_populates="owner", cascade="all, delete-orphan")

class PostAnalysis(Base):
    __tablename__ = "post_analyses"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # x|instagram|youtube|tiktok
    url = Column(Text, nullable=False)
    status = Column(String(20), default="completed")  # queued|running|completed|failed
    summary_positive = Column(Integer, default=0)
    summary_negative = Column(Integer, default=0)
    summary_neutral = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="analyses")
    comments = relationship("Comment", back_populates="analysis", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("post_analyses.id"), nullable=False)
    author = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    label = Column(String(20), nullable=False)  # positive|negative|neutral
    score = Column(Integer, nullable=False)     # 0..100

    analysis = relationship("PostAnalysis", back_populates="comments")
