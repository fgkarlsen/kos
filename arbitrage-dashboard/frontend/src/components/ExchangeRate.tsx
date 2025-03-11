"use client";

import { useState, useEffect } from "react";

export default function ExchangeRate() {
  const [exchangeRate, setExchangeRate] = useState<number | null>(null);

  // 업비트에서 USDT/KRW 환율 가져오는 함수
  const fetchUpbitExchangeRate = async () => {
    try {
      const res = await fetch("https://api.upbit.com/v1/ticker?markets=USDT-KRW");
      const data = await res.json();

      if (data.length > 0 && data[0].trade_price) {
        setExchangeRate(data[0].trade_price); // 현재 거래 가격을 환율로 설정
      } else {
        console.error("업비트 환율 데이터를 가져오지 못했습니다:", data);
      }
    } catch (error) {
      console.error("업비트 API 호출 중 오류 발생:", error);
    }
  };

  useEffect(() => {
    fetchUpbitExchangeRate(); // 최초 실행
    const interval = setInterval(fetchUpbitExchangeRate, 5000); // 5초마다 갱신
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4 border rounded-lg shadow-md bg-white">
      <h2 className="text-xl font-semibold mb-2">실시간 환율 (업비트)</h2>
      {exchangeRate ? (
        <p className="text-2xl font-bold text-blue-600">{exchangeRate.toLocaleString()} KRW/USDT</p>
      ) : (
        <p className="text-gray-500">환율 데이터를 불러오는 중...</p>
      )}
    </div>
  );
}
