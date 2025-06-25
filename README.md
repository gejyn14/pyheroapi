# PyHero API - AI와 만들어본 키움증권 REST API Python 클라이언트 v0.3.0

[![PyPI version](https://badge.fury.io/py/pyheroapi.svg)](https://badge.fury.io/py/pyheroapi)
[![Python versions](https://img.shields.io/pypi/pyversions/pyheroapi.svg)](https://pypi.org/project/pyheroapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://github.com/gejyn14/pyheroapi#readme)

키움증권 REST API를 파이썬으로 직관적으로 사용하기 위한 클라이언트 라이브러리입니다.

🚀 **v0.3.0 새로운 기능**: 포괄적인 예제 시스템, 실시간 WebSocket 지원, 163개 API 메소드 완전 구현

---

## 🌟 주요 특징

### 💡 **직관적이고 강력한 API**
- 🎯 **한 줄 연결**: `pyheroapi.connect()` 한 번으로 모든 기능 사용
- 🔄 **자동 토큰 관리**: 토큰 발급, 갱신, 폐기 완전 자동화
- 🛡️ **우아한 오류 처리**: 예외 대신 안전한 기본값 반환
- ⚡ **스마트 캐싱**: 중복 API 호출 자동 최적화

### 📊 **완전한 거래 시스템**
- ✅ **포괄적인 주문 관리**: 매수/매도, 정정/취소, 조건부 주문
- ✅ **신용거래 지원**: 신용 매수/매도, 대출 관리
- ✅ **다양한 주문 유형**: 지정가, 시장가, 최유리, IOC, FOK 등
- ✅ **실시간 주문 추적**: 미체결/체결 내역, 실시간 상태 업데이트

### 🔥 **실시간 데이터 스트리밍**
- 🌐 **WebSocket 실시간 시세**: 주가, 호가, 체결 데이터
- 📈 **실시간 계좌 모니터링**: 잔고, 포지션 변화 추적
- ⚡ **비동기 처리**: async/await 패턴 완전 지원
- 🔔 **이벤트 기반 콜백**: 실시간 데이터 변화 알림

### 💰 **고급 금융 데이터 분석**
- 📊 **ETF 심화 분석**: NAV, 추적오차, 수익률, 구성종목
- ⚡ **ELW 전문 도구**: 그릭스(Delta, Gamma, Theta, Vega), 민감도 지표
- 🏛️ **기관/외국인 매매**: 실시간 매매 동향, 순매수/순매도
- 📈 **시장 순위 분석**: 거래량, 등락률, 시가총액 순위

### 🎓 **교육적 예제 시스템**
- 📚 **7개 포괄적 모듈**: 기초부터 고급까지 단계별 학습
- 🛡️ **안전한 샌드박스**: 기본적으로 모의거래 환경
- 📖 **상세한 문서화**: 모든 기능에 대한 실용적 예제
- 🔧 **프로덕션 준비**: 실제 거래를 위한 안전 가이드

---

## 🎯 완전한 API 커버리지

### **✅ 163개 API 메소드 구현 완료**

| 카테고리 | 구현된 기능 | 커버리지 |
|---------|------------|---------|
| 🔐 **인증 & 토큰** | 토큰 발급/폐기, 자동 관리 | **100%** |
| 💰 **주문 & 거래** | 모든 주문 유형, 신용거래 | **100%** |
| 🏛️ **계좌 관리** | 잔고, 포지션, 손익분석 | **100%** |
| 📊 **시세 데이터** | 실시간/과거 시세, 호가 | **100%** |
| 📈 **차트 데이터** | 일/주/월/분봉, 기술적 지표 | **100%** |
| 🔍 **종목 정보** | 종목 상세정보, 재무데이터 | **95%** |
| 💹 **ETF 분석** | NAV, 추적오차, 구성종목 | **100%** |
| ⚡ **ELW 도구** | 그릭스, 민감도, 조건검색 | **100%** |
| 📊 **순위 정보** | 거래량/등락률/시총 순위 | **100%** |
| 🏢 **기관/외국인** | 매매 동향, 보유 현황 | **100%** |
| 🔄 **실시간 데이터** | WebSocket 스트리밍 | **100%** |
| 🎯 **조건 검색** | 실시간 조건검색, 조건목록 관리 | **100%** |

---

## 🚀 빠른 시작

### 설치

```bash
# 기본 설치
pip install pyheroapi

# 실시간 기능 포함
pip install pyheroapi[realtime]

# 모든 기능 포함
pip install pyheroapi[all]
```

### 환경 변수 설정

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export KIWOOM_APPKEY="your_app_key_here"
export KIWOOM_SECRETKEY="your_secret_key_here"  
export KIWOOM_ACCOUNT_NUMBER="your_account_number_here"
```

### 🎯 30초 시작하기

```python
import pyheroapi

# 1. 간단한 연결 (샌드박스 모드)
with pyheroapi.connect(is_production=False) as api:  # SANDBOX MODE: set is_production=False explicitly
    # 2. 주식 가격 조회
    samsung = api.stock("005930")
    price = samsung.current_price
    print(f"삼성전자: ₩{price:,.0f}")
    
    # 3. 계좌 정보
    account = api.account()
    balance = account.balance["available_balance"] 
    print(f"주문가능금액: ₩{balance:,.0f}")
    
    # 4. 시장 순위 (상위 10개)
    rankings = api.rankings.volume_leaders(limit=10)
    for rank, stock in enumerate(rankings, 1):
        print(f"{rank}. {stock['name']}: {stock['volume']:,}주")
```

---

## 📚 포괄적인 예제 시스템

### 🎓 **7개 교육 모듈 - 초급부터 전문가까지**

#### [`01_authentication.py`](examples/01_authentication.py) - 🔐 인증 기초
```python
# 토큰 관리의 모든 것
from pyheroapi import KiwoomClient

# 환경변수에서 자동 로드
client = KiwoomClient.create_with_credentials()

# 토큰 수동 관리
token = client.issue_token()
print(f"발급된 토큰: {token.token[:20]}...")

# 토큰 검증 및 폐기
is_valid = client.validate_token()
client.revoke_token()
```

#### [`02_market_data.py`](examples/02_market_data.py) - 📊 시세 데이터 마스터
```python
# 실시간 시세부터 과거 데이터까지
with pyheroapi.connect(is_production=False) as api:  # SANDBOX MODE: set is_production=False explicitly
    # 실시간 시세
    samsung = api.stock("005930")
    quote = samsung.quote
    print(f"현재가: {quote['current_price']}")
    print(f"매수호가: {quote['best_bid']}")
    print(f"매도호가: {quote['best_ask']}")
    
    # OHLCV 과거 데이터
    history = samsung.get_daily_data(period="1Y")
    
    # 분봉 데이터 
    minute_data = samsung.get_minute_data(interval="1", period="1D")
    
    # 시장 성과 지표
    performance = samsung.market_performance()
    print(f"거래강도: {performance['trading_intensity']}")
```

#### [`03_trading_orders.py`](examples/03_trading_orders.py) - 💰 거래 실행 완전 가이드
```python
# 모든 종류의 주문과 관리
with pyheroapi.connect(is_production=False) as api:  # SANDBOX MODE: set is_production=False explicitly
    # 계좌 상태 확인
    account = api.account()
    balance = account.balance
    print(f"주문가능금액: ₩{balance['available']:,.0f}")
    
    # 다양한 주문 유형
    # 지정가 매수
    result = api.trading.buy("005930", quantity=10, price=75000, order_type="limit")
    
    # 시장가 매도  
    result = api.trading.sell("005930", quantity=5, order_type="market")
    
    # 조건부 지정가
    result = api.trading.buy("005930", quantity=10, price=75000, 
                           order_type="conditional_limit", condition_price=74000)
    
    # 주문 수정/취소
    if result["success"]:
        order_no = result["order_number"]
        
        # 주문 수정
        api.trading.modify_order(order_no, "005930", new_quantity=8, new_price=74500)
        
        # 주문 취소
        api.trading.cancel_order(order_no, "005930", cancel_quantity=8)
    
    # 신용거래
    credit_result = api.trading.credit_buy("005930", quantity=100, price=75000)
```

#### [`04_etf_elw.py`](examples/04_etf_elw.py) - 💹 ETF/ELW 전문 분석
```python
# ETF와 ELW의 모든 것
with pyheroapi.connect(is_production=False) as api:  # SANDBOX MODE: set is_production=False explicitly
    # ETF 심화 분석
    kodex = api.etf("069500")
    
    # NAV 분석
    nav_data = kodex.get_nav_analysis()
    print(f"NAV: ₩{nav_data['nav']:,.2f}")
    print(f"괴리율: {nav_data['premium_discount']:.2f}%")
    print(f"추적오차: {nav_data['tracking_error']:.4f}")
    
    # ETF 구성종목
    holdings = kodex.get_holdings()
    for holding in holdings[:10]:
        print(f"{holding['symbol']}: {holding['weight']:.2f}%")
    
    # ELW 그릭스 분석
    elw = api.elw("5XXXXX")  # ELW 종목코드
    
    # 실시간 그릭스
    greeks = elw.get_greeks()
    print(f"Delta: {greeks['delta']:.4f}")
    print(f"Gamma: {greeks['gamma']:.4f}")
    print(f"Theta: {greeks['theta']:.4f}")
    print(f"Vega: {greeks['vega']:.4f}")
    
    # 민감도 지표
    sensitivity = elw.get_sensitivity_indicators()
    
    # ELW 조건 검색 (REST API)
    elw_search = client.get_elw_condition_search(
        underlying_asset_code="201",  # KOSPI200
        right_type="1",  # 콜옵션
        sort_type="1"    # 상승율순
    )
    
    # 실시간 조건검색 (WebSocket)
    async def on_condition_result(data):
        print(f"조건검색 결과: {data['symbol']} - {data['name']}")
    
    # 조건검색 목록 조회
    await client.realtime.get_conditional_search_list()
    
    # 조건검색 실행 (일반)
    await client.realtime.execute_conditional_search("1", "0")
    
    # 조건검색 실시간 모니터링
    await client.realtime.execute_conditional_search_realtime("1")
    
    # 실시간 조건검색 해제
    await client.realtime.cancel_conditional_search_realtime("1")
```

#### [`05_rankings_analysis.py`](examples/05_rankings_analysis.py) - 📈 시장 순위 분석
```python
# 시장의 모든 순위 정보
with pyheroapi.connect(is_production=False) as api:  # SANDBOX MODE: set is_production=False explicitly
    # 거래량 순위
    volume_leaders = api.rankings.volume_leaders(limit=20)
    print("🔥 거래량 TOP 20")
    for i, stock in enumerate(volume_leaders, 1):
        print(f"{i:2d}. {stock['name']:10s} {stock['volume']:>10,}주")
    
    # 상승률 순위
    gainers = api.rankings.price_gainers(limit=10)
    print("\n📈 상승률 TOP 10")
    for stock in gainers:
        print(f"{stock['name']}: +{stock['change_rate']:.2f}%")
    
    # 외국인 순매수 순위
    foreign_net_buy = api.rankings.foreign_net_buying(limit=15)
    print("\n🌍 외국인 순매수 TOP 15")
    
    # 기관 순매수 순위  
    institutional_buy = api.rankings.institutional_net_buying(limit=15)
    
    # 프로그램 매매 분석
    program_trading = api.rankings.program_trading_activity()
    
    # 섹터별 분석
    sector_performance = api.rankings.sector_performance()
    print("\n🏭 섹터 성과")
    for sector in sector_performance:
        print(f"{sector['name']}: {sector['change_rate']:+.2f}%")
```

#### [`06_charts_technical.py`](examples/06_charts_technical.py) - 📊 차트 & 기술적 분석
```python
# 모든 차트 데이터와 기술적 분석
with pyheroapi.connect(is_production=False) as api:  # SANDBOX MODE: set is_production=False explicitly
    samsung = api.stock("005930")
    
    # 다양한 시간프레임 차트
    daily_chart = samsung.get_chart_data("daily", period="6M")
    weekly_chart = samsung.get_chart_data("weekly", period="2Y") 
    monthly_chart = samsung.get_chart_data("monthly", period="5Y")
    
    # 분봉 차트 (1분, 5분, 15분, 30분, 60분)
    minute_1 = samsung.get_chart_data("1min", period="1D")
    minute_5 = samsung.get_chart_data("5min", period="5D")
    minute_30 = samsung.get_chart_data("30min", period="1M")
    
    # 기술적 지표 계산
    def calculate_sma(data, period=20):
        """단순이동평균 계산"""
        prices = [float(d['close']) for d in data]
        sma = []
        for i in range(len(prices)):
            if i >= period - 1:
                avg = sum(prices[i-period+1:i+1]) / period
                sma.append(avg)
            else:
                sma.append(None)
        return sma
    
    # 20일 이동평균
    sma_20 = calculate_sma(daily_chart, 20)
    
    # 거래량 분석
    volume_analysis = samsung.volume_analysis(period="3M")
    
    # 업종 차트 분석
    sector_chart = api.get_sector_chart("전기전자", period="1Y")
```

#### [`07_realtime_websocket.py`](examples/07_realtime_websocket.py) - 🌐 실시간 스트리밍
```python
# WebSocket을 통한 실시간 데이터 스트리밍
import asyncio
from pyheroapi import RealtimeClient

async def main():
    # 실시간 클라이언트 생성
    realtime = RealtimeClient()
    await realtime.connect()
    
    # 실시간 시세 콜백
    def on_price_update(data):
        print(f"[{data['symbol']}] ₩{data['price']:,} ({data['change']:+.2f}%)")
    
    # 실시간 호가 콜백  
    def on_orderbook_update(data):
        print(f"매수호가: ₩{data['best_bid']:,} / 매도호가: ₩{data['best_ask']:,}")
    
    # 실시간 체결 콜백
    def on_trade_update(data):
        print(f"체결: {data['quantity']:,}주 @ ₩{data['price']:,}")
    
    # 실시간 계좌 콜백
    def on_account_update(data):
        print(f"계좌변화: 잔고 ₩{data['balance']:,}")
    
    # 실시간 조건검색 콜백
    def on_conditional_search_result(data):
        print(f"🎯 조건검색 편입: {data['symbol']} - 시간: {data['time']}")
    
    def on_conditional_search_list(data):
        print(f"📋 조건검색 목록: {len(data)}개 조건식 확인")
    
    # 구독 설정
    await realtime.subscribe_price("005930", on_price_update)
    await realtime.subscribe_orderbook("005930", on_orderbook_update)  
    await realtime.subscribe_trades("005930", on_trade_update)
    await realtime.subscribe_account("your_account", on_account_update)
    
    # 조건검색 콜백 등록
    realtime.register_callback('conditional_search_realtime', on_conditional_search_result)
    realtime.register_callback('conditional_search_list', on_conditional_search_list)
    
    # 조건검색 목록 조회
    await realtime.get_conditional_search_list()
    
    # 실시간 조건검색 시작 (조건식 번호 "1")
    await realtime.execute_conditional_search_realtime("1")
    
    # 다중 종목 구독
    symbols = ["005930", "000660", "035420", "005380", "068270"]
    for symbol in symbols:
        await realtime.subscribe_price(symbol, on_price_update)
    
    # 실시간 데이터 수신 대기
    print("🔴 실시간 데이터 수신 중... (Ctrl+C로 중단)")
    try:
        await realtime.listen()
    except KeyboardInterrupt:
        print("\n⏹️ 실시간 데이터 수신 중단")
        await realtime.disconnect()

# 실행
if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔥 고급 기능

### 🎯 **스마트 포트폴리오 관리**

```python
with pyheroapi.connect(is_production=False) as api:  # SANDBOX MODE: set is_production=False explicitly
    account = api.account()
    
    # 전체 포트폴리오 분석
    portfolio = account.get_portfolio_analysis()
    print(f"총 평가금액: ₩{portfolio['total_value']:,.0f}")
    print(f"실현손익: ₩{portfolio['realized_pnl']:,.0f}")
    print(f"평가손익: ₩{portfolio['unrealized_pnl']:,.0f}")
    print(f"총 수익률: {portfolio['total_return']:.2f}%")
    
    # 종목별 포지션
    positions = account.positions
    for pos in positions:
        print(f"{pos['name']}: {pos['quantity']:,}주")
        print(f"  평균단가: ₩{pos['avg_price']:,}")
        print(f"  현재가: ₩{pos['current_price']:,}")
        print(f"  수익률: {pos['return_rate']:+.2f}%")
        print(f"  평가손익: ₩{pos['unrealized_pnl']:+,.0f}")
    
    # 일별 손익 내역
    daily_pnl = account.get_daily_pnl(days=30)
    total_trades = sum(day['trade_count'] for day in daily_pnl)
    total_pnl = sum(day['realized_pnl'] for day in daily_pnl)
    
    print(f"\n📊 30일 거래 통계")
    print(f"총 거래 횟수: {total_trades:,}회")
    print(f"실현손익 합계: ₩{total_pnl:+,.0f}")
```

### 📊 **고급 시장 분석**

```python
with pyheroapi.connect(is_production=False) as api:  # SANDBOX MODE: set is_production=False explicitly
    # 시장 전체 현황
    market_summary = api.get_market_summary()
    print(f"KOSPI: {market_summary['kospi']['value']:.2f} ({market_summary['kospi']['change']:+.2f}%)")
    print(f"KOSDAQ: {market_summary['kosdaq']['value']:.2f} ({market_summary['kosdaq']['change']:+.2f}%)")
    
    # 외국인/기관 매매 동향
    institutional_flow = api.get_institutional_trading()
    print(f"\n💰 외국인 순매매: ₩{institutional_flow['foreign_net']:+,.0f}억")
    print(f"💰 기관 순매매: ₩{institutional_flow['institution_net']:+,.0f}억")
    
    # 프로그램 매매 현황
    program_trading = api.get_program_trading()
    print(f"📈 프로그램 매수: ₩{program_trading['buy_amount']:,.0f}억")
    print(f"📉 프로그램 매도: ₩{program_trading['sell_amount']:,.0f}억")
    
    # 신용거래 현황
    credit_info = api.get_credit_balance()
    print(f"🏦 신용잔고: ₩{credit_info['credit_balance']:,.0f}억")
    print(f"🏦 대주잔고: ₩{credit_info['lending_balance']:,.0f}억")
```

### ⚡ **고성능 일괄 처리**

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def analyze_multiple_stocks(symbols):
    """여러 종목 동시 분석"""
    with pyheroapi.connect(is_production=False) as api:  # SANDBOX MODE: set is_production=False explicitly
        with ThreadPoolExecutor(max_workers=10) as executor:
            # 동시에 여러 종목 데이터 수집
            futures = []
            for symbol in symbols:
                future = executor.submit(api.stock(symbol).get_complete_data)
                futures.append((symbol, future))
            
            results = {}
            for symbol, future in futures:
                try:
                    data = future.result(timeout=30)
                    results[symbol] = data
                    print(f"✅ {symbol}: 데이터 수집 완료")
                except Exception as e:
                    print(f"❌ {symbol}: 오류 - {e}")
            
            return results

# 대형주 TOP 20 동시 분석
large_caps = ["005930", "000660", "035420", "005380", "068270", 
              "207940", "005490", "035720", "000270", "006400"]

results = asyncio.run(analyze_multiple_stocks(large_caps))
```

---

## 🛡️ 안전 가이드

### 🔒 **보안 모범 사례**

```python
import os
from pyheroapi import KiwoomClient

# ✅ 환경변수 사용 (권장)
appkey = os.getenv("KIWOOM_APPKEY")
secretkey = os.getenv("KIWOOM_SECRETKEY")

# ❌ 하드코딩 금지
# appkey = "PAKXXXXXXXX"  # 절대 금지!

# 안전한 클라이언트 생성
client = KiwoomClient.create_with_credentials(
    appkey=appkey,
    secretkey=secretkey,
    is_production=False,  # SANDBOX MODE: set is_production=False explicitly
    timeout=30,
    retry_attempts=3
)
```

### 🎯 **거래 안전 점검**

```python
def safe_trading_example():
    """안전한 거래 프로세스"""
    with pyheroapi.connect(is_production=False) as api:  # SANDBOX MODE: set is_production=False explicitly
        account = api.account()
        
        # 1. 계좌 상태 확인
        balance = account.balance
        available = balance["available_balance"]
        print(f"주문가능금액: ₩{available:,.0f}")
        
        # 2. 종목 분석
        samsung = api.stock("005930")
        current_price = samsung.current_price
        quote = samsung.quote
        
        # 3. 안전 점검
        order_amount = current_price * 100  # 100주 주문금액
        
        if available < order_amount:
            print("❌ 주문가능금액 부족")
            return
        
        if quote["volume"] < 1000:  # 최소 거래량 점검
            print("❌ 거래량 부족 - 주문 취소")
            return
        
        # 4. 주문 실행 (샌드박스에서만!)
        result = api.trading.buy("005930", quantity=100, price=current_price)
        
        if result["success"]:
            print(f"✅ 주문 성공: {result['order_number']}")
            
            # 5. 주문 상태 모니터링
            order_status = api.trading.get_order_status(result["order_number"])
            print(f"주문 상태: {order_status['status']}")
        else:
            print(f"❌ 주문 실패: {result['message']}")

# 실행
safe_trading_example()
```

---

## 🎓 단계별 학습 가이드

### **1단계: 기초 (1-2일)**
- [`01_authentication.py`](examples/01_authentication.py) - 인증과 토큰 관리
- [`02_market_data.py`](examples/02_market_data.py) - 기본 시세 조회

### **2단계: 거래 (3-5일)**  
- [`03_trading_orders.py`](examples/03_trading_orders.py) - 주문 실행과 관리
- 샌드박스에서 충분한 연습

### **3단계: 분석 (1주)**
- [`04_etf_elw.py`](examples/04_etf_elw.py) - ETF/ELW 전문 분석
- [`05_rankings_analysis.py`](examples/05_rankings_analysis.py) - 시장 순위 분석
- [`06_charts_technical.py`](examples/06_charts_technical.py) - 차트와 기술적 분석

### **4단계: 고급 (2주)**
- [`07_realtime_websocket.py`](examples/07_realtime_websocket.py) - 실시간 스트리밍
- 포트폴리오 관리 시스템 구축
- 자동 매매 시스템 개발

---

## 🔧 환경 설정

### **API 키 발급**
1. [키움 OpenAPI 홈페이지지](https://openapi.kiwoom.com/) 방문
2. 계정 생성 및 로그인
3. REST API 서비스 신청
4. APP KEY와 SECRET KEY 발급

### **개발 환경 설정**

```bash
# 1. 프로젝트 폴더 생성
mkdir my_trading_bot
cd my_trading_bot

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. PyHeroAPI 설치
pip install pyheroapi[all]

# 4. 환경변수 설정
echo 'export KIWOOM_APPKEY="키움 REST API APPKEY' >> ~/.bashrc
echo 'export KIWOOM_SECRETKEY="키움 REST API SECRETKEY"' >> ~/.bashrc
source ~/.bashrc

# 5. 첫 번째 테스트
python -c "
import pyheroapi
with pyheroapi.connect(is_production=False) as api:
    print('✅ 연결 성공!')
    print(f'삼성전자: ₩{api.stock(\"005930\").current_price:,.0f}')
"
```

---

## 📋 시스템 요구사항

- **Python**: 3.8 이상
- **운영체제**: Windows, macOS, Linux
- **메모리**: 최소 512MB (실시간 스트리밍 시 1GB 권장)
- **네트워크**: 안정적인 인터넷 연결

### **의존성 패키지**
```
requests>=2.25.0        # HTTP 클라이언트
pydantic>=2.0.0         # 데이터 검증
typing-extensions>=4.0.0 # 타입 힌트
websockets>=11.0.0      # 실시간 스트리밍 (선택사항)
```

---

## ⚠️ 중요 공지사항

### **면책조항**
- 📖 **교육 목적**: 이 라이브러리는 교육 및 개발 목적으로 제공됩니다
- 💰 **투자 책임**: 실제 거래로 인한 손실에 대해 책임지지 않습니다
- 🧪 **충분한 테스트**: 실거래 전 반드시 샌드박스에서 충분히 테스트하세요
- 📊 **시장 리스크**: 주식 투자에는 원금 손실 위험이 있습니다

### **사용 제한사항**
- 🕐 **API 호출 제한**: 초당 요청 수 제한 (자동 관리됨)
- 🏛️ **장 시간 제한**: 일부 기능은 개장 시간에만 작동
- 📱 **실시간 데이터**: 약간의 지연이 있을 수 있음
- 🔒 **보안**: API 키는 절대 공개하지 마세요

---

## 🤝 커뮤니티

### **기여하기**
1. 🍴 [저장소 포크](https://github.com/gejyn14/pyheroapi/fork)
2. 🌿 기능 브랜치 생성: `git checkout -b feature/amazing-feature`
3. 📝 변경사항 커밋: `git commit -m 'Add amazing feature'`
4. 📤 브랜치 푸시: `git push origin feature/amazing-feature`
5. 🔄 Pull Request 생성

### **지원 채널**
- 📖 **문서**: [GitHub Wiki](https://github.com/gejyn14/pyheroapi/wiki)
- 🐛 **버그 리포트**: [Issues](https://github.com/gejyn14/pyheroapi/issues)
- 💡 **기능 요청**: [Discussions](https://github.com/gejyn14/pyheroapi/discussions)
- 📧 **이메일**: dean_jin@icloud.com

### **라이선스**
MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

---

<div align="center">

### ⭐ 이 프로젝트가 도움이 되셨다면 별표를 눌러주세요!

[![GitHub stars](https://img.shields.io/github/stars/gejyn14/pyheroapi.svg?style=social&label=Star)](https://github.com/gejyn14/pyheroapi)
[![GitHub forks](https://img.shields.io/github/forks/gejyn14/pyheroapi.svg?style=social&label=Fork)](https://github.com/gejyn14/pyheroapi/fork)

**Happy Trading! 📈🚀**

**⚠️ 면책조항**: 이 라이브러리는 교육 및 개발 목적으로 제공됩니다. 실제 거래에서 발생하는 손실에 대해서는 책임지지 않습니다. 거래 시 주의하시기 바랍니다.
