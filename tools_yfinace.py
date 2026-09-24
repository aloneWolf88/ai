from datetime import datetime
from zoneinfo import ZoneInfo  
import pandas as pd
import yfinance as yf

def get_current_time(timezone: str = "Asia/Seoul"):
    """지정한 타임존을 기준으로 현재 날짜, 시간, 요일을 반환합니다.

    잘못된 타임존이 입력되면 안전하게 기본값(Asia/Seoul)으로 동작합니다.
    """
    try:
        tz = ZoneInfo(timezone)
        used_tz = timezone
    except Exception:
        # LLM이 이상한 타임존 문자열을 보냈을 때 안전하게 fallback
        tz = ZoneInfo("Asia/Seoul")
        used_tz = "Asia/Seoul (잘못된 타임존으로 기본값 적용됨)"

    now = datetime.now(tz)

    # 주식 분석을 위해 요일(%A: Monday 등)을 함께 제공
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S (%A)")
    result = f"{formatted_time} [{used_tz}]"

    print(result)
    return result

def get_yf_stock_info(ticker: str):
    """
`   종목 코드(Ticker)를 입력받아 기본 재무 및 주가 정보를 반환
    """
    stock = yf.Ticker(ticker)
    info = stock.info # 사전(dict) 형태로 주식의 모든 상세 정보 수집

    # 52주최고/최저(없을경우 기본값)
    high_52 = info.get("fiftyTwoWeekHigh", "-")
    low_52 = info.get("fiftyTwoWeekLow", "-")
    result = {
        "종목명": [info.get("longName", ticker)],
        "통화": [info.get("currency", "USD")],
        "현재가": [
            info.get("currentPrice", info.get("regularMarketPrice", "정보없음"))
        ],
        "목표주가": [info.get("targetMeanPrice", "정보없음")],
        "52주최고/최저": [f"{high_52} / {low_52}"],
        "EPS(주당순이익)": [
            info.get("trailingEps", "정보없음")
        ],  # <-- EPS 추가
        "PER(주가수익비율)": [
            info.get("trailingPE", "정보없음")
        ],  # <-- PER
        "애널리스트의견": [info.get("recommendationKey", "정보없음")],
        "시가총액": [info.get("marketCap", "정보없음")],
    }
    result_d = pd.DataFrame(result)
    result_md = result_d.to_markdown(index=False)
    print(result_md)
    return result_md

def get_yf_stock_history(ticker: str, period: str):
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)

    # 데이터가 비어있을 때 예외 처리
    if history.empty:
        return "조회된 주가 데이터가 없습니다. 티커를 확인해주세요."

    # 1. 꼭 필요한 핵심 컬럼만 필터링
    core_cols = [
        col
        for col in ["Open", "High", "Low", "Close", "Volume"]
        if col in history.columns
    ]
    history = history[core_cols]

    # 2. 소수점 둘째 자리로 정리 (가독성 향상 & 토큰 절약)
    history = history.round(2)

    # 3. 토큰 폭탄 방지: 데이터가 너무 많으면 최근 30~60거래일만 전달
    if len(history) > 30:
        history = history.tail(30)

    history_md = history.to_markdown()
    print(history_md)
    return history_md

def get_yf_stock_recommendations(ticker: str):
    """
    최근 3~4개월간 분석가들의 매수/매도 추천 현황을 안전하게 가져옵니다.
    """
    stock = yf.Ticker(ticker)
    
    try:
        recommendations = stock.recommendations
    except Exception as e:
        return f"{ticker}의 투자의견 데이터를 불러오는 중 오류 발생: {e}"

    # 1. None이거나 비어있는 경우 방어 (AttributeError 방지)
    if recommendations is None or (hasattr(recommendations, 'empty') and recommendations.empty):
        return f"'{ticker}' 종목에 대한 애널리스트 투자의견 데이터가 존재하지 않습니다."

    # 2. 데이터가 너무 많을 경우 최근 4개 주기(기간)만 유지 (토큰 절약)
    if len(recommendations) > 4:
        recommendations = recommendations.tail(4)

    # 3. 마크다운 변환 및 반환
    recommendations_md = recommendations.to_markdown()
    print(recommendations_md)
    return recommendations_md


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "지정한 타임존의 현재 날짜, 시간, 요일을 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "타임존 문자열. 한국 주식: 'Asia/Seoul', 미국 주식: 'America/New_York' (생략 시 기본값: Asia/Seoul)",
                    },
                },
                "required": [],  # LLM이 생략해도 안전하게 기본값 사용
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_info",
            "description": "해당 종목의 기업 개요, 현재가, 밸류에이션(PER/EPS) 등 기본 재무 정보를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "조회할 종목 티커 (예: 미국 AAPL, TSLA / 한국 005930.KS, 035720.KQ)",
                    },
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_history",
            "description": "해당 종목의 최근 주가 차트 데이터(OHLCV)를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "조회할 종목 티커 (예: AAPL, 코스피 지수는 ^KS11)",
                    },
                    "period": {
                        "type": "string",
                        "description": "조회할 기간 (일주일은 5d)",
                        "enum": [
                            "1d",
                            "5d",
                            "1mo",
                            "1y",
                        ],  # 허용된 값 외 다른 문자열 입력 방지
                    },
                },
                "required": ["ticker", "period"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_recommendations",
            "description": "해당 종목에 대한 애널리스트들의 최근 매수/매도 투자의견 및 목표주가 추세를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "조회할 종목 티커 (예: AAPL, NVDA)",
                    },
                },
                "required": ["ticker"],
            },
        },
    },
]

if __name__ == "__main__":
    print("=== 1. 현재 시간 조회 테스트 ===")
    get_current_time()  # 기본 서울
    get_current_time("America/New_York")  # 뉴욕 시간

    print("\n=== 2. 종목 기본 정보 조회 테스트 ===")
    get_yf_stock_info("AAPL")

    print("\n=== 3. 주가 히스토리 조회 테스트 ===")
    get_yf_stock_history("AAPL", "5d")

    print("\n=== 4. 애널리스트 투자의견 조회 테스트 ===")
    get_yf_stock_recommendations("AAPL")
  