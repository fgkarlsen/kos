from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
