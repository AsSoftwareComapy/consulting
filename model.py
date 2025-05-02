from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class WhatsAppMessageLog(Base):
    __tablename__ = "whatsapp_message_logs"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, nullable=False)
    full_name = Column(String)
    location = Column(String)
    qualification = Column(String)
    status_code = Column(Integer)
    response_text = Column(Text)
    sent_at = Column(DateTime)
