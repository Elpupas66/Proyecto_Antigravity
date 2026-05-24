from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class TradeState(str, Enum):
    RECEIVED = "RECEIVED"
    AI_VALIDATED = "AI_VALIDATED"
    AI_REJECTED = "AI_REJECTED"
    RISK_APPROVED = "RISK_APPROVED"
    RISK_REJECTED = "RISK_REJECTED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    APPROVED_BY_USER = "APPROVED_BY_USER"
    REJECTED_BY_USER = "REJECTED_BY_USER"
    SENT_TO_GATEKEEPER = "SENT_TO_GATEKEEPER"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    KILLED = "KILLED"

class Signal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    action: str  # BUY or SELL
    timeframe: str
    price: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "TradingView"

class TradeIntent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal_id: str
    symbol: str
    action: str
    lot_size: float = 0.01
    entry_price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    state: TradeState = TradeState.RECEIVED
    ai_reason: Optional[str] = None
    risk_reason: Optional[str] = None
    is_real_execution_intent: bool = False
    is_user_approved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AccountState(BaseModel):
    balance: float
    equity: float
    daily_loss_pct: float
    open_trades: int
    max_daily_loss_pct: float
    max_concurrent_trades: int
    allow_real_execution: bool
    require_approval: bool

class RiskResult(BaseModel):
    approved: bool
    reason: str
    failed_rules: list[str]
    risk_score: float

class LogEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trade_id: str
    state: TradeState
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
