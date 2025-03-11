"use client";
import { useEffect, useState, useRef } from "react";

export default function ArbitrageDashboard() {
  const [upbitPrice, setUpbitPrice] = useState(0);
  const [binancePrice, setBinancePrice] = useState(0);
  const [exchangeRate, setExchangeRate] = useState(1300);
  const [binanceUsdPrice, setBinanceUsdPrice] = useState(0);
  const [lastUpdate, setLastUpdate] = useState('');
  const [isClient, setIsClient] = useState(false);
  const exchangeRateRef = useRef(exchangeRate);
  const [threshold, setThreshold] = useState(1.0); 
  const [recordHistory, setRecordHistory] = useState([]); 

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    exchangeRateRef.current = exchangeRate;
    if (binanceUsdPrice > 0) {
      setBinancePrice(binanceUsdPrice * exchangeRate);
    }
  }, [exchangeRate, binanceUsdPrice]);

  useEffect(() => {
    const upbitSocket = new WebSocket("wss://api.upbit.com/websocket/v1");
    const binanceSocket = new WebSocket("wss://stream.binance.com:9443/ws/xrpusdt@trade");

    const fetchExchangeRate = async () => {
      try {
        const res = await fetch("https://crispy-xylophone-7v95jpqjw53pjv9-8000.app.github.dev/exchange-rate");
        const data = await res.json();
        if (data.length > 0 && data[0].trade_price) {
          setExchangeRate(data[0].trade_price);
        }
      } catch (error) {
        console.error("환율 데이터 오류:", error);
      }
    };

    const fetchUpbitPrice = async () => {
      try {
        const res = await fetch("http://localhost:8000/upbit-price");
        const data = await res.json();
        if (data.length > 0 && data[0].trade_price) {
          setUpbitPrice(data[0].trade_price);
        }
      } catch (error) {
        console.error("업비트 가격 데이터 오류:", error);
      }
    };

    fetchExchangeRate();
    fetchUpbitPrice();
    const exchangeInterval = setInterval(fetchExchangeRate, 900000);

    upbitSocket.onopen = () => {
      upbitSocket.send(JSON.stringify([{ ticket: "test" }, { type: "ticker", codes: ["KRW-XRP"] }]));
    };

    upbitSocket.onmessage = (event) => {
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const parsedData = JSON.parse(reader.result as string);
          if (parsedData && parsedData.trade_price) {
            setUpbitPrice(parsedData.trade_price);
            setLastUpdate(new Date().toISOString());
          }
        } catch (error) {
          console.error("업비트 데이터 오류:", error);
        }
      };
      reader.readAsText(event.data);
    };

    binanceSocket.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data);
        if (parsedData && parsedData.p) {
          const usdPrice = parseFloat(parsedData.p);
          setBinanceUsdPrice(usdPrice);
          setBinancePrice(usdPrice * exchangeRateRef.current);
          setLastUpdate(new Date().toISOString());
        }
      } catch (error) {
        console.error("바이낸스 데이터 오류:", error);
      }
    };

    return () => {
      clearInterval(exchangeInterval);
      upbitSocket.close();
      binanceSocket.close();
    };
  }, []);

  const arbitrage = upbitPrice && binancePrice ? ((upbitPrice - binancePrice) / binancePrice) * 100 : 0;

  useEffect(() => {
    if (Math.abs(arbitrage) >= threshold) {
      const newRecord = {
        time: new Date().toLocaleTimeString(),
        upbit: upbitPrice,
        binance: binancePrice,
        arbitrage: arbitrage.toFixed(2),
      };
      setRecordHistory((prev) => [...prev, newRecord]);
    }
  }, [arbitrage, threshold]);

  const formattedTime = isClient && lastUpdate ? new Date(lastUpdate).toLocaleTimeString('en-US', { hour12: false }) : "";

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">리플 차익거래 대시보드</h1>
      <div>업비트 가격: {upbitPrice.toLocaleString()} KRW</div>
      <div>바이낸스 가격: {binancePrice.toLocaleString()} KRW</div>
      <div>바이낸스 USD 가격: ${binanceUsdPrice.toFixed(4)}</div>
      <div>현재 환율 (USDT/KRW): {exchangeRate.toFixed(2)}</div>
      <div className={`mt-2 text-lg ${arbitrage > 0 ? "text-green-500" : "text-red-500"}`}>
        차익률: {arbitrage.toFixed(2)}%
      </div>

      {isClient && (
        <div className="text-sm text-gray-500 mt-2">마지막 업데이트: {formattedTime}</div>
      )}

      <div className="mt-4">
        <label className="block text-sm font-medium">기준 차익률 설정 (%)</label>
        <input
          type="number"
          value={threshold}
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
          className="border px-2 py-1 rounded w-20 mt-1"
        />
      </div>

      <button className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600" onClick={() => window.location.reload()}>
        새로고침
      </button>
    </div>
  );
}
