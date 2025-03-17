from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
import asyncio
import json

import httpx

app = FastAPI()

# 거래소 및 코인 설정
exchanges = ["upbit", "bithumb", "binance", "bybit", "kucoin", "okx", "mexc"]
coins = ["XRP", "TRX", "LTC"]

# 거래소 API 엔드포인트 예제
exchange_urls = {
    "upbit": "wss://api.upbit.com/websocket/v1",
    "bithumb": "wss://pubwss.bithumb.com/pub/ws",
    "binance": "wss://stream.binance.com:9443/ws",
    "bybit": "wss://stream.bybit.com/v5/public/spot",
    "kucoin": "wss://ws-api.kucoin.com/endpoint",
    "okx": "wss://ws.okx.com:8443/ws/v5/public",
    "mexc": "wss://wbs.mexc.com/ws"
}

# 실시간 가격 저장
prices = {exchange: {coin: 0.0 for coin in coins} for exchange in exchanges}


origins = [
    "https://crispy-xylophone-7v95jpqjw53pjv9-3000.app.github.dev",
    "https://crispy-xylophone-7v95jpqjw53pjv9-8000.app.github.dev",
    "http://localhost:3000",
]

# CORS 설정 (모든 도메인 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 보안을 위해 실제 도메인만 허용하는 것이 좋음
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXCHANGES = {
    "upbit": "https://api.upbit.com/v1/market/all",
    "binance": "https://api.binance.com/api/v3/exchangeInfo",
    "bybit": "https://api.bybit.com/v2/public/symbols",
    "kucoin": "https://api.kucoin.com/api/v1/symbols",
    "okx": "https://www.okx.com/api/v5/market/tickers?instType=SPOT",
    "mexc": "https://api.mexc.com/api/v3/exchangeInfo",
    "bithumb": "https://api.bithumb.com/public/ticker/ALL_KRW"
}

cached_coins = {}

# 거래소 웹소켓 연결 함수
async def connect_exchange_ws(exchange, coin):
    url = exchange_urls[exchange]
    try:
        async with asyncio.open_connection(url) as (reader, writer):
            if exchange == "upbit":
                payload = json.dumps([{"ticket": "test"}, {"type": "ticker", "codes": [f"KRW-{coin}"]}])
            elif exchange == "bithumb":
                payload = json.dumps({"type": "ticker", "symbols": [f"{coin}_KRW"], "tickTypes": ["1M"]})
            elif exchange == "binance":
                payload = f"{{\"method\": \"SUBSCRIBE\", \"params\": [\"{coin.lower()}usdt@trade\"], \"id\": 1}}"
            else:
                payload = json.dumps({"subscribe": f"{coin}_USDT"})
            
            writer.write(payload.encode())
            await writer.drain()

            while True:
                data = await reader.read(1024)
                try:
                    message = json.loads(data.decode())
                    if exchange == "upbit" and "trade_price" in message:
                        prices[exchange][coin] = message["trade_price"]
                    elif exchange == "bithumb" and "content" in message:
                        prices[exchange][coin] = float(message["content"]["closePrice"])
                    elif exchange == "binance" and "p" in message:
                        prices[exchange][coin] = float(message["p"])
                    
                    print(f"[{exchange}] {coin} 가격: {prices[exchange][coin]}")
                except Exception as e:
                    print(f"데이터 처리 오류: {e}")
                    continue
    except Exception as e:
        print(f"{exchange} 연결 실패: {e}")

# 각 거래소와 코인에 대해 웹소켓 연결 시작
@app.on_event("startup")
async def start_ws_connections():
    tasks = []
    for exchange in exchanges:
        for coin in coins:
            tasks.append(connect_exchange_ws(exchange, coin))
    asyncio.create_task(asyncio.gather(*tasks))

# 프론트엔드와 웹소켓 통신
@app.websocket("/ws/arbitrage")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 실시간 차익률 계산
            result = []
            for coin in coins:
                for i, ex1 in enumerate(exchanges):
                    for j, ex2 in enumerate(exchanges):
                        if i >= j:  # 중복 계산 방지
                            continue
                        price1 = prices[ex1][coin]
                        price2 = prices[ex2][coin]
                        if price1 > 0 and price2 > 0:
                            spread = ((price1 - price2) / price2) * 100
                            result.append({
                                "coin": coin,
                                "exchange1": ex1,
                                "exchange2": ex2,
                                "price1": price1,
                                "price2": price2,
                                "spread": round(spread, 2)
                            })
            # 프론트엔드로 데이터 전송
            await websocket.send_json(result)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("클라이언트 연결 해제")


@app.get("/get-coins")
async def get_coins():
    global cached_coins
    results = {}
    for exchange, url in EXCHANGES.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                data = response.json()
                
                if exchange == "upbit":
                    results[exchange] = [item['market'] for item in data if 'KRW-' in item['market']]
                elif exchange == "binance" or exchange == "mexc":
                    results[exchange] = [item['symbol'] for item in data['symbols']]
                elif exchange == "bybit":
                    results[exchange] = [item['name'] for item in data['result']]
                elif exchange == "kucoin":
                    results[exchange] = [item['symbol'] for item in data['data']]
                elif exchange == "okx":
                    results[exchange] = [item['instId'] for item in data['data']]
                elif exchange == "bithumb":
                    results[exchange] = list(data['data'].keys())
        
        except Exception as e:
            print(f"{exchange} 에러: {e}")

    cached_coins = results
    return results

@app.get("/get-price")
async def get_price(exchange: str = Query(...), coin: str = Query(...)):
    price_url = ""

    if exchange == "upbit":
        price_url = f"https://api.upbit.com/v1/ticker?markets={coin}"
    elif exchange == "binance":
        price_url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}"
    elif exchange == "bybit":
        price_url = f"https://api.bybit.com/v2/public/tickers?symbol={coin}"
    elif exchange == "kucoin":
        price_url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={coin}"
    elif exchange == "okx":
        price_url = f"https://www.okx.com/api/v5/market/ticker?instId={coin}"
    elif exchange == "mexc":
        price_url = f"https://api.mexc.com/api/v3/ticker/price?symbol={coin}"
    elif exchange == "bithumb":
        price_url = f"https://api.bithumb.com/public/ticker/{coin}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(price_url)
            data = response.json()
            
            if exchange == "upbit":
                return {"price": data[0]["trade_price"]}
            elif exchange == "binance" or exchange == "mexc":
                return {"price": float(data['price'])}
            elif exchange == "bybit":
                return {"price": float(data['result'][0]['last_price'])}
            elif exchange == "kucoin":
                return {"price": float(data['data']['price'])}
            elif exchange == "okx":
                return {"price": float(data['data'][0]['last'])}
            elif exchange == "bithumb":
                return {"price": float(data['data']['closing_price'])}
    
    except Exception as e:
        return {"error": f"가격 조회 실패: {e}"}



UPBIT_TICKER_URL = "https://api.upbit.com/v1/ticker?markets=KRW-XRP"
UPBIT_USDT_URL = "https://api.upbit.com/v1/ticker?markets=KRW-USDT"

@app.get("/upbit-price")
async def get_upbit_price():
    async with httpx.AsyncClient() as client:
        response = await client.get(UPBIT_TICKER_URL)
        return response.json()

@app.get("/exchange-rate")
async def get_exchange_rate():
    async with httpx.AsyncClient() as client:
        response = await client.get(UPBIT_USDT_URL)
        return response.json()
