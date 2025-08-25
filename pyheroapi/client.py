"""
Main client for Kiwoom Securities REST API.
"""

import time
import os
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import requests

from .exceptions import (
    KiwoomAPIError,
    KiwoomAuthError,
    KiwoomRateLimitError,
    KiwoomRequestError,
    KiwoomServerError,
)
from .models import (
    AccountBalance,
    CancelOrderRequest,
    CancelOrderResponse,
    ELWData,
    ETFData,
    MarketData,
    ModifyOrderRequest,
    ModifyOrderResponse,
    OrderData,
    OrderRequest,
    OrderResponse,
    Position,
    QuoteData,
    TokenRequest,
    TokenResponse,
    TokenRevokeRequest,
    TokenRevokeResponse,
)

# Import realtime module (optional dependency)
try:
    from .realtime import KiwoomRealtimeClient
    _REALTIME_AVAILABLE = True
except ImportError:
    KiwoomRealtimeClient = None  # type: ignore
    _REALTIME_AVAILABLE = False


class KiwoomClient:
    """
    Main client for interacting with Kiwoom Securities REST API.

    This client provides easy-to-use methods for:
    - Market data retrieval
    - Quote/order book data
    - ETF and ELW information
    - Account management
    - Order placement and tracking
    """

    # API Base URLs
    PRODUCTION_URL = "https://api.kiwoom.com"
    SANDBOX_URL = "https://mockapi.kiwoom.com"

    def __init__(
        self,
        access_token: str,
        is_production: bool = True,
        timeout: int = 30,
        retry_attempts: int = 3,
        rate_limit_delay: float = 0.1,
    ):
        """
        Initialize Kiwoom API client.

        Args:
            access_token: Your Kiwoom API access token
            is_production: Whether to use production (default) or sandbox environment
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
            rate_limit_delay: Delay between requests to avoid rate limiting
        """
        self.access_token = access_token
        self.base_url = self.PRODUCTION_URL if is_production else self.SANDBOX_URL
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.rate_limit_delay = rate_limit_delay
        self.is_production = is_production

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            }
        )

        # Real-time client (lazy initialization)
        self._realtime_client: Optional[KiwoomRealtimeClient] = None

    @property
    def realtime(self) -> KiwoomRealtimeClient:
        """
        Get the real-time client for WebSocket streaming.
        
        Returns:
            KiwoomRealtimeClient instance for real-time data streaming
            
        Raises:
            ImportError: If websockets library is not installed
        """
        if not _REALTIME_AVAILABLE:
            raise ImportError(
                "Real-time functionality requires 'websockets' library. "
                "Install with: pip install pyheroapi[realtime] or pip install websockets"
            )
        
        if self._realtime_client is None:
            self._realtime_client = KiwoomRealtimeClient(
                access_token=self.access_token,
                is_production=self.is_production
            )
        
        return self._realtime_client

    @classmethod
    def create_with_credentials(
        cls, appkey: str, secretkey: str, is_production: bool = True, **kwargs
    ) -> "KiwoomClient":
        """
        Create a client instance by automatically obtaining an access token.

        Args:
            appkey: App key from Kiwoom Securities
            secretkey: Secret key from Kiwoom Securities
            is_production: Whether to use production (default) or sandbox environment
            **kwargs: Additional arguments for KiwoomClient constructor

        Returns:
            Configured KiwoomClient instance
        """
        # For sandbox mode, check if mock environment variables are set
        if not is_production:
            mock_appkey = os.getenv("MOCK_KIWOOM_APPKEY")
            mock_secretkey = os.getenv("MOCK_KIWOOM_SECRETKEY")
            
            if mock_appkey and mock_secretkey:
                appkey = mock_appkey
                secretkey = mock_secretkey
        
        token_response = cls.issue_token(appkey, secretkey, is_production)
        return cls(
            access_token=token_response.token, is_production=is_production, **kwargs
        )

    @staticmethod
    def issue_token(
        appkey: str, secretkey: str, is_production: bool = True
    ) -> TokenResponse:
        """
        Issue a new access token using app credentials (au10001).

        Args:
            appkey: App key from Kiwoom Securities
            secretkey: Secret key from Kiwoom Securities
            is_production: Whether to use production (default) or sandbox environment

        Returns:
            TokenResponse with access token and expiration info
        """
        # For sandbox mode, check if mock environment variables are set
        if not is_production:
            mock_appkey = os.getenv("MOCK_KIWOOM_APPKEY")
            mock_secretkey = os.getenv("MOCK_KIWOOM_SECRETKEY")
            
            if mock_appkey and mock_secretkey:
                appkey = mock_appkey
                secretkey = mock_secretkey
        
        base_url = (
            KiwoomClient.PRODUCTION_URL if is_production else KiwoomClient.SANDBOX_URL
        )
        url = urljoin(base_url, "/oauth2/token")

        token_request = TokenRequest(
            grant_type="client_credentials", appkey=appkey, secretkey=secretkey
        )

        headers = {"Content-Type": "application/json;charset=UTF-8"}

        response = requests.post(
            url, json=token_request.model_dump(), headers=headers, timeout=30
        )

        if response.status_code != 200:
            raise KiwoomAuthError(f"Token issuance failed: {response.status_code}")

        try:
            response_data = response.json()
        except ValueError as e:
            raise KiwoomAPIError(f"Invalid JSON response: {e}")

        if response_data.get("return_code") != 0:
            error_msg = response_data.get("return_msg", "Unknown error")
            raise KiwoomAuthError(f"Token issuance failed: {error_msg}")

        return TokenResponse(**response_data)

    @staticmethod
    def revoke_token(
        appkey: str, secretkey: str, token: str, is_production: bool = False
    ) -> TokenRevokeResponse:
        """
        Revoke an access token (au10002).

        Args:
            appkey: App key from Kiwoom Securities
            secretkey: Secret key from Kiwoom Securities
            token: Access token to revoke
            is_production: Whether to use production or sandbox environment

        Returns:
            TokenRevokeResponse with revocation status
        """
        # For sandbox mode, check if mock environment variables are set
        if not is_production:
            mock_appkey = os.getenv("MOCK_KIWOOM_APPKEY")
            mock_secretkey = os.getenv("MOCK_KIWOOM_SECRETKEY")
            
            if mock_appkey and mock_secretkey:
                appkey = mock_appkey
                secretkey = mock_secretkey
        
        base_url = (
            KiwoomClient.PRODUCTION_URL if is_production else KiwoomClient.SANDBOX_URL
        )
        url = urljoin(base_url, "/oauth2/revoke")

        token_revoke_request = TokenRevokeRequest(
            appkey=appkey, secretkey=secretkey, token=token
        )

        headers = {"Content-Type": "application/json;charset=UTF-8"}

        response = requests.post(
            url, json=token_revoke_request.model_dump(), headers=headers, timeout=30
        )

        if response.status_code != 200:
            raise KiwoomAuthError(f"Token revocation failed: {response.status_code}")

        try:
            response_data = response.json()
        except ValueError as e:
            raise KiwoomAPIError(f"Invalid JSON response: {e}")

        if response_data.get("return_code") != 0:
            error_msg = response_data.get("return_msg", "Unknown error")
            raise KiwoomAuthError(f"Token revocation failed: {error_msg}")

        return TokenRevokeResponse(**response_data)

    def revoke_current_token(self, appkey: str, secretkey: str) -> TokenRevokeResponse:
        """
        Revoke the current access token being used by this client.

        Args:
            appkey: App key from Kiwoom Securities
            secretkey: Secret key from Kiwoom Securities

        Returns:
            TokenRevokeResponse confirming revocation
        """
        return self.revoke_token(
            appkey=appkey,
            secretkey=secretkey,
            token=self.access_token,
            is_production=(self.base_url == self.PRODUCTION_URL),
        )

    def _make_request(
        self,
        endpoint: str,
        api_id: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cont_yn: Optional[str] = None,
        next_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to the Kiwoom API with error handling and retries.

        Args:
            endpoint: API endpoint path
            api_id: TR code/API ID
            data: Request body data
            headers: Additional headers
            cont_yn: Continuation flag for paginated requests
            next_key: Next key for paginated requests

        Returns:
            API response as dictionary

        Raises:
            KiwoomAPIError: For various API errors
        """
        url = urljoin(self.base_url, endpoint)

        # Set up headers
        request_headers = self.session.headers.copy()
        request_headers["api-id"] = api_id

        if cont_yn:
            request_headers["cont-yn"] = cont_yn
        if next_key:
            request_headers["next-key"] = next_key
        if headers:
            request_headers.update(headers)

        # Prepare request data
        json_data = data or {}

        for attempt in range(self.retry_attempts):
            try:
                # Rate limiting
                if attempt > 0:
                    time.sleep(self.rate_limit_delay * (2**attempt))

                response = self.session.post(
                    url, json=json_data, headers=request_headers, timeout=self.timeout
                )

                # Handle HTTP errors
                if response.status_code == 401:
                    raise KiwoomAuthError(
                        "Authentication failed. Check your access token."
                    )
                elif response.status_code == 429:
                    raise KiwoomRateLimitError(
                        "Rate limit exceeded. Please slow down requests."
                    )
                elif response.status_code >= 500:
                    raise KiwoomServerError(f"Server error: {response.status_code}")
                elif response.status_code >= 400:
                    raise KiwoomRequestError(
                        f"Request failed: {response.status_code}",
                        status_code=response.status_code,
                    )

                # Parse response
                try:
                    response_data = response.json()
                except ValueError as e:
                    raise KiwoomAPIError(f"Invalid JSON response: {e}")

                # Check API response code
                return_code = response_data.get("return_code")
                if return_code != 0:
                    error_msg = response_data.get("return_msg", "Unknown error")
                    raise KiwoomRequestError(
                        f"API error {return_code}: {error_msg}",
                        response_data=response_data,
                    )

                return response_data

            except (requests.RequestException, KiwoomRateLimitError, KiwoomServerError) as e:
                if attempt == self.retry_attempts - 1:
                    raise KiwoomAPIError(
                        f"Request failed after {self.retry_attempts} attempts: {e}"
                    )
                continue

        raise KiwoomAPIError("Max retry attempts exceeded")

    # Market Data Methods

    def get_quote(self, symbol: str) -> QuoteData:
        """
        Get real-time quote/order book data for a stock.

        Args:
            symbol: Stock symbol (e.g., "005930" for Samsung Electronics)

        Returns:
            QuoteData object with order book information
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10004", data)

        return QuoteData(**response)

    def get_market_data(self, symbol: str) -> MarketData:
        """
        Get basic market data for a stock.

        Args:
            symbol: Stock symbol

        Returns:
            MarketData object with price and volume information
        """
        quote_data = self.get_quote(symbol)

        # Extract basic market data from quote response
        return MarketData(
            symbol=symbol,
            # Map relevant fields from quote data
            # This would need to be adjusted based on actual response structure
        )

    def get_daily_prices(
        self, symbol: str, period: str = "D", count: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical daily price data.

        Args:
            symbol: Stock symbol
            period: Time period ("D" for daily, "W" for weekly, "M" for monthly)
            count: Number of data points to retrieve

        Returns:
            List of daily price data
        """
        data = {"stk_cd": symbol, "period": period}
        if count:
            data["count"] = count

        response = self._make_request("/api/dostk/mrkcond", "ka10005", data)
        return response.get("daily_data", [])

    # ETF Methods

    def get_etf_info(self, symbol: str) -> ETFData:
        """
        Get ETF information including NAV and tracking error.

        Args:
            symbol: ETF symbol

        Returns:
            ETFData object with ETF-specific information
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/etf", "ka40002", data)

        return ETFData(
            symbol=symbol,
            name=response.get("stk_nm"),
            nav=response.get("nav"),
            tracking_error=response.get("trace_eor_rt"),
            # Map other relevant fields
        )

    def get_etf_returns(
        self, symbol: str, etf_index_code: str, period: str = "3"
    ) -> Dict[str, Any]:
        """
        Get ETF return data.

        Args:
            symbol: ETF symbol
            etf_index_code: ETF target index code
            period: Period ("0" for 1 week, "1" for 1 month, "2" for 6 months, "3" for 1 year)

        Returns:
            ETF return information
        """
        data = {"stk_cd": symbol, "etfobjt_idex_cd": etf_index_code, "dt": period}
        response = self._make_request("/api/dostk/etf", "ka40001", data)
        return response.get("etfprft_rt_lst", [])

    def get_etf_daily_trend(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get ETF daily trend data (ka40003).

        Args:
            symbol: ETF symbol

        Returns:
            List of daily trend data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/etf", "ka40003", data)
        return response.get("etfdaly_trnsn", [])

    def get_etf_all_market_data(
        self,
        tax_type: str = "0",        # 과세유형 (0:전체, 1:비과세, 2:보유기간과세, etc.)
        nav_comparison: str = "0",  # NAV대비 (0:전체, 1:NAV > 전일종가, 2:NAV < 전일종가)
        management_company: str = "0000",  # 운용사 (0000:전체, 3020:KODEX, etc.)
        tax_status: str = "0",      # 과세여부 (0:전체, 1:과세, 2:비과세)
        tracking_index: str = "0",  # 추적지수 (0:전체)
        exchange_type: str = "1"    # 거래소구분 (1:KRX, 2:NXT, 3:통합)
    ) -> List[Dict[str, Any]]:
        """
        Get all ETF market data (ka40004).

        Args:
            tax_type: 과세유형 (0:전체, 1:비과세, 2:보유기간과세, etc.)
            nav_comparison: NAV대비 (0:전체, 1:NAV > 전일종가, 2:NAV < 전일종가)
            management_company: 운용사 (0000:전체, 3020:KODEX, etc.)
            tax_status: 과세여부 (0:전체, 1:과세, 2:비과세)
            tracking_index: 추적지수 (0:전체)
            exchange_type: 거래소구분 (1:KRX, 2:NXT, 3:통합)

        Returns:
            List of all ETF market data
        """
        data = {
            "txon_type": tax_type,
            "navpre": nav_comparison,
            "mngmcomp": management_company,
            "txon_yn": tax_status,
            "trace_idex": tracking_index,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/etf", "ka40004", data)
        return response.get("etfall_mrpr", [])

    def get_etf_time_series_trend(self, symbol: str) -> Dict[str, Any]:
        """
        Get ETF time series trend data (ka40006).

        Args:
            symbol: ETF symbol

        Returns:
            Dictionary containing ETF time series trend data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/etf", "ka40006", data)
        return response

    def get_etf_time_series_execution(self, symbol: str) -> Dict[str, Any]:
        """
        Get ETF time series execution data (ka40007).

        Args:
            symbol: ETF symbol

        Returns:
            Dictionary containing ETF time series execution data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/etf", "ka40007", data)
        return response

    def get_etf_daily_execution(self, symbol: str) -> Dict[str, Any]:
        """
        Get ETF daily execution data (ka40008).

        Args:
            symbol: ETF symbol

        Returns:
            Dictionary containing ETF daily execution data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/etf", "ka40008", data)
        return response

    def get_etf_time_execution_details(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get ETF time-based execution details (ka40009).

        Args:
            symbol: ETF symbol

        Returns:
            List of ETF execution details
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/etf", "ka40009", data)
        return response.get("etfnavarray", [])

    def get_etf_time_trend_analysis(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get ETF time trend analysis (ka40010).

        Args:
            symbol: ETF symbol

        Returns:
            List of ETF time trend analysis data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/etf", "ka40010", data)
        return response.get("etftisl_trnsn", [])

    # ELW Methods

    def get_elw_info(self, symbol: str) -> ELWData:
        """
        Get ELW (Equity Linked Warrant) detailed information.

        Args:
            symbol: ELW symbol

        Returns:
            ELWData object with ELW-specific information
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/elw", "ka30012", data)

        return ELWData(
            symbol=symbol,
            underlying_asset=response.get("bsis_aset_1"),
            strike_price=response.get("elwexec_pric"),
            expiry_date=response.get("expr_dt"),
            conversion_ratio=response.get("elwcnvt_rt"),
            delta=response.get("delta"),
            gamma=response.get("gam"),
            theta=response.get("theta"),
            vega=response.get("vega"),
        )

    def get_elw_sensitivity(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get ELW sensitivity indicators (Greeks).

        Args:
            symbol: ELW symbol

        Returns:
            List of sensitivity data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/elw", "ka10050", data)
        return response.get("elwsnst_ix_array", [])

    def get_elw_daily_sensitivity(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get ELW daily sensitivity indicators (ka10048).

        Args:
            symbol: ELW symbol

        Returns:
            List of daily sensitivity data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/elw", "ka10048", data)
        return response.get("elwdaly_snst_ix", [])

    def get_elw_price_movement_ranking(
        self,
        movement_type: str = "1",  # 1:급등, 2:급락
        time_type: str = "2",     # 1:분전, 2:일전  
        time_period: str = "1",   # 분 혹은 일입력 (예 1, 3, 5)
        volume_filter: str = "0", # 0:전체, 10:만주이상, 50:5만주이상, etc.
        issuer_code: str = "000000000000",     # 전체:000000000000, 한국투자증권:3, etc.
        underlying_asset_code: str = "000000000000", # 전체:000000000000, KOSPI200:201, etc.
        right_type: str = "000",  # 000:전체, 001:콜, 002:풋, etc.
        lp_code: str = "000000000000",         # LP코드
        exclude_trading_end: str = "0"         # 0:포함, 1:제외
    ) -> Dict[str, Any]:
        """
        Get ELW price movement ranking (ka30001).

        Args:
            movement_type: 1:급등, 2:급락
            time_type: 1:분전, 2:일전
            time_period: 분 혹은 일입력 (예 1, 3, 5)
            volume_filter: 거래량구분 (0:전체, 10:만주이상, etc.)
            issuer_code: 발행사코드 (전체:000000000000)
            underlying_asset_code: 기초자산코드 (전체:000000000000)
            right_type: 권리구분 (000:전체, 001:콜, 002:풋, etc.)
            lp_code: LP코드
            exclude_trading_end: 거래종료ELW제외 (0:포함, 1:제외)

        Returns:
            Dictionary containing ELW price movement ranking data
        """
        data = {
            "flu_tp": movement_type,
            "tm_tp": time_type,
            "tm": time_period,
            "trde_qty_tp": volume_filter,
            "isscomp_cd": issuer_code,
            "bsis_aset_cd": underlying_asset_code,
            "rght_tp": right_type,
            "lpcd": lp_code,
            "trde_end_elwskip": exclude_trading_end
        }
        response = self._make_request("/api/dostk/elw", "ka30001", data)
        return response

    def get_elw_trader_net_trading_ranking(
        self,
        issuer_code: str = "003",    # 발행사코드 (3자리)
        volume_filter: str = "0",    # 거래량구분 (0:전체, 5:5천주, 10:만주, etc.)
        trading_type: str = "1",     # 매매구분 (1:순매수, 2:순매도)
        period: str = "60",          # 기간 (1:전일, 5:5일, 10:10일, 40:40일, 60:60일)
        exclude_trading_end: str = "0"  # 거래종료ELW제외 (0:포함, 1:제외)
    ) -> List[Dict[str, Any]]:
        """
        Get trader-wise ELW net trading ranking (ka30002).

        Args:
            issuer_code: 발행사코드 (3자리, 영웅문4 0273화면참조)
            volume_filter: 거래량구분 (0:전체, 5:5천주, 10:만주, etc.)
            trading_type: 매매구분 (1:순매수, 2:순매도)
            period: 기간 (1:전일, 5:5일, 10:10일, 40:40일, 60:60일)
            exclude_trading_end: 거래종료ELW제외 (0:포함, 1:제외)

        Returns:
            List of trader net trading data
        """
        data = {
            "isscomp_cd": issuer_code,
            "trde_qty_tp": volume_filter,
            "trde_tp": trading_type,
            "dt": period,
            "trde_end_elwskip": exclude_trading_end
        }
        response = self._make_request("/api/dostk/elw", "ka30002", data)
        return response.get("trde_ori_elwnettrde_upper", [])

    def get_elw_lp_holdings_daily_trend(
        self,
        underlying_asset_code: str,  # 기초자산코드
        base_date: str               # 기준일자 (YYYYMMDD)
    ) -> List[Dict[str, Any]]:
        """
        Get ELW LP holdings daily trend (ka30003).

        Args:
            underlying_asset_code: 기초자산코드
            base_date: 기준일자 (YYYYMMDD)

        Returns:
            List of LP holdings daily trend data
        """
        data = {
            "bsis_aset_cd": underlying_asset_code,
            "base_dt": base_date
        }
        response = self._make_request("/api/dostk/elw", "ka30003", data)
        return response.get("elwlpposs_daly_trnsn", [])

    def get_elw_divergence_rate(
        self,
        issuer_code: str = "000000000000",      # 발행사코드
        underlying_asset_code: str = "000000000000", # 기초자산코드
        right_type: str = "000",                # 권리구분
        lp_code: str = "000000000000",          # LP코드
        exclude_trading_end: str = "0"          # 거래종료ELW제외
    ) -> List[Dict[str, Any]]:
        """
        Get ELW divergence rate (ka30004).

        Args:
            issuer_code: 발행사코드 (전체:000000000000)
            underlying_asset_code: 기초자산코드 (전체:000000000000)
            right_type: 권리구분 (000:전체, 001:콜, 002:풋, etc.)
            lp_code: LP코드 (전체:000000000000)
            exclude_trading_end: 거래종료ELW제외 (1:제외, 0:포함)

        Returns:
            List of ELW divergence rate data
        """
        data = {
            "isscomp_cd": issuer_code,
            "bsis_aset_cd": underlying_asset_code,
            "rght_tp": right_type,
            "lpcd": lp_code,
            "trde_end_elwskip": exclude_trading_end
        }
        response = self._make_request("/api/dostk/elw", "ka30004", data)
        return response.get("elwdispty_rt", [])

    def get_elw_condition_search(
        self,
        issuer_code: str = "000000000017",      # 발행사코드 (12자리)
        underlying_asset_code: str = "201",     # 기초자산코드
        right_type: str = "1",                  # 권리구분 (0:전체, 1:콜, 2:풋, etc.)
        lp_code: str = "000000000000",          # LP코드 (12자리)
        sort_type: str = "0"                    # 정렬구분 (0:정렬없음, 1:상승율순, etc.)
    ) -> List[Dict[str, Any]]:
        """
        Get ELW condition search results (ka30005).

        Args:
            issuer_code: 발행사코드 (12자리)
            underlying_asset_code: 기초자산코드
            right_type: 권리구분 (0:전체, 1:콜, 2:풋, etc.)
            lp_code: LP코드 (12자리)
            sort_type: 정렬구분 (0:정렬없음, 1:상승율순, etc.)

        Returns:
            List of ELW condition search results
        """
        data = {
            "isscomp_cd": issuer_code,
            "bsis_aset_cd": underlying_asset_code,
            "rght_tp": right_type,
            "lpcd": lp_code,
            "sort_tp": sort_type
        }
        response = self._make_request("/api/dostk/elw", "ka30005", data)
        return response.get("elwcnd_qry", [])

    def get_elw_fluctuation_rate_ranking(
        self,
        sort_type: str = "1",           # 정렬구분 (1:상승률, 2:상승폭, 3:하락률, 4:하락폭)
        right_type: str = "000",        # 권리구분 (000:전체, 001:콜, 002:풋, etc.)
        exclude_trading_end: str = "0"  # 거래종료제외 (0:거래종료포함, 1:거래종료제외)
    ) -> List[Dict[str, Any]]:
        """
        Get ELW fluctuation rate ranking (ka30009).

        Args:
            sort_type: 정렬구분 (1:상승률, 2:상승폭, 3:하락률, 4:하락폭)
            right_type: 권리구분 (000:전체, 001:콜, 002:풋, etc.)
            exclude_trading_end: 거래종료제외 (0:거래종료포함, 1:거래종료제외)

        Returns:
            List of ELW fluctuation rate ranking data
        """
        data = {
            "sort_tp": sort_type,
            "rght_tp": right_type,
            "trde_end_skip": exclude_trading_end
        }
        response = self._make_request("/api/dostk/elw", "ka30009", data)
        return response.get("elwflu_rt_rank", [])

    def get_elw_remaining_quantity_ranking(
        self,
        sort_type: str = "1",           # 정렬구분 (1:순매수잔량상위, 2:순매도잔량상위)
        right_type: str = "000",        # 권리구분 (000:전체, 001:콜, 002:풋, etc.)
        exclude_trading_end: str = "1"  # 거래종료제외 (1:거래종료제외, 0:거래종료포함)
    ) -> List[Dict[str, Any]]:
        """
        Get ELW remaining quantity ranking (ka30010).

        Args:
            sort_type: 정렬구분 (1:순매수잔량상위, 2:순매도잔량상위)
            right_type: 권리구분 (000:전체, 001:콜, 002:풋, etc.)
            exclude_trading_end: 거래종료제외 (1:거래종료제외, 0:거래종료포함)

        Returns:
            List of ELW remaining quantity ranking data
        """
        data = {
            "sort_tp": sort_type,
            "rght_tp": right_type,
            "trde_end_skip": exclude_trading_end
        }
        response = self._make_request("/api/dostk/elw", "ka30010", data)
        return response.get("elwreq_rank", [])

    def get_elw_proximity_rate(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get ELW proximity rate (ka30011).

        Args:
            symbol: ELW symbol

        Returns:
            List of proximity rate data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/elw", "ka30011", data)
        return response.get("elwalacc_rt", [])

    # Market Data Methods (시세)

    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get stock quote/order book data (ka10004).

        Args:
            symbol: Stock symbol (with exchange suffix if needed)

        Returns:
            Dictionary containing detailed order book data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10004", data)
        return response

    def get_stock_ohlcv(
        self,
        symbol: str,
        time_type: str = "D",  # D:일, W:주, M:월, T:분
        count: int = 120,      # 조회개수
        start_date: str = "",  # 시작일자 (YYYYMMDD)
        end_date: str = ""     # 종료일자 (YYYYMMDD)
    ) -> List[Dict[str, Any]]:
        """
        Get stock OHLCV data for daily/weekly/monthly/minute timeframes (ka10005).

        Args:
            symbol: Stock symbol
            time_type: Time type (D:일, W:주, M:월, T:분)
            count: Number of data points to retrieve
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)

        Returns:
            List of OHLCV data
        """
        data = {
            "stk_cd": symbol,
            "perd_tp": time_type,
            "inqry_cnt": str(count),
            "strt_dt": start_date,
            "end_dt": end_date
        }
        response = self._make_request("/api/dostk/mrkcond", "ka10005", data)
        return response.get("chart_data", [])

    def get_stock_minute_data(
        self,
        symbol: str,
        minute_type: str = "1"  # 1:1분, 3:3분, 5:5분, 10:10분, 15:15분, 30:30분, 60:60분
    ) -> List[Dict[str, Any]]:
        """
        Get stock minute-by-minute data (ka10006).

        Args:
            symbol: Stock symbol
            minute_type: Minute interval (1, 3, 5, 10, 15, 30, 60)

        Returns:
            List of minute data
        """
        data = {
            "stk_cd": symbol,
            "min_tp": minute_type
        }
        response = self._make_request("/api/dostk/mrkcond", "ka10006", data)
        return response.get("minute_data", [])

    def get_market_performance_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get market performance information (ka10007).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing market performance data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10007", data)
        return response

    def get_new_shares_rights_all_market_data(self) -> List[Dict[str, Any]]:
        """
        Get all new shares rights market data (ka10011).

        Returns:
            List of new shares rights market data
        """
        data = {}
        response = self._make_request("/api/dostk/mrkcond", "ka10011", data)
        return response.get("new_shares_data", [])

    def get_daily_institutional_trading_stocks(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get daily institutional trading stocks data (ka10044).

        Args:
            symbol: Stock symbol

        Returns:
            List of daily institutional trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10044", data)
        return response.get("institutional_data", [])

    def get_institutional_trading_trends(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get institutional trading trends by stock (ka10045).

        Args:
            symbol: Stock symbol

        Returns:
            List of institutional trading trends
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10045", data)
        return response.get("institutional_trends", [])

    def get_trading_intensity_hourly(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get trading intensity trends hourly (ka10046).

        Args:
            symbol: Stock symbol

        Returns:
            List of hourly trading intensity data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10046", data)
        return response.get("intensity_hourly", [])

    def get_trading_intensity_daily(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get trading intensity trends daily (ka10047).

        Args:
            symbol: Stock symbol

        Returns:
            List of daily trading intensity data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10047", data)
        return response.get("intensity_daily", [])

    def get_intraday_investor_trading(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get intraday investor trading data (ka10063).

        Args:
            symbol: Stock symbol

        Returns:
            List of intraday investor trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10063", data)
        return response.get("intraday_investor", [])

    def get_after_hours_investor_trading(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get after hours investor trading data (ka10066).

        Args:
            symbol: Stock symbol

        Returns:
            List of after hours investor trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10066", data)
        return response.get("after_hours_investor", [])

    def get_securities_firm_trading_trends(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get securities firm trading trends by stock (ka10078).

        Args:
            symbol: Stock symbol

        Returns:
            List of securities firm trading trends
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10078", data)
        return response.get("firm_trends", [])

    def get_daily_stock_prices(
        self, symbol: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get daily stock prices (ka10086).

        Args:
            symbol: Stock symbol
            days: Number of days to retrieve

        Returns:
            List of daily stock price data
        """
        data = {
            "stk_cd": symbol,
            "inqry_cnt": str(days)
        }
        response = self._make_request("/api/dostk/mrkcond", "ka10086", data)
        return response.get("daily_prices", [])

    def get_after_hours_single_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get after hours single price data (ka10087).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing after hours single price data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10087", data)
        return response

    def get_program_trading_hourly(self) -> List[Dict[str, Any]]:
        """
        Get program trading trends hourly (ka90005).

        Returns:
            List of hourly program trading data
        """
        data = {}
        response = self._make_request("/api/dostk/mrkcond", "ka90005", data)
        return response.get("program_hourly", [])

    def get_program_trading_arbitrage(self) -> List[Dict[str, Any]]:
        """
        Get program trading arbitrage balance trends (ka90006).

        Returns:
            List of program trading arbitrage data
        """
        data = {}
        response = self._make_request("/api/dostk/mrkcond", "ka90006", data)
        return response.get("program_arbitrage", [])

    def get_program_trading_cumulative(self) -> List[Dict[str, Any]]:
        """
        Get program trading cumulative trends (ka90007).

        Returns:
            List of cumulative program trading data
        """
        data = {}
        response = self._make_request("/api/dostk/mrkcond", "ka90007", data)
        return response.get("program_cumulative", [])

    def get_symbol_program_trading_hourly(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get stock hourly program trading trends (ka90008).

        Args:
            symbol: Stock symbol

        Returns:
            List of stock hourly program trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka90008", data)
        return response.get("symbol_program_hourly", [])

    def get_program_trading_daily(self) -> List[Dict[str, Any]]:
        """
        Get program trading trends daily (ka90010).

        Returns:
            List of daily program trading data
        """
        data = {}
        response = self._make_request("/api/dostk/mrkcond", "ka90010", data)
        return response.get("program_daily", [])

    def get_symbol_program_trading_daily(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get stock daily program trading trends (ka90013).

        Args:
            symbol: Stock symbol

        Returns:
            List of stock daily program trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka90013", data)
        return response.get("symbol_program_daily", [])

    # Ranking Information Methods (순위정보)

    def get_order_book_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:순매수잔량순, 2:순매도잔량순, 3:매수비율순, 4:매도비율순
        volume_type: str = "0000",    # 0000:장시작전, 0010:만주이상, 0050:5만주이상, 00100:10만주이상
        stock_condition: str = "0",   # 0:전체조회, 1:관리종목제외, 5:증100제외, 6:증100만보기, etc.
        credit_condition: str = "0",  # 0:전체조회, 1:신용융자A군, 2:신용융자B군, etc.
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get order book ranking data (ka10020).

        Args:
            market_type: Market type (001:코스피, 101:코스닥)
            sort_type: Sort type (1:순매수잔량순, 2:순매도잔량순, 3:매수비율순, 4:매도비율순)
            volume_type: Volume filter (0000:장시작전, 0010:만주이상, etc.)
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type (1:KRX, 2:NXT, 3:통합)

        Returns:
            List of order book ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10020", data)
        return response.get("bid_req_upper", [])

    def get_order_book_surge_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:매수잔량급증, 2:매도잔량급증
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get order book surge ranking data (ka10021).

        Args:
            market_type: Market type (001:코스피, 101:코스닥)
            sort_type: Sort type (1:매수잔량급증, 2:매도잔량급증)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of order book surge ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10021", data)
        return response.get("bid_req_spik", [])

    def get_remaining_volume_rate_surge_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:매수잔량율급증, 2:매도잔량율급증
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get remaining volume rate surge ranking data (ka10022).

        Args:
            market_type: Market type
            sort_type: Sort type (1:매수잔량율급증, 2:매도잔량율급증)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of remaining volume rate surge data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10022", data)
        return response.get("req_rt_spik", [])

    def get_volume_surge_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:거래량급증
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get volume surge ranking data (ka10023).

        Args:
            market_type: Market type
            sort_type: Sort type
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of volume surge ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10023", data)
        return response.get("trde_qty_spik", [])

    def get_change_rate_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:상승률, 2:하락률
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get daily change rate ranking data (ka10027).

        Args:
            market_type: Market type
            sort_type: Sort type (1:상승률, 2:하락률)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of change rate ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10027", data)
        return response.get("pred_pre_eltrt_upper", [])

    def get_expected_execution_change_rate_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:상승률, 2:하락률
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get expected execution change rate ranking data (ka10029).

        Args:
            market_type: Market type
            sort_type: Sort type (1:상승률, 2:하락률)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of expected execution change rate ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10029", data)
        return response.get("expct_cheby_eltrt_upper", [])

    def get_current_day_volume_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:거래량상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get current day volume ranking data (ka10030).

        Args:
            market_type: Market type
            sort_type: Sort type
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of current day volume ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10030", data)
        return response.get("today_trde_qty_upper", [])

    def get_previous_day_volume_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:거래량상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get previous day volume ranking data (ka10031).

        Args:
            market_type: Market type
            sort_type: Sort type
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of previous day volume ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10031", data)
        return response.get("pred_trde_qty_upper", [])

    def get_trading_value_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:거래대금상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get trading value ranking data (ka10032).

        Args:
            market_type: Market type
            sort_type: Sort type
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of trading value ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10032", data)
        return response.get("trde_damt_upper", [])

    def get_credit_ratio_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:신용비율상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get credit ratio ranking data (ka10033).

        Args:
            market_type: Market type
            sort_type: Sort type
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of credit ratio ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10033", data)
        return response.get("crd_rt_upper", [])

    def get_foreign_period_trading_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:순매수상위, 2:순매도상위
        period_type: str = "1",       # 1:1일, 3:3일, 5:5일, 10:10일, 20:20일
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get foreign period trading ranking data (ka10034).

        Args:
            market_type: Market type
            sort_type: Sort type (1:순매수상위, 2:순매도상위)
            period_type: Period type (1:1일, 3:3일, 5:5일, 10:10일, 20:20일)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of foreign period trading ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "perd_tp": period_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10034", data)
        return response.get("frg_perd_trde_upper", [])

    def get_foreign_consecutive_trading_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:순매수연속상위, 2:순매도연속상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get foreign consecutive trading ranking data (ka10035).

        Args:
            market_type: Market type
            sort_type: Sort type (1:순매수연속상위, 2:순매도연속상위)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of foreign consecutive trading ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10035", data)
        return response.get("frg_consec_nettrde_upper", [])

    def get_foreign_limit_exhaustion_increase_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:한도소진율증가상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get foreign limit exhaustion rate increase ranking data (ka10036).

        Args:
            market_type: Market type
            sort_type: Sort type
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of foreign limit exhaustion ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10036", data)
        return response.get("frg_lmt_exhst_rt_incrs_upper", [])

    def get_foreign_window_trading_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:순매수상위, 2:순매도상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get foreign window trading ranking data (ka10037).

        Args:
            market_type: Market type
            sort_type: Sort type (1:순매수상위, 2:순매도상위)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of foreign window trading ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10037", data)
        return response.get("frg_wnd_trde_upper", [])

    def get_stock_securities_firm_ranking(
        self,
        symbol: str,              # 종목코드
        sort_type: str = "1",     # 1:순매수상위, 2:순매도상위
        exchange_type: str = "1"  # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get stock securities firm ranking data (ka10038).

        Args:
            symbol: Stock symbol
            sort_type: Sort type (1:순매수상위, 2:순매도상위)
            exchange_type: Exchange type

        Returns:
            List of stock securities firm ranking data
        """
        data = {
            "stk_cd": symbol,
            "sort_tp": sort_type,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10038", data)
        return response.get("stk_scrt_firm_rnk", [])

    def get_securities_firm_trading_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:순매수상위, 2:순매도상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get securities firm trading ranking data (ka10039).

        Args:
            market_type: Market type
            sort_type: Sort type (1:순매수상위, 2:순매도상위)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of securities firm trading ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10039", data)
        return response.get("scrt_firm_trde_upper", [])

    def get_current_day_major_traders(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:순매수상위, 2:순매도상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get current day major traders data (ka10040).

        Args:
            market_type: Market type
            sort_type: Sort type (1:순매수상위, 2:순매도상위)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of current day major traders data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10040", data)
        return response.get("today_mjr_trder", [])

    def get_net_buy_trader_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:순매수상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get net buy trader ranking data (ka10042).

        Args:
            market_type: Market type
            sort_type: Sort type
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of net buy trader ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10042", data)
        return response.get("netbuy_trder_rnk", [])

    def get_current_day_top_dropout(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:상위이탈
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get current day top dropout data (ka10053).

        Args:
            market_type: Market type
            sort_type: Sort type
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of current day top dropout data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10053", data)
        return response.get("today_upper_dropout", [])

    def get_same_period_net_trading_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:순매수상위, 2:순매도상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get same period net trading ranking data (ka10062).

        Args:
            market_type: Market type
            sort_type: Sort type (1:순매수상위, 2:순매도상위)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of same period net trading ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10062", data)
        return response.get("same_perd_nettrde_rnk", [])

    def get_intraday_investor_trading_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:순매수상위, 2:순매도상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get intraday investor trading ranking data (ka10065).

        Args:
            market_type: Market type
            sort_type: Sort type (1:순매수상위, 2:순매도상위)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of intraday investor trading ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10065", data)
        return response.get("intrady_invstr_trde_upper", [])

    def get_after_hours_single_price_change_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:상승률상위, 2:하락률상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get after hours single price change ranking data (ka10098).

        Args:
            market_type: Market type
            sort_type: Sort type (1:상승률상위, 2:하락률상위)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of after hours single price change ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka10098", data)
        return response.get("ovtm_sngl_prc_eltrt_rnk", [])

    def get_foreign_institutional_trading_ranking(
        self,
        market_type: str = "001",     # 001:코스피, 101:코스닥
        sort_type: str = "1",         # 1:순매수상위, 2:순매도상위
        volume_type: str = "0000",    # 거래량구분
        stock_condition: str = "0",   # 종목조건
        credit_condition: str = "0",  # 신용조건
        exchange_type: str = "1"      # 거래소구분
    ) -> List[Dict[str, Any]]:
        """
        Get foreign institutional trading ranking data (ka90009).

        Args:
            market_type: Market type
            sort_type: Sort type (1:순매수상위, 2:순매도상위)
            volume_type: Volume filter
            stock_condition: Stock condition filter
            credit_condition: Credit condition filter
            exchange_type: Exchange type

        Returns:
            List of foreign institutional trading ranking data
        """
        data = {
            "mrkt_tp": market_type,
            "sort_tp": sort_type,
            "trde_qty_tp": volume_type,
            "stk_cnd": stock_condition,
            "crd_cnd": credit_condition,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/rkinfo", "ka90009", data)
        return response.get("frg_instit_trde_upper", [])

    # ===========================================
    # TRADING/ORDER METHODS
    # ===========================================

    def buy_stock(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "3",  # 3=market, 0=limit
        market: str = "KRX",
        condition_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Place a stock buy order (주식 매수주문).
        
        Args:
            symbol: Stock symbol (6 digits)
            quantity: Order quantity
            price: Order price (None for market orders)
            order_type: Trading type (0=limit, 3=market, 5=conditional, etc.)
            market: Exchange type (KRX, NXT, SOR)
            condition_price: Conditional price for conditional orders
            
        Returns:
            Order response with order number
        """
        return self._make_request(
            "/api/dostk/ordr",
            "kt10000",
            {
                "dmst_stex_tp": market,
                "stk_cd": symbol,
                "ord_qty": str(quantity),
                "ord_uv": str(int(price)) if price else "",
                "trde_tp": order_type,
                "cond_uv": str(int(condition_price)) if condition_price else "",
            },
        )
    
    def sell_stock(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "3",  # 3=market, 0=limit
        market: str = "KRX",
        condition_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Place a stock sell order (주식 매도주문).
        
        Args:
            symbol: Stock symbol (6 digits)
            quantity: Order quantity
            price: Order price (None for market orders)
            order_type: Trading type (0=limit, 3=market, 5=conditional, etc.)
            market: Exchange type (KRX, NXT, SOR)
            condition_price: Conditional price for conditional orders
            
        Returns:
            Order response with order number
        """
        return self._make_request(
            "/api/dostk/ordr",
            "kt10001",
            {
                "dmst_stex_tp": market,
                "stk_cd": symbol,
                "ord_qty": str(quantity),
                "ord_uv": str(int(price)) if price else "",
                "trde_tp": order_type,
                "cond_uv": str(int(condition_price)) if condition_price else "",
            },
        )
    
    def modify_order(
        self,
        original_order_number: str,
        symbol: str,
        new_quantity: int,
        new_price: float,
        market: str = "KRX",
        new_condition_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Modify an existing stock order (주식 정정주문).
        
        Args:
            original_order_number: Original order number to modify
            symbol: Stock symbol (6 digits)
            new_quantity: New order quantity
            new_price: New order price
            market: Exchange type (KRX, NXT, SOR)
            new_condition_price: New conditional price if applicable
            
        Returns:
            Modification response with new order number
        """
        return self._make_request(
            "/api/dostk/ordr",
            "kt10002",
            {
                "dmst_stex_tp": market,
                "orig_ord_no": original_order_number,
                "stk_cd": symbol,
                "mdfy_qty": str(new_quantity),
                "mdfy_uv": str(int(new_price)),
                "mdfy_cond_uv": str(int(new_condition_price)) if new_condition_price else "",
            },
        )
    
    def cancel_order(
        self,
        original_order_number: str,
        symbol: str,
        cancel_quantity: int,
        market: str = "KRX",
    ) -> Dict[str, Any]:
        """
        Cancel an existing stock order (주식 취소주문).
        
        Args:
            original_order_number: Original order number to cancel
            symbol: Stock symbol (6 digits)
            cancel_quantity: Quantity to cancel (0 = cancel all remaining)
            market: Exchange type (KRX, NXT, SOR)
            
        Returns:
            Cancellation response with new order number
        """
        return self._make_request(
            "/api/dostk/ordr",
            "kt10003",
            {
                "dmst_stex_tp": market,
                "orig_ord_no": original_order_number,
                "stk_cd": symbol,
                "cncl_qty": str(cancel_quantity),
            },
        )
    
    def credit_buy_stock(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "3",  # 3=market, 0=limit
        market: str = "KRX",
        condition_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Place a credit buy order (신용 매수주문).
        
        Args:
            symbol: Stock symbol (6 digits)
            quantity: Order quantity
            price: Order price (None for market orders)
            order_type: Trading type (0=limit, 3=market, 5=conditional, etc.)
            market: Exchange type (KRX, NXT, SOR)
            condition_price: Conditional price for conditional orders
            
        Returns:
            Order response with order number
        """
        return self._make_request(
            "/api/dostk/crdordr",
            "kt10006",
            {
                "dmst_stex_tp": market,
                "stk_cd": symbol,
                "ord_qty": str(quantity),
                "ord_uv": str(int(price)) if price else "",
                "trde_tp": order_type,
                "cond_uv": str(int(condition_price)) if condition_price else "",
            },
        )
    
    def credit_sell_stock(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "3",  # 3=market, 0=limit
        market: str = "KRX",
        credit_deal_type: str = "99",  # 33=margin, 99=margin combined
        credit_loan_date: Optional[str] = None,  # YYYYMMDD (required for margin=33)
        condition_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Place a credit sell order (신용 매도주문).
        
        Args:
            symbol: Stock symbol (6 digits)
            quantity: Order quantity
            price: Order price (None for market orders)
            order_type: Trading type (0=limit, 3=market, 5=conditional, etc.)
            market: Exchange type (KRX, NXT, SOR)
            credit_deal_type: Credit deal type (33=margin, 99=margin combined)
            credit_loan_date: Loan date in YYYYMMDD format (required for margin=33)
            condition_price: Conditional price for conditional orders
            
        Returns:
            Order response with order number
        """
        return self._make_request(
            "/api/dostk/crdordr",
            "kt10007",
            {
                "dmst_stex_tp": market,
                "stk_cd": symbol,
                "ord_qty": str(quantity),
                "ord_uv": str(int(price)) if price else "",
                "trde_tp": order_type,
                "crd_deal_tp": credit_deal_type,
                "crd_loan_dt": credit_loan_date or "",
                "cond_uv": str(int(condition_price)) if condition_price else "",
            },
        )
    
    def credit_modify_order(
        self,
        original_order_number: str,
        symbol: str,
        new_quantity: int,
        new_price: float,
        market: str = "KRX",
        new_condition_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Modify an existing credit order (신용 정정주문).
        
        Args:
            original_order_number: Original order number to modify
            symbol: Stock symbol (6 digits)
            new_quantity: New order quantity
            new_price: New order price
            market: Exchange type (KRX, NXT, SOR)
            new_condition_price: New conditional price if applicable
            
        Returns:
            Modification response with new order number
        """
        return self._make_request(
            "/api/dostk/crdordr",
            "kt10008",
            {
                "dmst_stex_tp": market,
                "orig_ord_no": original_order_number,
                "stk_cd": symbol,
                "mdfy_qty": str(new_quantity),
                "mdfy_uv": str(int(new_price)),
                "mdfy_cond_uv": str(int(new_condition_price)) if new_condition_price else "",
            },
        )
    
    def credit_cancel_order(
        self,
        original_order_number: str,
        symbol: str,
        cancel_quantity: int,
        market: str = "KRX",
    ) -> Dict[str, Any]:
        """
        Cancel an existing credit order (신용 취소주문).
        
        Args:
            original_order_number: Original order number to cancel
            symbol: Stock symbol (6 digits)
            cancel_quantity: Quantity to cancel (0 = cancel all remaining)
            market: Exchange type (KRX, NXT, SOR)
            
        Returns:
            Cancellation response with new order number
        """
        return self._make_request(
            "/api/dostk/crdordr",
            "kt10009",
            {
                "dmst_stex_tp": market,
                "orig_ord_no": original_order_number,
                "stk_cd": symbol,
                "cncl_qty": str(cancel_quantity),
            },
        )

    # ===========================================
    # ACCOUNT MANAGEMENT METHODS
    # ===========================================

    def get_daily_stock_profit_loss(
        self, symbol: str, start_date: str
    ) -> List["RealizedProfitLoss"]:
        """
        Get daily realized profit/loss by stock (ka10072).

        Args:
            symbol: Stock symbol
            start_date: Start date in YYYYMMDD format

        Returns:
            List of RealizedProfitLoss data
        """
        from .models import RealizedProfitLoss

        data = {"stk_cd": symbol, "strt_dt": start_date}
        response = self._make_request("/api/dostk/acnt", "ka10072", data)
        profit_loss_data = response.get("dt_stk_div_rlzt_pl", [])
        return [RealizedProfitLoss(**item) for item in profit_loss_data]

    def get_period_stock_profit_loss(
        self, symbol: str, start_date: str, end_date: str
    ) -> List["RealizedProfitLoss"]:
        """
        Get period realized profit/loss by stock (ka10073).

        Args:
            symbol: Stock symbol
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format

        Returns:
            List of RealizedProfitLoss data
        """
        from .models import RealizedProfitLoss

        data = {"stk_cd": symbol, "strt_dt": start_date, "end_dt": end_date}
        response = self._make_request("/api/dostk/acnt", "ka10073", data)
        profit_loss_data = response.get("dt_stk_rlzt_pl", [])
        return [RealizedProfitLoss(**item) for item in profit_loss_data]

    def get_daily_realized_profit_loss(self, date: str) -> List[Dict[str, Any]]:
        """
        Get daily realized profit/loss (ka10074).

        Args:
            date: Date in YYYYMMDD format

        Returns:
            List of daily profit/loss data
        """
        data = {"dt": date}
        response = self._make_request("/api/dostk/acnt", "ka10074", data)
        return response.get("dt_rlzt_pl", [])

    def get_unfilled_orders(
        self,
        all_stock_type: str = "0",
        trade_type: str = "0",
        symbol: Optional[str] = None,
        exchange_type: str = "0",
    ) -> List["UnfilledOrder"]:
        """
        Get unfilled orders (ka10075).

        Args:
            all_stock_type: All stock type (0:all, 1:specific stock)
            trade_type: Trade type (0:all, 1:sell, 2:buy)
            symbol: Stock symbol (required if all_stock_type="1")
            exchange_type: Exchange type (0:integrated, 1:KRX, 2:NXT)

        Returns:
            List of UnfilledOrder data
        """
        from .models import UnfilledOrder

        data = {
            "all_stk_tp": all_stock_type,
            "trde_tp": trade_type,
            "stex_tp": exchange_type,
        }
        if symbol:
            data["stk_cd"] = symbol

        response = self._make_request("/api/dostk/acnt", "ka10075", data)
        unfilled_data = response.get("oso", [])
        return [UnfilledOrder(**item) for item in unfilled_data]

    def get_filled_orders(
        self,
        symbol: Optional[str] = None,
        query_type: str = "0",
        sell_type: str = "0",
        order_number: Optional[str] = None,
        exchange_type: str = "0",
    ) -> List["FilledOrder"]:
        """
        Get filled orders (ka10076).

        Args:
            symbol: Stock symbol
            query_type: Query type (0:all, 1:specific stock)
            sell_type: Sell type (0:all, 1:sell, 2:buy)
            order_number: Order number (for filtering)
            exchange_type: Exchange type (0:integrated, 1:KRX, 2:NXT)

        Returns:
            List of FilledOrder data
        """
        from .models import FilledOrder

        data = {"qry_tp": query_type, "sell_tp": sell_type, "stex_tp": exchange_type}
        if symbol:
            data["stk_cd"] = symbol
        if order_number:
            data["ord_no"] = order_number

        response = self._make_request("/api/dostk/acnt", "ka10076", data)
        filled_data = response.get("cntr", [])
        return [FilledOrder(**item) for item in filled_data]

    def get_daily_profit_loss_detail(self, date: str) -> Dict[str, Any]:
        """
        Get daily realized profit/loss detail (ka10077).

        Args:
            date: Date in YYYYMMDD format

        Returns:
            Daily profit/loss detail data
        """
        data = {"dt": date}
        response = self._make_request("/api/dostk/acnt", "ka10077", data)
        return response

    def get_account_return_rate(self, period: str = "1") -> Dict[str, Any]:
        """
        Get account return rate (ka10085).

        Args:
            period: Period (1:1month, 3:3months, 6:6months, 12:1year)

        Returns:
            Account return rate data
        """
        data = {"period": period}
        response = self._make_request("/api/dostk/acnt", "ka10085", data)
        return response

    def get_split_order_detail(self, order_number: str) -> Dict[str, Any]:
        """
        Get unfilled split order detail (ka10088).

        Args:
            order_number: Order number

        Returns:
            Split order detail data
        """
        data = {"ord_no": order_number}
        response = self._make_request("/api/dostk/acnt", "ka10088", data)
        return response

    def get_daily_trading_journal(self, date: str) -> List["TradingJournal"]:
        """
        Get daily trading journal (ka10170).

        Args:
            date: Date in YYYYMMDD format

        Returns:
            List of TradingJournal data
        """
        from .models import TradingJournal

        data = {"dt": date}
        response = self._make_request("/api/dostk/acnt", "ka10170", data)
        journal_data = response.get("data", [])
        return [TradingJournal(**item) for item in journal_data]

    def get_deposit_details(self) -> "DepositDetail":
        """
        Get deposit detail status (kt00001).

        Returns:
            DepositDetail data
        """
        from .models import DepositDetail

        response = self._make_request("/api/dostk/acnt", "kt00001", {})
        return DepositDetail(**response)

    def get_daily_estimated_deposit_assets(self, date: str) -> Dict[str, Any]:
        """
        Get daily estimated deposit asset status (kt00002).

        Args:
            date: Date in YYYYMMDD format

        Returns:
            Daily estimated deposit asset data
        """
        data = {"dt": date}
        response = self._make_request("/api/dostk/acnt", "kt00002", data)
        return response

    def get_estimated_assets(self) -> "AssetEvaluation":
        """
        Get estimated asset inquiry (kt00003).

        Returns:
            AssetEvaluation data
        """
        from .models import AssetEvaluation

        response = self._make_request("/api/dostk/acnt", "kt00003", {})
        return AssetEvaluation(**response)

    def get_account_evaluation_status(self) -> Dict[str, Any]:
        """
        Get account evaluation status (kt00004).

        Returns:
            Account evaluation status data
        """
        response = self._make_request("/api/dostk/acnt", "kt00004", {})
        return response

    def get_execution_balance(self) -> List[Position]:
        """
        Get execution balance (kt00005).

        Returns:
            List of Position data
        """
        response = self._make_request("/api/dostk/acnt", "kt00005", {})
        balance_data = response.get("data", [])
        return [Position(**item) for item in balance_data]

    def get_account_order_execution_detail(
        self, order_number: Optional[str] = None, symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get account order execution detail (kt00007).

        Args:
            order_number: Order number
            symbol: Stock symbol

        Returns:
            List of order execution detail data
        """
        data = {}
        if order_number:
            data["ord_no"] = order_number
        if symbol:
            data["stk_cd"] = symbol

        response = self._make_request("/api/dostk/acnt", "kt00007", data)
        return response.get("data", [])

    def get_next_day_settlement_schedule(self) -> List[Dict[str, Any]]:
        """
        Get next day settlement schedule by account (kt00008).

        Returns:
            List of next day settlement data
        """
        response = self._make_request("/api/dostk/acnt", "kt00008", {})
        return response.get("data", [])

    def get_account_order_execution_status(self) -> Dict[str, Any]:
        """
        Get account order execution status (kt00009).

        Returns:
            Order execution status data
        """
        response = self._make_request("/api/dostk/acnt", "kt00009", {})
        return response

    def get_order_withdrawal_available_amount(self) -> Dict[str, Any]:
        """
        Get order withdrawal available amount (kt00010).

        Returns:
            Withdrawal available amount data
        """
        response = self._make_request("/api/dostk/acnt", "kt00010", {})
        return response

    def get_margin_rate_order_quantity(
        self, symbol: str, margin_rate: str
    ) -> Dict[str, Any]:
        """
        Get margin rate order available quantity (kt00011).

        Args:
            symbol: Stock symbol
            margin_rate: Margin rate

        Returns:
            Available quantity data
        """
        data = {"stk_cd": symbol, "margin_rate": margin_rate}
        response = self._make_request("/api/dostk/acnt", "kt00011", data)
        return response

    def get_credit_guarantee_rate_order_quantity(
        self, symbol: str, guarantee_rate: str
    ) -> Dict[str, Any]:
        """
        Get credit guarantee rate order available quantity (kt00012).

        Args:
            symbol: Stock symbol
            guarantee_rate: Guarantee rate

        Returns:
            Available quantity data
        """
        data = {"stk_cd": symbol, "guarantee_rate": guarantee_rate}
        response = self._make_request("/api/dostk/acnt", "kt00012", data)
        return response

    def get_margin_detail_inquiry(self) -> List[Dict[str, Any]]:
        """
        Get margin detail inquiry (kt00013).

        Returns:
            List of margin detail data
        """
        response = self._make_request("/api/dostk/acnt", "kt00013", {})
        return response.get("data", [])

    def get_consignment_comprehensive_transaction_details(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get consignment comprehensive transaction details (kt00015).

        Args:
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format

        Returns:
            List of transaction detail data
        """
        data = {"strt_dt": start_date, "end_dt": end_date}
        response = self._make_request("/api/dostk/acnt", "kt00015", data)
        return response.get("data", [])

    def get_daily_account_return_detail(self, date: str) -> Dict[str, Any]:
        """
        Get daily account return rate detail status (kt00016).

        Args:
            date: Date in YYYYMMDD format

        Returns:
            Daily account return detail data
        """
        data = {"dt": date}
        response = self._make_request("/api/dostk/acnt", "kt00016", data)
        return response

    def get_account_daily_status(self, date: str) -> Dict[str, Any]:
        """
        Get account daily status (kt00017).

        Args:
            date: Date in YYYYMMDD format

        Returns:
            Account daily status data
        """
        data = {"dt": date}
        response = self._make_request("/api/dostk/acnt", "kt00017", data)
        return response

    def get_account_evaluation_balance_detail(self) -> List[Dict[str, Any]]:
        """
        Get account evaluation balance detail (kt00018).

        Returns:
            List of evaluation balance detail data
        """
        response = self._make_request("/api/dostk/acnt", "kt00018", {})
        return response.get("data", [])

    # Stock Information Methods (종목정보)

    def get_stock_basic_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get stock basic information (ka10001).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing basic stock information
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10001", data)
        return response

    def get_stock_traders(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get stock traders information (ka10002).

        Args:
            symbol: Stock symbol

        Returns:
            List of stock traders data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10002", data)
        return response.get("stk_trders", [])

    def get_execution_info(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get execution information (ka10003).

        Args:
            symbol: Stock symbol

        Returns:
            List of execution data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10003", data)
        return response.get("exec_info", [])

    def get_credit_trading_trends(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get credit trading trends (ka10013).

        Args:
            symbol: Stock symbol

        Returns:
            List of credit trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10013", data)
        return response.get("crd_trde_trends", [])

    def get_daily_trading_detail(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get daily trading detail (ka10015).

        Args:
            symbol: Stock symbol

        Returns:
            List of daily trading detail data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10015", data)
        return response.get("daly_trde_detail", [])

    def get_new_low_high_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get new low/high price information (ka10016).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing new low/high price data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10016", data)
        return response

    def get_upper_lower_limit_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get upper/lower limit price information (ka10017).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing upper/lower limit price data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10017", data)
        return response

    def get_high_low_proximity(self, symbol: str) -> Dict[str, Any]:
        """
        Get high/low proximity information (ka10018).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing high/low proximity data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10018", data)
        return response

    def get_price_volatility(self, symbol: str) -> Dict[str, Any]:
        """
        Get price volatility information (ka10019).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing price volatility data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10019", data)
        return response

    def get_volume_renewal(self, symbol: str) -> Dict[str, Any]:
        """
        Get volume renewal information (ka10024).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing volume renewal data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10024", data)
        return response

    def get_order_concentration(self, symbol: str) -> Dict[str, Any]:
        """
        Get order concentration information (ka10025).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing order concentration data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10025", data)
        return response

    def get_high_low_per(self, symbol: str) -> Dict[str, Any]:
        """
        Get high/low PER information (ka10026).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing high/low PER data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10026", data)
        return response

    def get_opening_price_volatility(self, symbol: str) -> Dict[str, Any]:
        """
        Get opening price volatility information (ka10028).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing opening price volatility data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10028", data)
        return response

    def get_trader_order_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get trader order analysis information (ka10043).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing trader order analysis data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10043", data)
        return response

    def get_trader_instant_volume(self, symbol: str) -> Dict[str, Any]:
        """
        Get trader instant volume information (ka10052).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing trader instant volume data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10052", data)
        return response

    def get_volatility_interruption_stocks(self) -> List[Dict[str, Any]]:
        """
        Get volatility interruption triggered stocks (ka10054).

        Returns:
            List of volatility interruption stock data
        """
        data = {}
        response = self._make_request("/api/dostk/stkinfo", "ka10054", data)
        return response.get("vi_stocks", [])

    def get_current_previous_execution_volume(self, symbol: str) -> Dict[str, Any]:
        """
        Get current vs previous execution volume (ka10055).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing current vs previous execution volume data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10055", data)
        return response

    def get_investor_daily_trading_stocks(
        self, date: str, investor_type: str = "1"
    ) -> List[Dict[str, Any]]:
        """
        Get investor daily trading stocks (ka10058).

        Args:
            date: Date in YYYYMMDD format
            investor_type: Investor type (1:개인, 2:외국인, 3:기관)

        Returns:
            List of investor daily trading data
        """
        data = {"dt": date, "invr_tp": investor_type}
        response = self._make_request("/api/dostk/stkinfo", "ka10058", data)
        return response.get("invr_daly_trde", [])

    def get_stock_investor_institution_detail(
        self, symbol: str, date: str
    ) -> List[Dict[str, Any]]:
        """
        Get stock investor institution detail (ka10059).

        Args:
            symbol: Stock symbol
            date: Date in YYYYMMDD format

        Returns:
            List of investor institution detail data
        """
        data = {"stk_cd": symbol, "dt": date}
        response = self._make_request("/api/dostk/stkinfo", "ka10059", data)
        return response.get("invr_inst_detail", [])

    def get_stock_investor_institution_summary(
        self, symbol: str, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """
        Get stock investor institution summary (ka10061).

        Args:
            symbol: Stock symbol
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format

        Returns:
            Dictionary containing investor institution summary data
        """
        data = {"stk_cd": symbol, "strt_dt": start_date, "end_dt": end_date}
        response = self._make_request("/api/dostk/stkinfo", "ka10061", data)
        return response

    def get_current_previous_execution_detail(self, symbol: str) -> Dict[str, Any]:
        """
        Get current vs previous execution detail (ka10084).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing current vs previous execution detail data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10084", data)
        return response

    def get_watchlist_stock_info(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Get watchlist stock information (ka10095).

        Args:
            symbols: List of stock symbols

        Returns:
            List of watchlist stock data
        """
        data = {"stk_cds": ",".join(symbols)}
        response = self._make_request("/api/dostk/stkinfo", "ka10095", data)
        return response.get("wtch_stks", [])

    def get_stock_info_list(
        self, market_type: str = "KRX", page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get stock information list (ka10099).

        Args:
            market_type: Market type (KRX, NXT, SOR)
            page_size: Number of items per page

        Returns:
            List of stock information data
        """
        data = {"mkt_tp": market_type, "page_size": str(page_size)}
        response = self._make_request("/api/dostk/stkinfo", "ka10099", data)
        return response.get("stk_list", [])

    def get_stock_info_detail(self, symbol: str) -> Dict[str, Any]:
        """
        Get detailed stock information (ka10100).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing detailed stock information
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/stkinfo", "ka10100", data)
        return response

    def get_sector_code_list(self) -> List[Dict[str, Any]]:
        """
        Get sector code list (ka10101).

        Returns:
            List of sector code data
        """
        data = {}
        response = self._make_request("/api/dostk/stkinfo", "ka10101", data)
        return response.get("sect_list", [])

    def get_member_firm_list(self) -> List[Dict[str, Any]]:
        """
        Get member firm list (ka10102).

        Returns:
            List of member firm data
        """
        data = {}
        response = self._make_request("/api/dostk/stkinfo", "ka10102", data)
        return response.get("memb_firms", [])

    def get_program_net_buy_top50(self, date: str) -> List[Dict[str, Any]]:
        """
        Get program trading net buy top 50 stocks (ka90003).

        Args:
            date: Date in YYYYMMDD format

        Returns:
            List of program net buy top 50 data
        """
        data = {"dt": date}
        response = self._make_request("/api/dostk/stkinfo", "ka90003", data)
        return response.get("prog_net_buy", [])

    # Note: Removed get_stock_program_trading_status as it was incorrectly using ka90012
    # ka90012 is actually for securities lending details, not program trading

    # Short Selling Methods (공매도)

    def get_short_selling_trend(
        self, 
        symbol: str, 
        time_type: str = "1", 
        start_date: str = "", 
        end_date: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Get short selling trend information (ka10014).

        Args:
            symbol: Stock symbol (거래소별 종목코드)
                   KRX: 039490, NXT: 039490_N, SOR: 039490_AL
            time_type: Time division (시간구분)
                      0: Start date, 1: Period
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format

        Returns:
            List containing short selling trend data
        """
        data = {
            "stk_cd": symbol,
            "tm_tp": time_type,
            "strt_dt": start_date,
            "end_dt": end_date
        }
        response = self._make_request("/api/dostk/shsa", "ka10014", data)
        return response.get("shrts_trnsn", [])

    # Institutional-Foreign Methods (기관-외국인)

    def get_foreign_stock_trading_trend(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get foreign stock trading trend by stock (ka10008).

        Args:
            symbol: Stock symbol (거래소별 종목코드)
                   KRX: 039490, NXT: 039490_NX, SOR: 039490_AL

        Returns:
            List containing foreign trading trend data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/frgnistt", "ka10008", data)
        return response.get("stk_frgnr", [])

    def get_institutional_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get institutional stock information (ka10009).

        Args:
            symbol: Stock symbol (거래소별 종목코드)
                   KRX: 039490, NXT: 039490_NX, SOR: 039490_AL

        Returns:
            Dictionary containing institutional stock information
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/frgnistt", "ka10009", data)
        return response

    def get_institutional_foreign_continuous_trading(
        self,
        period: str = "1",
        start_date: str = "",
        end_date: str = "",
        market_type: str = "001",
        net_sell_type: str = "2",
        stock_sector_type: str = "0",
        amount_quantity_type: str = "0",
        exchange_type: str = "1"
    ) -> List[Dict[str, Any]]:
        """
        Get institutional-foreign continuous trading status (ka10131).

        Args:
            period: Period (기간)
                   1: Recent day, 3: 3 days, 5: 5 days, 10: 10 days,
                   20: 20 days, 120: 120 days, 0: Use start/end dates
            start_date: Start date in YYYYMMDD format (when period=0)
            end_date: End date in YYYYMMDD format (when period=0)
            market_type: Market division (장구분)
                        001: KOSPI, 101: KOSDAQ
            net_sell_type: Net sell/buy division (순매도수구분)
                          2: Net buy (fixed value)
            stock_sector_type: Stock/sector division (종목업종구분)
                              0: Stock, 1: Sector
            amount_quantity_type: Amount/quantity division (금액수량구분)
                                 0: Amount, 1: Quantity
            exchange_type: Exchange division (거래소구분)
                          1: KRX, 2: NXT, 3: Integrated

        Returns:
            List containing institutional-foreign continuous trading data
        """
        data = {
            "dt": period,
            "strt_dt": start_date,
            "end_dt": end_date,
            "mrkt_tp": market_type,
            "netslmt_tp": net_sell_type,
            "stk_inds_tp": stock_sector_type,
            "amt_qty_tp": amount_quantity_type,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/frgnistt", "ka10131", data)
        return response.get("orgn_frgnr_cont_trde_prst", [])

    # Securities Lending Methods (대차거래)

    def get_securities_lending_trend(
        self,
        start_date: str = "",
        end_date: str = "",
        all_type: str = "1"
    ) -> List[Dict[str, Any]]:
        """
        Get securities lending trend information (ka10068).

        Args:
            start_date: Start date in YYYYMMDD format (optional)
            end_date: End date in YYYYMMDD format (optional)
            all_type: All type division (전체구분)
                     1: Show all

        Returns:
            List containing securities lending trend data
        """
        data = {
            "strt_dt": start_date,
            "end_dt": end_date,
            "all_type": all_type
        }
        response = self._make_request("/api/dostk/slb", "ka10068", data)
        return response.get("sec_lend_trend", [])

    def get_securities_lending_top10(self, market_type: str = "1") -> List[Dict[str, Any]]:
        """
        Get top 10 securities lending stocks (ka10069).

        Args:
            market_type: Market type (시장구분)
                        1: KOSPI, 2: KOSDAQ

        Returns:
            List containing top 10 securities lending data
        """
        data = {"mrkt_tp": market_type}
        response = self._make_request("/api/dostk/slb", "ka10069", data)
        return response.get("sec_lend_top10", [])

    def get_securities_lending_balance_top10(self, market_type: str = "1") -> List[Dict[str, Any]]:
        """
        Get top 10 securities lending balance stocks (ka20068).

        Args:
            market_type: Market type (시장구분)
                        1: KOSPI, 2: KOSDAQ

        Returns:
            List containing top 10 securities lending balance data
        """
        data = {"mrkt_tp": market_type}
        response = self._make_request("/api/dostk/slb", "ka20068", data)
        return response.get("sec_lend_bal_top10", [])

    def get_securities_lending_details(
        self, 
        symbol: str, 
        date_type: str = "1",
        start_date: str = "",
        end_date: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Get securities lending details information (ka90012).

        Args:
            symbol: Stock symbol (종목코드)
            date_type: Date type (일자구분)
                      1: Single date, 2: Date range
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format

        Returns:
            List containing securities lending details
        """
        data = {
            "stk_cd": symbol,
            "dt_tp": date_type,
            "strt_dt": start_date,
            "end_dt": end_date
        }
        response = self._make_request("/api/dostk/slb", "ka90012", data)
        return response.get("sec_lend_details", [])

    # Sector Methods (업종)

    def get_sector_program_trading(self, symbol: str) -> Dict[str, Any]:
        """
        Get sector program trading information (ka10010).

        Args:
            symbol: Stock symbol (종목코드)
                   Exchange-specific format (KRX:039490, NXT:039490_NX, SOR:039490_AL)

        Returns:
            Dictionary containing sector program trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/sect", "ka10010", data)
        return response

    def get_sector_investor_net_buying(
        self,
        market_type: str = "0",
        amount_quantity_type: str = "0", 
        base_date: str = "",
        exchange_type: str = "3"
    ) -> List[Dict[str, Any]]:
        """
        Get sector investor net buying information (ka10051).

        Args:
            market_type: Market type (시장구분)
                        0: KOSPI, 1: KOSDAQ
            amount_quantity_type: Amount/Quantity type (금액수량구분)
                                 0: Amount, 1: Quantity
            base_date: Base date in YYYYMMDD format (optional)
            exchange_type: Exchange type (거래소구분)
                          1: KRX, 2: NXT, 3: Integrated

        Returns:
            List containing sector investor net buying data
        """
        data = {
            "mrkt_tp": market_type,
            "amt_qty_tp": amount_quantity_type,
            "base_dt": base_date,
            "stex_tp": exchange_type
        }
        response = self._make_request("/api/dostk/sect", "ka10051", data)
        return response.get("inds_netprps", [])

    def get_sector_current_price(self, sector_code: str) -> Dict[str, Any]:
        """
        Get sector current price information (ka20001).

        Args:
            sector_code: Sector code (업종코드)

        Returns:
            Dictionary containing sector current price data
        """
        data = {"sect_cd": sector_code}
        response = self._make_request("/api/dostk/sect", "ka20001", data)
        return response

    def get_sector_stock_prices(self, sector_code: str) -> List[Dict[str, Any]]:
        """
        Get sector stock prices information (ka20002).

        Args:
            sector_code: Sector code (업종코드)

        Returns:
            List containing sector stock prices data
        """
        data = {"sect_cd": sector_code}
        response = self._make_request("/api/dostk/sect", "ka20002", data)
        return response.get("sect_stk_prices", [])

    def get_all_sector_indices(self, market_type: str = "0") -> List[Dict[str, Any]]:
        """
        Get all sector indices information (ka20003).

        Args:
            market_type: Market type (시장구분)
                        0: KOSPI, 1: KOSDAQ

        Returns:
            List containing all sector indices data
        """
        data = {"mrkt_tp": market_type}
        response = self._make_request("/api/dostk/sect", "ka20003", data)
        return response.get("all_sect_indices", [])

    def get_sector_daily_current_price(
        self, 
        sector_code: str,
        period_type: str = "1"
    ) -> List[Dict[str, Any]]:
        """
        Get sector daily current price information (ka20009).

        Args:
            sector_code: Sector code (업종코드)
            period_type: Period type (기간구분)
                        1: Daily, 2: Weekly, 3: Monthly

        Returns:
            List containing sector daily current price data
        """
        data = {
            "sect_cd": sector_code,
            "period_tp": period_type
        }
        response = self._make_request("/api/dostk/sect", "ka20009", data)
        return response.get("sect_daily_prices", [])

    # ==========================================
    # Chart Data Methods (차트.md)
    # ==========================================

    def get_stock_investor_institution_chart(
        self,
        date: str,
        symbol: str,
        amount_quantity_type: str = "1",  # 1:금액, 2:수량
        trade_type: str = "0",            # 0:순매수, 1:매수, 2:매도
        unit_type: str = "1000"           # 1000:천주, 1:단주
    ) -> List[Dict[str, Any]]:
        """
        Get stock investor institution chart data (ka10060).
        종목별투자자기관별차트요청
        
        Args:
            date: 일자 (YYYYMMDD)
            symbol: 종목코드 (KRX:005930, NXT:005930_NX, SOR:005930_AL)
            amount_quantity_type: 금액수량구분 (1:금액, 2:수량)
            trade_type: 매매구분 (0:순매수, 1:매수, 2:매도)
            unit_type: 단위구분 (1000:천주, 1:단주)
            
        Returns:
            List of investor institution chart data
        """
        data = {
            "dt": date,
            "stk_cd": symbol,
            "amt_qty_tp": amount_quantity_type,
            "trde_tp": trade_type,
            "unit_tp": unit_type
        }
        response = self._make_request("/api/dostk/chart", "ka10060", data)
        return response.get("stk_invsr_orgn_chart", [])

    def get_intraday_investor_trading_chart(
        self,
        market_type: str = "000",    # 000:전체, 001:코스피, 101:코스닥
        amount_quantity_type: str = "1",  # 1:금액, 2:수량
        trade_type: str = "0",       # 0:순매수, 1:매수, 2:매도
        symbol: str = "005930"       # 종목코드
    ) -> List[Dict[str, Any]]:
        """
        Get intraday investor trading chart data (ka10064).
        장중투자자별매매차트요청
        
        Args:
            market_type: 시장구분 (000:전체, 001:코스피, 101:코스닥)
            amount_quantity_type: 금액수량구분 (1:금액, 2:수량)
            trade_type: 매매구분 (0:순매수, 1:매수, 2:매도)
            symbol: 종목코드
            
        Returns:
            List of intraday investor trading chart data
        """
        data = {
            "mrkt_tp": market_type,
            "amt_qty_tp": amount_quantity_type,
            "trde_tp": trade_type,
            "stk_cd": symbol
        }
        response = self._make_request("/api/dostk/chart", "ka10064", data)
        return response.get("opmr_invsr_trde_chart", [])

    def get_stock_tick_chart(
        self,
        symbol: str,
        tick_scope: str = "1",       # 틱범위 (1:전체)
        adjusted_price_type: str = "1"  # 수정주가구분 (1:수정주가)
    ) -> Dict[str, Any]:
        """
        Get stock tick chart data (ka10079).
        주식틱차트조회요청
        
        Args:
            symbol: 종목코드
            tick_scope: 틱범위 (1:전체)
            adjusted_price_type: 수정주가구분 (1:수정주가)
            
        Returns:
            Dictionary containing tick chart data with symbol and tick data list
        """
        data = {
            "stk_cd": symbol,
            "tic_scope": tick_scope,
            "upd_stkpc_tp": adjusted_price_type
        }
        response = self._make_request("/api/dostk/chart", "ka10079", data)
        return {
            "stk_cd": response.get("stk_cd", symbol),
            "last_tic_cnt": response.get("last_tic_cnt", ""),
            "stk_tic_chart_qry": response.get("stk_tic_chart_qry", [])
        }

    def get_stock_minute_chart(
        self,
        symbol: str,
        minute_type: str = "1",      # 분구분 (1:1분, 3:3분, 5:5분, 10:10분, 15:15분, 30:30분, 60:60분)
        adjusted_price_type: str = "1"  # 수정주가구분 (1:수정주가)
    ) -> Dict[str, Any]:
        """
        Get stock minute chart data (ka10080).
        주식분봉차트조회요청
        
        Args:
            symbol: 종목코드
            minute_type: 분구분 (1:1분, 3:3분, 5:5분, 10:10분, 15:15분, 30:30분, 60:60분)
            adjusted_price_type: 수정주가구분 (1:수정주가)
            
        Returns:
            Dictionary containing minute chart data with symbol and minute data list
        """
        data = {
            "stk_cd": symbol,
            "min_tp": minute_type,
            "upd_stkpc_tp": adjusted_price_type
        }
        response = self._make_request("/api/dostk/chart", "ka10080", data)
        return {
            "stk_cd": response.get("stk_cd", symbol),
            "stk_min_pole_chart_qry": response.get("stk_min_pole_chart_qry", [])
        }

    def get_stock_daily_chart(
        self,
        symbol: str,
        base_date: str = "",        # 기준일자 (YYYYMMDD, 공백시 당일)
        adjusted_price_type: str = "1"  # 수정주가구분 (1:수정주가)
    ) -> Dict[str, Any]:
        """
        Get stock daily chart data (ka10081).
        주식일봉차트조회요청
        
        Args:
            symbol: 종목코드
            base_date: 기준일자 (YYYYMMDD, 공백시 당일)
            adjusted_price_type: 수정주가구분 (1:수정주가)
            
        Returns:
            Dictionary containing daily chart data with symbol and daily data list
        """
        data = {
            "stk_cd": symbol,
            "base_dt": base_date,
            "upd_stkpc_tp": adjusted_price_type
        }
        response = self._make_request("/api/dostk/chart", "ka10081", data)
        return {
            "stk_cd": response.get("stk_cd", symbol),
            "stk_dt_pole_chart_qry": response.get("stk_dt_pole_chart_qry", [])
        }

    def get_stock_weekly_chart(
        self,
        symbol: str,
        base_date: str = "",        # 기준일자 (YYYYMMDD, 공백시 당일)
        adjusted_price_type: str = "1"  # 수정주가구분 (1:수정주가)
    ) -> Dict[str, Any]:
        """
        Get stock weekly chart data (ka10082).
        주식주봉차트조회요청
        
        Args:
            symbol: 종목코드
            base_date: 기준일자 (YYYYMMDD, 공백시 당일)
            adjusted_price_type: 수정주가구분 (1:수정주가)
            
        Returns:
            Dictionary containing weekly chart data with symbol and weekly data list
        """
        data = {
            "stk_cd": symbol,
            "base_dt": base_date,
            "upd_stkpc_tp": adjusted_price_type
        }
        response = self._make_request("/api/dostk/chart", "ka10082", data)
        return {
            "stk_cd": response.get("stk_cd", symbol),
            "stk_wk_pole_chart_qry": response.get("stk_wk_pole_chart_qry", [])
        }

    def get_stock_monthly_chart(
        self,
        symbol: str,
        base_date: str = "",        # 기준일자 (YYYYMMDD, 공백시 당일)
        adjusted_price_type: str = "1"  # 수정주가구분 (1:수정주가)
    ) -> Dict[str, Any]:
        """
        Get stock monthly chart data (ka10083).
        주식월봉차트조회요청
        
        Args:
            symbol: 종목코드
            base_date: 기준일자 (YYYYMMDD, 공백시 당일)
            adjusted_price_type: 수정주가구분 (1:수정주가)
            
        Returns:
            Dictionary containing monthly chart data with symbol and monthly data list
        """
        data = {
            "stk_cd": symbol,
            "base_dt": base_date,
            "upd_stkpc_tp": adjusted_price_type
        }
        response = self._make_request("/api/dostk/chart", "ka10083", data)
        return {
            "stk_cd": response.get("stk_cd", symbol),
            "stk_mth_pole_chart_qry": response.get("stk_mth_pole_chart_qry", [])
        }

    def get_stock_yearly_chart(
        self,
        symbol: str,
        base_date: str = "",        # 기준일자 (YYYYMMDD, 공백시 당일)
        adjusted_price_type: str = "1"  # 수정주가구분 (1:수정주가)
    ) -> Dict[str, Any]:
        """
        Get stock yearly chart data (ka10094).
        주식년봉차트조회요청
        
        Args:
            symbol: 종목코드
            base_date: 기준일자 (YYYYMMDD, 공백시 당일)
            adjusted_price_type: 수정주가구분 (1:수정주가)
            
        Returns:
            Dictionary containing yearly chart data with symbol and yearly data list
        """
        data = {
            "stk_cd": symbol,
            "base_dt": base_date,
            "upd_stkpc_tp": adjusted_price_type
        }
        response = self._make_request("/api/dostk/chart", "ka10094", data)
        return {
            "stk_cd": response.get("stk_cd", symbol),
            "stk_yr_pole_chart_qry": response.get("stk_yr_pole_chart_qry", [])
        }

    def get_sector_tick_chart(
        self,
        sector_code: str,           # 업종코드 (예: 001)
        tick_scope: str = "1"       # 틱범위 (1:전체)
    ) -> Dict[str, Any]:
        """
        Get sector tick chart data (ka20004).
        업종틱차트조회요청
        
        Args:
            sector_code: 업종코드 (예: 001)
            tick_scope: 틱범위 (1:전체)
            
        Returns:
            Dictionary containing sector tick chart data
        """
        data = {
            "inds_cd": sector_code,
            "tic_scope": tick_scope
        }
        response = self._make_request("/api/dostk/chart", "ka20004", data)
        return {
            "inds_cd": response.get("inds_cd", sector_code),
            "inds_tic_chart_qry": response.get("inds_tic_chart_qry", [])
        }

    def get_sector_minute_chart(
        self,
        sector_code: str,           # 업종코드 (예: 001)
        minute_type: str = "1"      # 분구분 (1:1분, 3:3분, 5:5분, 10:10분, 15:15분, 30:30분, 60:60분)
    ) -> Dict[str, Any]:
        """
        Get sector minute chart data (ka20005).
        업종분봉조회요청
        
        Args:
            sector_code: 업종코드 (예: 001)
            minute_type: 분구분 (1:1분, 3:3분, 5:5분, 10:10분, 15:15분, 30:30분, 60:60분)
            
        Returns:
            Dictionary containing sector minute chart data
        """
        data = {
            "inds_cd": sector_code,
            "min_tp": minute_type
        }
        response = self._make_request("/api/dostk/chart", "ka20005", data)
        return {
            "inds_cd": response.get("inds_cd", sector_code),
            "inds_min_pole_qry": response.get("inds_min_pole_qry", [])
        }

    def get_sector_daily_chart(
        self,
        sector_code: str,           # 업종코드 (예: 001)
        base_date: str = ""         # 기준일자 (YYYYMMDD, 공백시 당일)
    ) -> Dict[str, Any]:
        """
        Get sector daily chart data (ka20006).
        업종일봉조회요청
        
        Args:
            sector_code: 업종코드 (예: 001)
            base_date: 기준일자 (YYYYMMDD, 공백시 당일)
            
        Returns:
            Dictionary containing sector daily chart data
        """
        data = {
            "inds_cd": sector_code,
            "base_dt": base_date
        }
        response = self._make_request("/api/dostk/chart", "ka20006", data)
        return {
            "inds_cd": response.get("inds_cd", sector_code),
            "inds_dt_pole_qry": response.get("inds_dt_pole_qry", [])
        }

    def get_sector_weekly_chart(
        self,
        sector_code: str,           # 업종코드 (예: 001)
        base_date: str = ""         # 기준일자 (YYYYMMDD, 공백시 당일)
    ) -> Dict[str, Any]:
        """
        Get sector weekly chart data (ka20007).
        업종주봉조회요청
        
        Args:
            sector_code: 업종코드 (예: 001)
            base_date: 기준일자 (YYYYMMDD, 공백시 당일)
            
        Returns:
            Dictionary containing sector weekly chart data
        """
        data = {
            "inds_cd": sector_code,
            "base_dt": base_date
        }
        response = self._make_request("/api/dostk/chart", "ka20007", data)
        return {
            "inds_cd": response.get("inds_cd", sector_code),
            "inds_stk_pole_qry": response.get("inds_stk_pole_qry", [])
        }

    def get_sector_monthly_chart(
        self,
        sector_code: str,           # 업종코드 (예: 002)
        base_date: str = ""         # 기준일자 (YYYYMMDD, 공백시 당일)
    ) -> Dict[str, Any]:
        """
        Get sector monthly chart data (ka20008).
        업종월봉조회요청
        
        Args:
            sector_code: 업종코드 (예: 002)
            base_date: 기준일자 (YYYYMMDD, 공백시 당일)
            
        Returns:
            Dictionary containing sector monthly chart data
        """
        data = {
            "inds_cd": sector_code,
            "base_dt": base_date
        }
        response = self._make_request("/api/dostk/chart", "ka20008", data)
        return {
            "inds_cd": response.get("inds_cd", sector_code),
            "inds_mth_pole_qry": response.get("inds_mth_pole_qry", [])
        }

    def get_sector_yearly_chart(
        self,
        sector_code: str,           # 업종코드 (예: 001)
        base_date: str = ""         # 기준일자 (YYYYMMDD, 공백시 당일)
    ) -> Dict[str, Any]:
        """
        Get sector yearly chart data (ka20019).
        업종년봉조회요청
        
        Args:
            sector_code: 업종코드 (예: 001)
            base_date: 기준일자 (YYYYMMDD, 공백시 당일)
            
        Returns:
            Dictionary containing sector yearly chart data
        """
        data = {
            "inds_cd": sector_code,
            "base_dt": base_date
        }
        response = self._make_request("/api/dostk/chart", "ka20019", data)
        return {
            "inds_cd": response.get("inds_cd", sector_code),
            "inds_yr_pole_qry": response.get("inds_yr_pole_qry", [])
        }

    # ============================================================================
    # Theme (테마) API Methods
    # ============================================================================

    def get_theme_groups(
        self,
        qry_tp: str,
        date_tp: str,
        flu_pl_amt_tp: str,
        stex_tp: str,
        stk_cd: str = "",
        thema_nm: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        테마그룹별요청 (ka90001) - Get theme group information
        
        Args:
            qry_tp: 검색구분 (0:전체검색, 1:테마검색, 2:종목검색)
            date_tp: 날짜구분 (n일전, 1일 ~ 99일 날짜입력)
            flu_pl_amt_tp: 등락수익구분 (1:상위기간수익률, 2:하위기간수익률, 3:상위등락률, 4:하위등락률)
            stex_tp: 거래소구분 (1:KRX, 2:NXT, 3:통합)
            stk_cd: 종목코드 (optional)
            thema_nm: 테마명 (optional)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing theme group information including:
            - thema_grp: List of theme groups with statistics
            - Each group contains: theme code, name, stock count, rise/fall info, period returns
        """
        data = {
            "qry_tp": qry_tp,
            "stk_cd": stk_cd,
            "date_tp": date_tp,
            "thema_nm": thema_nm,
            "flu_pl_amt_tp": flu_pl_amt_tp,
            "stex_tp": stex_tp,
            **kwargs
        }
        
        return self._make_request("ka90001", "/api/dostk/thme", data)

    def get_theme_component_stocks(
        self,
        thema_grp_cd: str,
        stex_tp: str,
        date_tp: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        테마구성종목요청 (ka90002) - Get stocks in a theme group
        
        Args:
            thema_grp_cd: 테마그룹코드 (6-digit theme group code)
            stex_tp: 거래소구분 (1:KRX, 2:NXT, 3:통합)
            date_tp: 날짜구분 (1일 ~ 99일 날짜입력, optional)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing theme component stocks information including:
            - flu_rt: Overall theme rise/fall rate
            - dt_prft_rt: Period return rate
            - thema_comp_stk: List of stocks in the theme with detailed data
        """
        data = {
            "date_tp": date_tp,
            "thema_grp_cd": thema_grp_cd,
            "stex_tp": stex_tp,
            **kwargs
        }
        
        return self._make_request("ka90002", "/api/dostk/thme", data)