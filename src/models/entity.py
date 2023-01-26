from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from db.db import Base


class Url(Base):
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True)
    full_url = Column(String(100), unique=True, nullable=False)
    short_url = Column(String(100), unique=True, nullable=False)
    clicks = Column(Integer, unique=False, default=0)
    is_active = Column(Boolean, default=True)


class Click(Base):
    __tablename__ = 'clicks'
    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, ForeignKey('urls.id'))
    date = Column(DateTime, index=True, default=datetime.utcnow)
    client = Column(String(100), unique=False, nullable=False)
