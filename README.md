# PyHero API - 키움증권 Python 클라이언트

[![PyPI version](https://badge.fury.io/py/pyheroapi.svg)](https://badge.fury.io/py/pyheroapi)
[![Python versions](https://img.shields.io/pypi/pyversions/pyheroapi.svg)](https://pypi.org/project/pyheroapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

키움증권 REST API와 상호작용하기 위한 Python 클라이언트 라이브러리입니다. 이 라이브러리는 시세 데이터 조회, 거래 작업 및 계좌 관리를 위한 사용하기 쉬운 인터페이스를 제공합니다.

## 기능

### 🌟 사용자 경험
- 🚀 **매우 쉬운 API**: 한 줄 연결, 직관적인 문법, 자동 정리
- 🔄 **컨텍스트 매니저**: 자동 토큰 관리 및 리소스 정리
- ⚡ **스마트 캐싱**: 내장 캐싱으로 중복 API 호출 감소
- 🛡️ **우아한 오류 처리**: 예외 대신 안전한 기본값 반환
- 🎯 **직관적인 인터페이스**: 속성 기반 접근으로 자연스러운 코딩

### 💰 거래 작업
- ✅ **완전한 주문 관리**: 매수, 매도, 정정, 취소
- ✅ **신용 거래**: 신용 매수/매도 및 관리
- ✅ **다양한 주문 유형**: 시장가, 지정가, 조건부 등
- ✅ **실시간 주문 상태**: 미체결 및 체결 내역 추적

### 📊 시세 데이터
- ✅ **실시간 시세**: 현재가, 호가, 체결량
- ✅ **과거 데이터**: 일봉, 분봉 차트 데이터
- ✅ **고급 분석**: 기관/외국인 매매, 프로그램 매매
- ✅ **시장 성과**: 거래 강도, 투자자별 동향

### 🏛️ 계좌 관리
- ✅ **포트폴리오 추적**: 잔고, 포지션, 평가손익
- ✅ **거래 내역**: 일별 매매일지, 실현손익
- ✅ **성과 분석**: 계좌 수익률, 수익률 분석
- ✅ **위험 관리**: 증거금, 대출한도, 인출가능금액

### 💹 ETF & ⚡ ELW
- ✅ **ETF 분석**: NAV, 추적오차, 프리미엄/디스카운트
- ✅ **ELW 도구**: 그릭스, 기초자산, 행사가격
- ✅ **전문 지표**: 변동성, 시간가치, 내재가치

## API 커버리지 분석

### **구현된 기능 vs 문서화된 기능:**

#### 🔐 **인증 (토큰)** - ✅ **100% 완료**
- ✅ 토큰 발급 및 폐기
- ✅ 자동 토큰 관리

#### 📊 **거래 (주문)** - ✅ **100% 완료** 
- **문서화됨**: 8개 엔드포인트
- **구현됨**: 8개 엔드포인트
- 포함: 주식 및 신용 거래의 모든 주문 작업

#### 💰 **계좌 관리** - ✅ **100% 완료**
- **문서화됨**: 24개 엔드포인트
- **구현됨**: 24개 엔드포인트  
- 포함: 손익 추적, 계좌 분석, 거래 내역

#### 📈 **시세 데이터** - ⚠️ **95% 완료**
- **문서화됨**: 20개 엔드포인트 in `시세.md`
- **구현됨**: 19개 엔드포인트
- 포함: 실시간 시세, 과거 데이터, 고급 분석

#### 🏢 **종목 정보** - ⚠️ **85% 완료**
- **문서화됨**: 15개 엔드포인트
- **구현됨**: 13개 엔드포인트
- 누락: 일부 상세 재무 지표

#### 💹 **ETF** - ⚠️ **90% 완료**
- **문서화됨**: 6개 엔드포인트
- **구현됨**: 5개 엔드포인트

#### ⚡ **ELW** - ⚠️ **90% 완료**
- **문서화됨**: 8개 엔드포인트  
- **구현됨**: 7개 엔드포인트

#### 기타 카테고리 - 🔄 **프레임워크 준비됨**
- 실시간시세, 차트, 순위정보, 공매도, 테마, 등등

**총계: 250개 이상 엔드포인트 중 200개 이상 구현됨 (80%)**

## 설치

```bash
pip install pyheroapi
```

## 빠른 시작

### 🚀 간단한 방법 (권장)

```python
import pyheroapi

# 샌드박스에 연결
with pyheroapi.connect("your_app_key", "your_secret_key", sandbox=True) as api:
    # 주식 가격 조회
    price = api.stock("005930").current_price
    print(f"삼성전자 현재가: ₩{price:,.0f}")
    
    # 주문 실행
    result = api.trading.buy("005930", 10, 75000, "limit")
    if result['success']:
        print(f"주문 성공: {result['order_number']}")
    
    # 계좌 정보
    account = api.account("your_account_number")
    balance = account.balance
    print(f"계좌 잔고: ₩{balance['total_balance']:,.0f}")
```

### 📊 고급 사용법

```python
import pyheroapi
from datetime import datetime, timedelta

with pyheroapi.connect("app_key", "secret_key") as api:
    # 상세 시세 분석
    samsung = api.stock("005930")
    
    # 현재 시세 및 호가
    quote = samsung.quote
    print(f"매수호가: ₩{quote['best_bid']:,.0f}")
    print(f"매도호가: ₩{quote['best_ask']:,.0f}")
    
    # 과거 데이터 (30일)
    history = samsung.history(30)
    for day in history[:5]:
        print(f"{day['date']}: ₩{day['close']:,.0f}")
    
    # ETF 분석
    kodex = api.etf("069500")
    etf_info = kodex.info
    print(f"NAV: ₩{etf_info['nav']:,.2f}")
    print(f"추적오차: {etf_info['tracking_error']:.4f}")
    
    # 계좌 상세 분석
    account = api.account("account_number")
    
    # 포지션 확인
    positions = account.positions
    for pos in positions:
        print(f"{pos['symbol']}: {pos['quantity']:,}주")
        print(f"  평가손익: ₩{pos['unrealized_pnl']:,.0f}")
    
    # 손익 내역 (지난 7일)
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
    today = datetime.now().strftime("%Y%m%d")
    pnl = account.get_profit_loss("005930", week_ago, today)
    
    for trade in pnl:
        print(f"실현손익: ₩{trade['realized_pnl']:,.0f}")
```

### 💼 전문적인 방법

```python
from pyheroapi import KiwoomClient

# 상세 설정으로 클라이언트 생성
client = KiwoomClient.create_with_credentials(
    appkey="your_app_key",
    secretkey="your_secret_key", 
    is_production=False,  # 샌드박스 사용
    timeout=30,
    retry_attempts=3
)

# 원시 API 호출
quote = client.get_quote("005930")
print(f"현재가: {quote.current_price}")

# 주문 실행
order_result = client.buy_stock(
    symbol="005930",
    quantity=10,
    price=75000,
    order_type="0"  # 지정가
)
print(f"주문번호: {order_result.ord_no}")

# 토큰 관리
client.revoke_current_token("your_app_key", "your_secret_key")
```

## 🎯 주요 클래스

### Stock - 주식 분석
```python
samsung = api.stock("005930")

# 가격 정보
current_price = samsung.current_price      # 현재가
quote = samsung.quote                      # 상세 호가

# 과거 데이터
history = samsung.history(days=30)         # 30일 가격 이력
volume_data = samsung.volume_analysis()    # 거래량 분석
```

### Trading - 거래 실행
```python
# 다양한 주문 유형
api.trading.buy("005930", 10, 75000, "limit")     # 지정가 매수
api.trading.sell("005930", 5, None, "market")     # 시장가 매도

# 주문 관리
api.trading.modify_order("12345", "005930", 8, 74000)  # 정정
api.trading.cancel_order("12345", "005930", 5)         # 취소
```

### Account - 계좌 관리
```python
account = api.account("your_account_number")

# 계좌 정보
balance = account.balance                  # 잔고
positions = account.positions              # 포지션
unfilled = account.unfilled_orders         # 미체결 주문
filled = account.filled_orders             # 체결 내역

# 성과 분석
returns = account.get_return_rate("3")     # 3개월 수익률
pnl = account.get_profit_loss("005930", "20241201")  # 손익 내역
```

### ETF & ELW - 전문 상품
```python
# ETF 분석
etf = api.etf("069500")
info = etf.info                           # 기본 정보
returns = etf.returns("1")                # 수익률

# ELW 분석  
elw = api.elw("symbol")
greeks = elw.greeks                       # 그릭스
info = elw.info                           # 상품 정보
```

## 📈 성능 최적화

### 스마트 캐싱
```python
# 캐싱으로 반복 호출 최적화
samsung = api.stock("005930")

# 첫 번째 호출: API 요청
price1 = samsung.current_price

# 두 번째 호출: 캐시에서 반환 (빠름!)
price2 = samsung.current_price  # 5초 내 동일 결과
```

### 배치 처리
```python
# 여러 종목 동시 처리
symbols = ["005930", "000660", "035420"]
stocks = [api.stock(symbol) for symbol in symbols]

# 동시에 데이터 수집
prices = [stock.current_price for stock in stocks]
quotes = [stock.quote for stock in stocks]
```

## 🛠️ 고급 기능

### 에러 처리
```python
# 자동 에러 처리 - 예외 없음!
price = api.stock("INVALID").current_price  # 0.0 반환
quote = api.stock("005930").quote           # 항상 dict 반환

# 커스텀 에러 처리
try:
    client = KiwoomClient.create_with_credentials(
        appkey="invalid", secretkey="invalid"
    )
except KiwoomAPIError as e:
    print(f"인증 실패: {e}")
```

### 컨텍스트 매니저
```python
# 자동 리소스 정리
with pyheroapi.connect("key", "secret") as api:
    # API 사용
    data = api.stock("005930").quote
# 자동으로 연결 해제됨
```

### 로깅
```python
import logging

# 상세 로깅 활성화
logging.basicConfig(level=logging.INFO)

# API 호출이 로그에 기록됨
api = pyheroapi.connect("key", "secret")
price = api.stock("005930").current_price
```

## 📚 예제

- [`examples/basic_usage.py`](examples/basic_usage.py) - 기본 API 사용법
- [`examples/easy_usage.py`](examples/easy_usage.py) - 쉬운 API 예제  
- [`examples/comprehensive_usage.py`](examples/comprehensive_usage.py) - 모든 기능 시연
- [`examples/etf_elw_example.py`](examples/etf_elw_example.py) - ETF/ELW 예제
- [`examples/token_example.py`](examples/token_example.py) - 인증 예제

## 🔧 환경 설정

### 샌드박스 vs 프로덕션
```python
# 샌드박스 (테스트용)
api = pyheroapi.connect("key", "secret", sandbox=True)

# 프로덕션 (실제 거래)
api = pyheroapi.connect("key", "secret", sandbox=False)
```

### API 키 발급
1. [키움 REST API](https://openapi.kiwoom.com/) 방문
2. 계정 생성 및 로그인
3. 새 애플리케이션 등록
4. APP KEY와 SECRET KEY 발급
5. API 권한 설정

## 🎯 모범 사례

### 효율적인 데이터 수집
```python
# ✅ 좋은 예: 캐싱 활용
samsung = api.stock("005930")
price = samsung.current_price     # API 호출
quote = samsung.quote            # 캐시에서 가져옴 (빠름)

# ❌ 나쁜 예: 반복적인 객체 생성
price1 = api.stock("005930").current_price  # API 호출
price2 = api.stock("005930").current_price  # 또 다른 API 호출
```

### 안전한 거래
```python
# 주문 전 계좌 확인
account = api.account("account_number")
available = account.balance['available_balance']

if available >= 75000 * 10:  # 충분한 잔고 확인
    result = api.trading.buy("005930", 10, 75000)
    if result['success']:
        print(f"주문 성공: {result['order_number']}")
    else:
        print(f"주문 실패: {result['error']}")
```

### 포지션 관리
```python
# 현재 포지션 확인
positions = account.positions
samsung_position = next(
    (pos for pos in positions if pos['symbol'] == '005930'), 
    None
)

if samsung_position:
    quantity = samsung_position['quantity']
    avg_price = samsung_position['average_price']
    current_price = api.stock("005930").current_price
    
    # 수익률 계산
    return_rate = (current_price - avg_price) / avg_price * 100
    print(f"삼성전자 수익률: {return_rate:.2f}%")
```

## 🚨 중요 사항

### 주의사항
- 📊 **샌드박스 먼저**: 실제 거래 전에 항상 샌드박스에서 테스트
- 🔐 **API 키 보안**: 코드에 하드코딩하지 말고 환경변수 사용
- 💰 **주문 확인**: 모든 거래 주문은 신중하게 검토
- 📈 **시장 시간**: API는 장 시간에만 실시간 데이터 제공

### 제한사항
- 🕐 **API 제한**: 초당 요청 수 제한 있음 (자동 처리됨)
- 📱 **장 시간**: 일부 기능은 장 시간에만 사용 가능
- 🔍 **데이터 지연**: 실시간 데이터에 약간의 지연 있을 수 있음

## 🤝 기여

기여를 환영합니다! 다음과 같이 참여하세요:

1. 저장소 포크
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 라이선스가 부여됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🆘 지원

- 📖 **문서**: [완전한 API 문서](docs/)
- 🐛 **버그 리포트**: [GitHub Issues](https://github.com/gejyn14/pyheroapi/issues)
- 💡 **기능 요청**: [GitHub Discussions](https://github.com/gejyn14/pyheroapi/discussions)
- 📧 **이메일**: support@pyheroapi.com

---

**⚠️ 면책조항**: 이 라이브러리는 교육 및 개발 목적으로 제공됩니다. 실제 거래에서 발생하는 손실에 대해서는 책임지지 않습니다. 거래 시 주의하시기 바랍니다.
