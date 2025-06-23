"""
Main client for Kiwoom Securities REST API.
"""

import requests
from typing import Dict, Any, Optional, List, Union
import time
from urllib.parse import urljoin

from .exceptions import (
    KiwoomAPIError,
    KiwoomAuthError, 
    KiwoomRequestError,
    KiwoomRateLimitError,
    KiwoomServerError
)
from .models import (
    QuoteData,
    MarketData,
    OrderData,
    ETFData,
    ELWData,
    AccountBalance,
    Position,
    TokenRequest,
    TokenResponse,
    TokenRevokeRequest,
    TokenRevokeResponse,
    OrderRequest,
    OrderResponse,
    ModifyOrderRequest,
    ModifyOrderResponse,
    CancelOrderRequest,
    CancelOrderResponse
)


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
        is_production: bool = False,
        timeout: int = 30,
        retry_attempts: int = 3,
        rate_limit_delay: float = 0.1
    ):
        """
        Initialize Kiwoom API client.
        
        Args:
            access_token: Your Kiwoom API access token
            is_production: Whether to use production or sandbox environment
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
            rate_limit_delay: Delay between requests to avoid rate limiting
        """
        self.access_token = access_token
        self.base_url = self.PRODUCTION_URL if is_production else self.SANDBOX_URL
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.rate_limit_delay = rate_limit_delay
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json;charset=UTF-8"
        })
    
    @classmethod
    def create_with_credentials(
        cls,
        appkey: str,
        secretkey: str,
        is_production: bool = False,
        **kwargs
    ) -> 'KiwoomClient':
        """
        Create a client instance by automatically obtaining an access token.
        
        Args:
            appkey: App key from Kiwoom Securities
            secretkey: Secret key from Kiwoom Securities  
            is_production: Whether to use production or sandbox environment
            **kwargs: Additional arguments for KiwoomClient constructor
            
        Returns:
            Configured KiwoomClient instance
        """
        token_response = cls.issue_token(appkey, secretkey, is_production)
        return cls(
            access_token=token_response.token,
            is_production=is_production,
            **kwargs
        )
    
    @staticmethod
    def issue_token(appkey: str, secretkey: str, is_production: bool = False) -> TokenResponse:
        """
        Issue a new access token using app credentials (au10001).
        
        Args:
            appkey: App key from Kiwoom Securities
            secretkey: Secret key from Kiwoom Securities
            is_production: Whether to use production or sandbox environment
            
        Returns:
            TokenResponse with access token and expiration info
        """
        base_url = KiwoomClient.PRODUCTION_URL if is_production else KiwoomClient.SANDBOX_URL
        url = urljoin(base_url, "/oauth2/token")
        
        token_request = TokenRequest(
            grant_type="client_credentials",
            appkey=appkey,
            secretkey=secretkey
        )
        
        headers = {
            "Content-Type": "application/json;charset=UTF-8"
        }
        
        response = requests.post(
            url,
            json=token_request.model_dump(),
            headers=headers,
            timeout=30
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
    def revoke_token(appkey: str, secretkey: str, token: str, is_production: bool = False) -> TokenRevokeResponse:
        """
        Revoke an access token (au10002).
        
        Args:
            appkey: App key from Kiwoom Securities
            secretkey: Secret key from Kiwoom Securities  
            token: Access token to revoke
            is_production: Whether to use production or sandbox environment
            
        Returns:
            TokenRevokeResponse confirming revocation
        """
        base_url = KiwoomClient.PRODUCTION_URL if is_production else KiwoomClient.SANDBOX_URL
        url = urljoin(base_url, "/oauth2/revoke")
        
        revoke_request = TokenRevokeRequest(
            appkey=appkey,
            secretkey=secretkey,
            token=token
        )
        
        headers = {
            "Content-Type": "application/json;charset=UTF-8"
        }
        
        response = requests.post(
            url,
            json=revoke_request.model_dump(),
            headers=headers,
            timeout=30
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
            is_production=(self.base_url == self.PRODUCTION_URL)
        )
    
    def _make_request(
        self,
        endpoint: str,
        api_id: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cont_yn: Optional[str] = None,
        next_key: Optional[str] = None
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
                    time.sleep(self.rate_limit_delay * (2 ** attempt))
                
                response = self.session.post(
                    url,
                    json=json_data,
                    headers=request_headers,
                    timeout=self.timeout
                )
                
                # Handle HTTP errors
                if response.status_code == 401:
                    raise KiwoomAuthError("Authentication failed. Check your access token.")
                elif response.status_code == 429:
                    raise KiwoomRateLimitError("Rate limit exceeded. Please slow down requests.")
                elif response.status_code >= 500:
                    raise KiwoomServerError(f"Server error: {response.status_code}")
                elif response.status_code >= 400:
                    raise KiwoomRequestError(
                        f"Request failed: {response.status_code}",
                        status_code=response.status_code
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
                    raise KiwoomRequestError(f"API error {return_code}: {error_msg}", response_data=response_data)
                
                return response_data
                
            except (requests.RequestException, KiwoomRateLimitError) as e:
                if attempt == self.retry_attempts - 1:
                    raise KiwoomAPIError(f"Request failed after {self.retry_attempts} attempts: {e}")
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
        self, 
        symbol: str, 
        period: str = "D",
        count: Optional[int] = None
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
        data = {
            "stk_cd": symbol,
            "period": period
        }
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
        self, 
        symbol: str, 
        etf_index_code: str,
        period: str = "3"
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
        data = {
            "stk_cd": symbol,
            "etfobjt_idex_cd": etf_index_code,
            "dt": period
        }
        response = self._make_request("/api/dostk/etf", "ka40001", data)
        return response.get("etfprft_rt_lst", [])
    
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
            vega=response.get("vega")
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
    
    # Account Methods (these would require proper authentication and account access)
    
    def get_account_balance(self, account_number: str) -> AccountBalance:
        """
        Get account balance information.
        
        Args:
            account_number: Account number
            
        Returns:
            AccountBalance object
        """
        # This would require the account API endpoints
        # Implementation depends on the specific account APIs available
        raise NotImplementedError("Account APIs require additional authentication setup")
    
    def get_positions(self, account_number: str) -> List[Position]:
        """
        Get current stock positions.
        
        Args:
            account_number: Account number
            
        Returns:
            List of Position objects
        """
        # This would require the account API endpoints
        raise NotImplementedError("Account APIs require additional authentication setup")
    
    # Utility Methods
    
    def search_stocks(self, query: str, market: str = "KRX") -> List[Dict[str, Any]]:
        """
        Search for stocks by name or symbol.
        
        Args:
            query: Search query (name or symbol)
            market: Market code ("KRX", "KOSPI", "KOSDAQ")
            
        Returns:
            List of matching stocks
        """
        # This would require a stock search API
        # Implementation depends on available search endpoints
        raise NotImplementedError("Stock search API not yet implemented")
    
    def get_market_status(self) -> Dict[str, Any]:
        """
        Get market status information.
        
        Returns:
            Dictionary containing market status
        """
        return self._make_request("/api/dostk/mkstat", "")
    
    # ===========================================
    # TRADING METHODS
    # ===========================================
    
    def buy_stock(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "3",  # Default to market order
        market: str = "KRX",
        condition_price: Optional[float] = None
    ) -> 'OrderResponse':
        """
        Place a buy order for a stock (kt10000).
        
        Args:
            symbol: Stock symbol (e.g., "005930")
            quantity: Number of shares to buy
            price: Order price (None for market orders)
            order_type: Order type (see OrderType enum)
            market: Market type (KRX, NXT, SOR)
            condition_price: Conditional price for conditional orders
            
        Returns:
            OrderResponse with order number and status
        """
        order_data = OrderRequest(
            dmst_stex_tp=market,
            stk_cd=symbol,
            ord_qty=str(quantity),
            ord_uv=str(price) if price else "",
            trde_tp=order_type,
            cond_uv=str(condition_price) if condition_price else ""
        )
        
        response = self._make_request("/api/dostk/ordr", "kt10000", order_data.model_dump())
        return OrderResponse(**response)
    
    def sell_stock(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "3",  # Default to market order
        market: str = "KRX",
        condition_price: Optional[float] = None
    ) -> 'OrderResponse':
        """
        Place a sell order for a stock (kt10001).
        
        Args:
            symbol: Stock symbol (e.g., "005930")
            quantity: Number of shares to sell
            price: Order price (None for market orders)
            order_type: Order type (see OrderType enum)
            market: Market type (KRX, NXT, SOR)
            condition_price: Conditional price for conditional orders
            
        Returns:
            OrderResponse with order number and status
        """
        order_data = OrderRequest(
            dmst_stex_tp=market,
            stk_cd=symbol,
            ord_qty=str(quantity),
            ord_uv=str(price) if price else "",
            trde_tp=order_type,
            cond_uv=str(condition_price) if condition_price else ""
        )
        
        response = self._make_request("/api/dostk/ordr", "kt10001", order_data.model_dump())
        return OrderResponse(**response)
    
    def modify_order(
        self,
        original_order_number: str,
        symbol: str,
        new_quantity: int,
        new_price: float,
        market: str = "KRX",
        condition_price: Optional[float] = None
    ) -> 'ModifyOrderResponse':
        """
        Modify an existing order (kt10002).
        
        Args:
            original_order_number: Original order number to modify
            symbol: Stock symbol
            new_quantity: New quantity
            new_price: New price
            market: Market type (KRX, NXT, SOR)
            condition_price: New conditional price
            
        Returns:
            ModifyOrderResponse with new order details
        """
        modify_data = ModifyOrderRequest(
            dmst_stex_tp=market,
            orig_ord_no=original_order_number,
            stk_cd=symbol,
            mdfy_qty=str(new_quantity),
            mdfy_uv=str(new_price),
            mdfy_cond_uv=str(condition_price) if condition_price else ""
        )
        
        response = self._make_request("/api/dostk/ordr", "kt10002", modify_data.model_dump())
        return ModifyOrderResponse(**response)
    
    def cancel_order(
        self,
        original_order_number: str,
        symbol: str,
        cancel_quantity: int,
        market: str = "KRX"
    ) -> 'CancelOrderResponse':
        """
        Cancel an existing order (kt10003).
        
        Args:
            original_order_number: Original order number to cancel
            symbol: Stock symbol
            cancel_quantity: Quantity to cancel
            market: Market type (KRX, NXT, SOR)
            
        Returns:
            CancelOrderResponse with cancellation details
        """
        cancel_data = CancelOrderRequest(
            dmst_stex_tp=market,
            orig_ord_no=original_order_number,
            stk_cd=symbol,
            cncl_qty=str(cancel_quantity)
        )
        
        response = self._make_request("/api/dostk/ordr", "kt10003", cancel_data.model_dump())
        return CancelOrderResponse(**response)
    
    # Credit trading methods
    def buy_stock_credit(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "3",
        market: str = "KRX",
        condition_price: Optional[float] = None
    ) -> 'OrderResponse':
        """
        Place a credit buy order (kt10006).
        """
        order_data = OrderRequest(
            dmst_stex_tp=market,
            stk_cd=symbol,
            ord_qty=str(quantity),
            ord_uv=str(price) if price else "",
            trde_tp=order_type,
            cond_uv=str(condition_price) if condition_price else ""
        )
        
        response = self._make_request("/api/dostk/ordr", "kt10006", order_data.model_dump())
        return OrderResponse(**response)
    
    def sell_stock_credit(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "3",
        market: str = "KRX",
        condition_price: Optional[float] = None
    ) -> 'OrderResponse':
        """
        Place a credit sell order (kt10007).
        """
        order_data = OrderRequest(
            dmst_stex_tp=market,
            stk_cd=symbol,
            ord_qty=str(quantity),
            ord_uv=str(price) if price else "",
            trde_tp=order_type,
            cond_uv=str(condition_price) if condition_price else ""
        )
        
        response = self._make_request("/api/dostk/ordr", "kt10007", order_data.model_dump())
        return OrderResponse(**response)
    
    def modify_order_credit(
        self,
        original_order_number: str,
        symbol: str,
        new_quantity: int,
        new_price: float,
        market: str = "KRX",
        condition_price: Optional[float] = None
    ) -> 'ModifyOrderResponse':
        """
        Modify a credit order (kt10008).
        """
        modify_data = ModifyOrderRequest(
            dmst_stex_tp=market,
            orig_ord_no=original_order_number,
            stk_cd=symbol,
            mdfy_qty=str(new_quantity),
            mdfy_uv=str(new_price),
            mdfy_cond_uv=str(condition_price) if condition_price else ""
        )
        
        response = self._make_request("/api/dostk/ordr", "kt10008", modify_data.model_dump())
        return ModifyOrderResponse(**response)
    
    def cancel_order_credit(
        self,
        original_order_number: str,
        symbol: str,
        cancel_quantity: int,
        market: str = "KRX"
    ) -> 'CancelOrderResponse':
        """
        Cancel a credit order (kt10009).
        """
        cancel_data = CancelOrderRequest(
            dmst_stex_tp=market,
            orig_ord_no=original_order_number,
            stk_cd=symbol,
            cncl_qty=str(cancel_quantity)
        )
        
        response = self._make_request("/api/dostk/ordr", "kt10009", cancel_data.model_dump())
        return CancelOrderResponse(**response)
    
    # ===========================================
    # ENHANCED MARKET DATA METHODS
    # ===========================================
    
    def get_intraday_prices(self, symbol: str) -> 'IntradayPrice':
        """
        Get intraday minute-by-minute price data (ka10006).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            IntradayPrice data
        """
        from .models import IntradayPrice
        
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10006", data)
        return IntradayPrice(**response)
    
    def get_market_performance(self, symbol: str) -> 'MarketPerformance':
        """
        Get market performance indicators (ka10007).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            MarketPerformance data
        """
        from .models import MarketPerformance
        
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10007", data)
        return MarketPerformance(**response)
    
    def get_new_shares_rights(self) -> List[Dict[str, Any]]:
        """
        Get new shares subscription rights data (ka10011).
        
        Returns:
            List of new shares rights data
        """
        response = self._make_request("/api/dostk/mrkcond", "ka10011", {})
        return response.get("data", [])
    
    def get_daily_institutional_trading(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get daily institutional trading data (ka10044).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of institutional trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10044", data)
        return response.get("data", [])
    
    def get_institutional_trading_trends(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get institutional trading trends by symbol (ka10045).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of institutional trading trends
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10045", data)
        return response.get("data", [])
    
    def get_trading_intensity_hourly(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get trading intensity trends by hour (ka10046).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of hourly trading intensity data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10046", data)
        return response.get("data", [])
    
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
        return response.get("data", [])
    
    def get_intraday_investor_trading(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get intraday investor trading data (ka10063).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of investor trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10063", data)
        return response.get("data", [])
    
    def get_after_hours_investor_trading(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get after-hours investor trading data (ka10066).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of after-hours investor trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10066", data)
        return response.get("data", [])
    
    def get_securities_firm_trading_trends(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get securities firm trading trends (ka10078).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of securities firm trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10078", data)
        return response.get("data", [])
    
    def get_daily_stock_prices(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily stock prices (ka10086).
        
        Args:
            symbol: Stock symbol
            days: Number of days to retrieve
            
        Returns:
            List of daily price data
        """
        data = {"stk_cd": symbol, "cnt": str(days)}
        response = self._make_request("/api/dostk/mrkcond", "ka10086", data)
        return response.get("data", [])
    
    def get_after_hours_single_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get after-hours single price data (ka10087).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            After-hours single price data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka10087", data)
        return response
    
    # Program trading methods
    def get_program_trading_hourly(self) -> List[Dict[str, Any]]:
        """
        Get program trading trends by hour (ka90005).
        
        Returns:
            List of hourly program trading data
        """
        response = self._make_request("/api/dostk/mrkcond", "ka90005", {})
        return response.get("data", [])
    
    def get_program_trading_arbitrage(self) -> List[Dict[str, Any]]:
        """
        Get program trading arbitrage balance trends (ka90006).
        
        Returns:
            List of arbitrage balance data
        """
        response = self._make_request("/api/dostk/mrkcond", "ka90006", {})
        return response.get("data", [])
    
    def get_program_trading_cumulative(self) -> List[Dict[str, Any]]:
        """
        Get program trading cumulative trends (ka90007).
        
        Returns:
            List of cumulative program trading data
        """
        response = self._make_request("/api/dostk/mrkcond", "ka90007", {})
        return response.get("data", [])
    
    def get_symbol_program_trading_hourly(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get symbol hourly program trading trends (ka90008).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of symbol-specific hourly program trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka90008", data)
        return response.get("data", [])
    
    def get_program_trading_daily(self) -> List[Dict[str, Any]]:
        """
        Get program trading trends daily (ka90010).
        
        Returns:
            List of daily program trading data
        """
        response = self._make_request("/api/dostk/mrkcond", "ka90010", {})
        return response.get("data", [])
    
    def get_symbol_program_trading_daily(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get symbol daily program trading trends (ka90013).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of symbol-specific daily program trading data
        """
        data = {"stk_cd": symbol}
        response = self._make_request("/api/dostk/mrkcond", "ka90013", data)
        return response.get("data", [])
    
    # ===========================================
    # ACCOUNT MANAGEMENT METHODS
    # ===========================================
    
    def get_daily_stock_profit_loss(
        self, 
        symbol: str, 
        start_date: str
    ) -> List['RealizedProfitLoss']:
        """
        Get daily realized profit/loss by stock (ka10072).
        
        Args:
            symbol: Stock symbol
            start_date: Start date in YYYYMMDD format
            
        Returns:
            List of RealizedProfitLoss data
        """
        from .models import RealizedProfitLoss
        
        data = {
            "stk_cd": symbol,
            "strt_dt": start_date
        }
        response = self._make_request("/api/dostk/acnt", "ka10072", data)
        profit_loss_data = response.get("dt_stk_div_rlzt_pl", [])
        return [RealizedProfitLoss(**item) for item in profit_loss_data]
    
    def get_period_stock_profit_loss(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> List['RealizedProfitLoss']:
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
        
        data = {
            "stk_cd": symbol,
            "strt_dt": start_date,
            "end_dt": end_date
        }
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
        exchange_type: str = "0"
    ) -> List['UnfilledOrder']:
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
            "stex_tp": exchange_type
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
        exchange_type: str = "0"
    ) -> List['FilledOrder']:
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
        
        data = {
            "qry_tp": query_type,
            "sell_tp": sell_type,
            "stex_tp": exchange_type
        }
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
    
    def get_daily_trading_journal(self, date: str) -> List['TradingJournal']:
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
    
    def get_deposit_details(self) -> 'DepositDetail':
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
    
    def get_estimated_assets(self) -> 'AssetEvaluation':
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
        self,
        order_number: Optional[str] = None,
        symbol: Optional[str] = None
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
        self,
        symbol: str,
        margin_rate: str
    ) -> Dict[str, Any]:
        """
        Get margin rate order available quantity (kt00011).
        
        Args:
            symbol: Stock symbol
            margin_rate: Margin rate
            
        Returns:
            Available quantity data
        """
        data = {
            "stk_cd": symbol,
            "margin_rate": margin_rate
        }
        response = self._make_request("/api/dostk/acnt", "kt00011", data)
        return response
    
    def get_credit_guarantee_rate_order_quantity(
        self,
        symbol: str,
        guarantee_rate: str
    ) -> Dict[str, Any]:
        """
        Get credit guarantee rate order available quantity (kt00012).
        
        Args:
            symbol: Stock symbol
            guarantee_rate: Guarantee rate
            
        Returns:
            Available quantity data
        """
        data = {
            "stk_cd": symbol,
            "guarantee_rate": guarantee_rate
        }
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
        self,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get consignment comprehensive transaction details (kt00015).
        
        Args:
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
            
        Returns:
            List of transaction detail data
        """
        data = {
            "strt_dt": start_date,
            "end_dt": end_date
        }
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