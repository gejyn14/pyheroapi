"""
Data models for Kiwoom API responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BaseKiwoomResponse(BaseModel):
    """Base response model for all Kiwoom API responses."""
    return_code: int
    return_msg: str


class QuoteData(BaseModel):
    """Stock quote/order book data."""
    
    # Order book data
    bid_req_base_tm: Optional[str] = Field(None, description="호가잔량기준시간")
    
    # Sell orders (매도호가)
    sell_orders: List[Dict[str, str]] = Field(default_factory=list)
    
    # Buy orders (매수호가) 
    buy_orders: List[Dict[str, str]] = Field(default_factory=list)
    
    # Total quantities
    tot_sel_req: Optional[str] = Field(None, description="총매도잔량")
    tot_buy_req: Optional[str] = Field(None, description="총매수잔량")
    
    # After hours data
    ovt_sel_req: Optional[str] = Field(None, description="시간외매도잔량")
    ovt_buy_req: Optional[str] = Field(None, description="시간외매수잔량")


class MarketData(BaseModel):
    """Basic market data for a stock."""
    
    symbol: str = Field(..., description="종목코드")
    name: Optional[str] = Field(None, description="종목명")
    current_price: Optional[str] = Field(None, description="현재가")
    change_sign: Optional[str] = Field(None, description="대비기호")
    change_amount: Optional[str] = Field(None, description="전일대비")
    change_rate: Optional[str] = Field(None, description="등락율")
    volume: Optional[str] = Field(None, description="거래량")
    value: Optional[str] = Field(None, description="거래대금")


class OrderData(BaseModel):
    """Order execution data."""
    
    symbol: str = Field(..., description="종목코드")
    order_time: Optional[str] = Field(None, description="주문시간")
    execution_time: Optional[str] = Field(None, description="체결시간")
    price: Optional[str] = Field(None, description="가격")
    quantity: Optional[str] = Field(None, description="수량")
    side: Optional[str] = Field(None, description="매매구분")


class ETFData(BaseModel):
    """ETF specific data."""
    
    symbol: str = Field(..., description="종목코드")
    name: Optional[str] = Field(None, description="종목명")
    nav: Optional[str] = Field(None, description="NAV")
    tracking_error: Optional[str] = Field(None, description="추적오차율")
    discount_premium: Optional[str] = Field(None, description="괴리율")


class ELWData(BaseModel):
    """ELW (Equity Linked Warrant) specific data."""
    
    symbol: str = Field(..., description="종목코드")
    name: Optional[str] = Field(None, description="종목명")
    underlying_asset: Optional[str] = Field(None, description="기초자산")
    strike_price: Optional[str] = Field(None, description="행사가격")
    expiry_date: Optional[str] = Field(None, description="만기일")
    conversion_ratio: Optional[str] = Field(None, description="전환비율")
    delta: Optional[str] = Field(None, description="델타")
    gamma: Optional[str] = Field(None, description="감마")
    theta: Optional[str] = Field(None, description="쎄타")
    vega: Optional[str] = Field(None, description="베가")


class AccountBalance(BaseModel):
    """Account balance information."""
    
    account_number: str = Field(..., description="계좌번호")
    total_balance: Optional[str] = Field(None, description="총잔고")
    available_balance: Optional[str] = Field(None, description="주문가능금액")
    deposit: Optional[str] = Field(None, description="예수금")
    substitute: Optional[str] = Field(None, description="대용금")


class Position(BaseModel):
    """Stock position information."""
    
    symbol: str = Field(..., description="종목코드")
    name: Optional[str] = Field(None, description="종목명") 
    quantity: Optional[str] = Field(None, description="보유수량")
    available_quantity: Optional[str] = Field(None, description="매도가능수량")
    average_price: Optional[str] = Field(None, description="평균단가")
    current_price: Optional[str] = Field(None, description="현재가")
    evaluation_amount: Optional[str] = Field(None, description="평가금액")
    profit_loss: Optional[str] = Field(None, description="평가손익")
    profit_loss_rate: Optional[str] = Field(None, description="수익률")


class TokenRequest(BaseModel):
    """Request model for token issuance (au10001)."""
    
    grant_type: str = Field("client_credentials", description="grant_type")
    appkey: str = Field(..., description="앱키")
    secretkey: str = Field(..., description="시크릿키")


class TokenResponse(BaseKiwoomResponse):
    """Response model for token issuance (au10001)."""
    
    expires_dt: str = Field(..., description="만료일")
    token_type: str = Field(..., description="토큰타입")
    token: str = Field(..., description="접근토큰")


class TokenRevokeRequest(BaseModel):
    """Request model for token revocation (au10002)."""
    
    appkey: str = Field(..., description="앱키")
    secretkey: str = Field(..., description="시크릿키")
    token: str = Field(..., description="접근토큰")


class TokenRevokeResponse(BaseKiwoomResponse):
    """Response model for token revocation (au10002)."""
    pass  # Only contains base response fields 