from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query

import httpx

app = FastAPI()

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
