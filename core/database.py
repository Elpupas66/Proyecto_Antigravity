import os
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# La DB se guardará en la raíz del proyecto, fuera de core/
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "antigravity_core.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class TradeDB(Base):
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True, index=True)
    signal_id = Column(String, index=True)
    symbol = Column(String)
    action = Column(String)
    lot_size = Column(Float)
    sl = Column(Float, nullable=True)
    tp = Column(Float, nullable=True)
    state = Column(String, index=True)
    ai_reason = Column(String, nullable=True)
    risk_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class LogEventDB(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, index=True)
    trade_id = Column(String, index=True)
    state = Column(String)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)
