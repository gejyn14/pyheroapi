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
    Position
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
        Get current market status and trading hours.
        
        Returns:
            Market status information
        """
        # This would require a market status API
        raise NotImplementedError("Market status API not yet implemented") 