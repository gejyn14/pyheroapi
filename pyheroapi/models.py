"""
Data models for Kiwoom API responses using Pydantic for validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class OrderType(str, Enum):
    """Order type enumeration"""

    NORMAL = "0"  # 보통
    MARKET = "3"  # 시장가
    CONDITIONAL_LIMIT = "5"  # 조건부지정가
    AFTER_HOURS_CLOSE = "81"  # 장마감후시간외
    BEFORE_HOURS_OPEN = "61"  # 장시작전시간외
    AFTER_HOURS_SINGLE = "62"  # 시간외단일가
    BEST_LIMIT = "6"  # 최유리지정가
    PRIORITY_LIMIT = "7"  # 최우선지정가
    NORMAL_IOC = "10"  # 보통(IOC)
    MARKET_IOC = "13"  # 시장가(IOC)
    BEST_IOC = "16"  # 최유리(IOC)
    NORMAL_FOK = "20"  # 보통(FOK)
    MARKET_FOK = "23"  # 시장가(FOK)
    BEST_FOK = "26"  # 최유리(FOK)
    STOP_LIMIT = "28"  # 스톱지정가
    MID_PRICE = "29"  # 중간가
    MID_PRICE_IOC = "30"  # 중간가(IOC)
    MID_PRICE_FOK = "31"  # 중간가(FOK)


class MarketType(str, Enum):
    """Market type enumeration"""

    KRX = "KRX"
    NASDAQ = "NXT"
    SOR = "SOR"


class BaseKiwoomResponse(BaseModel):
    """Base response model for all Kiwoom API responses."""

    return_code: int
    return_msg: str


class QuoteData(BaseModel):
    """Stock quote/order book data."""

    # Order book data
    bid_req_base_tm: Optional[str] = Field(None, description="호가잔량기준시간")

    # Best prices (most important for current price info)
    buy_fpr_bid: Optional[str] = Field(None, description="매수최우선호가")
    buy_fpr_req: Optional[str] = Field(None, description="매수최우선잔량")
    sel_fpr_bid: Optional[str] = Field(None, description="매도최우선호가")
    sel_fpr_req: Optional[str] = Field(None, description="매도최우선잔량")

    # Total quantities
    tot_sel_req: Optional[str] = Field(None, description="총매도잔량")
    tot_buy_req: Optional[str] = Field(None, description="총매수잔량")

    # After hours data
    ovt_sel_req: Optional[str] = Field(None, description="시간외매도잔량")
    ovt_buy_req: Optional[str] = Field(None, description="시간외매수잔량")

    # Additional order book levels (2-10)
    buy_2th_pre_bid: Optional[str] = Field(None, description="매수2차선호가")
    buy_2th_pre_req: Optional[str] = Field(None, description="매수2차선잔량")
    buy_3th_pre_bid: Optional[str] = Field(None, description="매수3차선호가")
    buy_3th_pre_req: Optional[str] = Field(None, description="매수3차선잔량")
    buy_4th_pre_bid: Optional[str] = Field(None, description="매수4차선호가")
    buy_4th_pre_req: Optional[str] = Field(None, description="매수4차선잔량")
    buy_5th_pre_bid: Optional[str] = Field(None, description="매수5차선호가")
    buy_5th_pre_req: Optional[str] = Field(None, description="매수5차선잔량")

    sel_2th_pre_bid: Optional[str] = Field(None, description="매도2차선호가")
    sel_2th_pre_req: Optional[str] = Field(None, description="매도2차선잔량")
    sel_3th_pre_bid: Optional[str] = Field(None, description="매도3차선호가")
    sel_3th_pre_req: Optional[str] = Field(None, description="매도3차선잔량")
    sel_4th_pre_bid: Optional[str] = Field(None, description="매도4차선호가")
    sel_4th_pre_req: Optional[str] = Field(None, description="매도4차선잔량")
    sel_5th_pre_bid: Optional[str] = Field(None, description="매도5차선호가")
    sel_5th_pre_req: Optional[str] = Field(None, description="매도5차선잔량")


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
    grant_type: str
    appkey: str
    secretkey: str


class TokenResponse(BaseModel):
    expires_dt: str
    token_type: str
    token: str
    return_code: int = 0
    return_msg: str = ""


class TokenRevokeRequest(BaseModel):
    appkey: str
    secretkey: str
    token: str


class TokenRevokeResponse(BaseModel):
    return_code: int = 0
    return_msg: str = ""


# Trading Models
class OrderRequest(BaseModel):
    """Base order request model"""

    dmst_stex_tp: str = Field(..., description="국내거래소구분 (KRX,NXT,SOR)")
    stk_cd: str = Field(..., description="종목코드")
    ord_qty: str = Field(..., description="주문수량")
    ord_uv: Optional[str] = Field(None, description="주문단가")
    trde_tp: str = Field(..., description="매매구분")
    cond_uv: Optional[str] = Field(None, description="조건단가")


class OrderResponse(BaseModel):
    """Order response model"""

    ord_no: Optional[str] = Field(None, description="주문번호")
    dmst_stex_tp: Optional[str] = Field(None, description="국내거래소구분")
    return_code: int = 0
    return_msg: str = ""


class ModifyOrderRequest(BaseModel):
    """Order modification request model"""

    dmst_stex_tp: str = Field(..., description="국내거래소구분")
    orig_ord_no: str = Field(..., description="원주문번호")
    stk_cd: str = Field(..., description="종목코드")
    mdfy_qty: str = Field(..., description="정정수량")
    mdfy_uv: str = Field(..., description="정정단가")
    mdfy_cond_uv: Optional[str] = Field(None, description="정정조건단가")


class ModifyOrderResponse(BaseModel):
    """Order modification response model"""

    ord_no: Optional[str] = Field(None, description="주문번호")
    base_orig_ord_no: Optional[str] = Field(None, description="모주문번호")
    mdfy_qty: Optional[str] = Field(None, description="정정수량")
    dmst_stex_tp: Optional[str] = Field(None, description="국내거래소구분")
    return_code: int = 0
    return_msg: str = ""


class CancelOrderRequest(BaseModel):
    """Order cancellation request model"""

    dmst_stex_tp: str = Field(..., description="국내거래소구분")
    orig_ord_no: str = Field(..., description="원주문번호")
    stk_cd: str = Field(..., description="종목코드")
    cncl_qty: str = Field(..., description="취소수량")


class CancelOrderResponse(BaseModel):
    """Order cancellation response model"""

    ord_no: Optional[str] = Field(None, description="주문번호")
    base_orig_ord_no: Optional[str] = Field(None, description="모주문번호")
    cncl_qty: Optional[str] = Field(None, description="취소수량")
    dmst_stex_tp: Optional[str] = Field(None, description="국내거래소구분")
    return_code: int = 0
    return_msg: str = ""


# Enhanced Market Data Models
class IntradayPrice(BaseModel):
    """Intraday price data model"""

    date: Optional[str] = None
    time: Optional[str] = None
    open_pric: Optional[str] = None
    high_pric: Optional[str] = None
    low_pric: Optional[str] = None
    close_pric: Optional[str] = None
    pre: Optional[str] = None
    flu_rt: Optional[str] = None
    trde_qty: Optional[str] = None
    trde_prica: Optional[str] = None
    cntr_str: Optional[str] = None


class MarketPerformance(BaseModel):
    """Market performance indicators model"""

    stk_nm: Optional[str] = None
    stk_cd: Optional[str] = None
    date: Optional[str] = None
    tm: Optional[str] = None
    pred_close_pric: Optional[str] = None
    pred_trde_qty: Optional[str] = None
    upl_pric: Optional[str] = None
    lst_pric: Optional[str] = None
    pred_trde_prica: Optional[str] = None
    flo_stkcnt: Optional[str] = None
    cur_prc: Optional[str] = None
    smbol: Optional[str] = None
    flu_rt: Optional[str] = None
    pred_rt: Optional[str] = None
    open_pric: Optional[str] = None
    high_pric: Optional[str] = None
    low_pric: Optional[str] = None
    cntr_qty: Optional[str] = None
    trde_qty: Optional[str] = None
    trde_prica: Optional[str] = None
    exp_cntr_pric: Optional[str] = None
    exp_cntr_qty: Optional[str] = None
    exp_sel_pri_bid: Optional[str] = None
    exp_buy_pri_bid: Optional[str] = None


# Account Models
class RealizedProfitLoss(BaseModel):
    """Realized profit/loss model"""

    stk_nm: Optional[str] = None
    cntr_qty: Optional[str] = None
    buy_uv: Optional[str] = None
    cntr_pric: Optional[str] = None
    tdy_sel_pl: Optional[str] = None
    pl_rt: Optional[str] = None
    stk_cd: Optional[str] = None
    tdy_trde_cmsn: Optional[str] = None
    tdy_trde_tax: Optional[str] = None
    wthd_alowa: Optional[str] = None
    loan_dt: Optional[str] = None
    crd_tp: Optional[str] = None


class UnfilledOrder(BaseModel):
    """Unfilled order model"""

    ord_no: Optional[str] = None
    stk_cd: Optional[str] = None
    stk_nm: Optional[str] = None
    ord_qty: Optional[str] = None
    ord_uv: Optional[str] = None
    ord_dvsn: Optional[str] = None
    ord_tm: Optional[str] = None
    cntr_qty: Optional[str] = None
    cntr_uv: Optional[str] = None
    rmn_qty: Optional[str] = None


class FilledOrder(BaseModel):
    """Filled order model"""

    ord_no: Optional[str] = None
    stk_cd: Optional[str] = None
    stk_nm: Optional[str] = None
    ord_qty: Optional[str] = None
    ord_uv: Optional[str] = None
    cntr_qty: Optional[str] = None
    cntr_uv: Optional[str] = None
    cntr_tm: Optional[str] = None
    ord_dvsn: Optional[str] = None


class TradingJournal(BaseModel):
    """Daily trading journal model"""

    stk_cd: Optional[str] = None
    stk_nm: Optional[str] = None
    buy_qty: Optional[str] = None
    sel_qty: Optional[str] = None
    buy_amt: Optional[str] = None
    sel_amt: Optional[str] = None
    rlzt_pl: Optional[str] = None
    fee: Optional[str] = None
    tax: Optional[str] = None


class DepositDetail(BaseModel):
    """Deposit detail model"""

    tot_evla_amt: Optional[str] = None
    scts_evla_amt: Optional[str] = None
    tot_dncl_amt: Optional[str] = None
    nxdy_excc_amt: Optional[str] = None
    nxdy_auto_rdpt_amt: Optional[str] = None
    ord_psbl_cash: Optional[str] = None


class AssetEvaluation(BaseModel):
    """Asset evaluation model"""

    evla_amt: Optional[str] = None
    bfdy_evla_amt: Optional[str] = None
    evla_pfls_amt: Optional[str] = None
    evla_pfls_rt: Optional[str] = None
    scts_evla_amt: Optional[str] = None
