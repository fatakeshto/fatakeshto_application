from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    error_type = Column(String(255))
    error_message = Column(Text)
    endpoint = Column(String(255))
    request_method = Column(String(50))
    request_body = Column(Text, nullable=True)
    status_code = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(255), nullable=True)
    stack_trace = Column(Text, nullable=True)

    # Relationship with User model
    user = relationship("User", backref="error_logs")