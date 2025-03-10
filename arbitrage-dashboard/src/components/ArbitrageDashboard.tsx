"use client";

import { useEffect, useState, useRef } from "react";

export default function ArbitrageDashboard() {
  const [upbitPrice, setUpbitPrice] = useState(0);
  const [binancePrice, setBinancePrice] = useState(0);
  const [exchangeRate, setExchangeRate] = useState(1300);
  const [binanceUsdPrice, setBinanceUsdPrice] = useState(0);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  
  // 최신 환율을 참조하기 위한 ref
  const exchangeRateRef = useRef(exchangeRate);
  
  // 환율이 변경될 때마다 ref 업데이트
  useEffect(() => {
    exchangeRateRef.current = exchangeRate;
    // 바이낸스 USD 가격이 있으면 KRW 가격 재계산
    if (binanceUsdPrice > 0) {
      setBinancePrice(binanceUsdPrice * exchangeRate);
    }
  }, [exchangeRate, binanceUsdPrice]);
  
  useEffect(() => {
    const upbitSocket = new WebSocket("wss://api.upbit.com/websocket/v1");
    const binanceSocket = new WebSocket("wss://stream.binance.com:9443/ws/xrpusdt@trade");
    
    // 업비트 USDT/KRW 환율 가져오기
    const fetchExchangeRate = async () => {
      try {
        const res = await fetch("https://api.upbit.com/v1/ticker?markets=KRW-USDT");
        const data = await res.json();
        if (data.length > 0 && data[0].trade_price) {
          console.log("환율 갱신:", data[0].trade_price);
          setExchangeRate(data[0].trade_price);
        }
      } catch (error) {
        console.error("환율 데이터를 가져오는 중 오류 발생:", error);
      }
    };
    
    // 페이지 로드 시 업비트 가격도 API로 가져오기
    const fetchUpbitPrice = async () => {
      try {
        const res = await fetch("https://api.upbit.com/v1/ticker?markets=KRW-XRP");
        const data = await res.json();
        if (data.length > 0 && data[0].trade_price) {
          console.log("업비트 초기 가격:", data[0].trade_price);
          setUpbitPrice(data[0].trade_price);
        }
      } catch (error) {
        console.error("업비트 가격 데이터를 가져오는 중 오류 발생:", error);
      }
    };
    
    fetchExchangeRate();
    fetchUpbitPrice();
    
    const exchangeInterval = setInterval(fetchExchangeRate, 10000); // 10초마다 환율 갱신
    
    upbitSocket.onopen = () => {
      console.log("업비트 웹소켓 연결됨");
      const subscribeMsg = JSON.stringify([
        { ticket: "test" }, 
        { type: "ticker", codes: ["KRW-XRP"] }
      ]);
      console.log("업비트 구독 메시지:", subscribeMsg);
      upbitSocket.send(subscribeMsg);
    };
    
    upbitSocket.onmessage = (event) => {
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const parsedData = JSON.parse(reader.result);
          console.log("업비트 데이터 수신:", parsedData);
          
          if (parsedData && parsedData.trade_price) {
            console.log("업비트 가격 갱신:", parsedData.trade_price);
            setUpbitPrice(parsedData.trade_price);
            setLastUpdate(new Date());
          }
        } catch (error) {
          console.error("업비트 데이터 파싱 오류:", error, reader.result);
        }
      };
      
      if (event.data instanceof Blob) {
        reader.readAsText(event.data);
      } else {
        try {
          const parsedData = JSON.parse(event.data);
          console.log("업비트 데이터 수신 (텍스트):", parsedData);
          
          if (parsedData && parsedData.trade_price) {
            console.log("업비트 가격 갱신:", parsedData.trade_price);
            setUpbitPrice(parsedData.trade_price);
            setLastUpdate(new Date());
          }
        } catch (error) {
          console.error("업비트 데이터 파싱 오류 (텍스트):", error);
        }
      }
    };
    
    binanceSocket.onopen = () => {
      console.log("바이낸스 웹소켓 연결됨");
    };
    
    binanceSocket.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data);
        if (parsedData && parsedData.p) {
          const usdPrice = parseFloat(parsedData.p);
          setBinanceUsdPrice(usdPrice);
          setBinancePrice(usdPrice * exchangeRateRef.current);
          setLastUpdate(new Date());
        }
      } catch (error) {
        console.error("바이낸스 데이터 파싱 오류:", error);
      }
    };
    
    return () => {
      clearInterval(exchangeInterval);
      upbitSocket.close();
      binanceSocket.close();
    };
  }, []);
  
  const arbitrage = upbitPrice && binancePrice ? ((upbitPrice - binancePrice) / binancePrice) * 100 : 0;
  
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
      <div className="text-sm text-gray-500 mt-2">
        마지막 업데이트: {lastUpdate.toLocaleTimeString()}
      </div>
      <button 
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        onClick={() => window.location.reload()}
      >
        새로고침
      </button>
    </div>
  );
}