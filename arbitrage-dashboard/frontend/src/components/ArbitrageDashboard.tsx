import { useEffect, useState } from "react";

const exchanges = ["upbit", "bithumb", "binance", "bybit", "kucoin", "okx", "mexc"];
const coins = ["XRP", "TRX", "LTC"];

export default function ArbitrageDashboard() {
  const [prices, setPrices] = useState({});
  const [bestArbitrage, setBestArbitrage] = useState(null);
  const [threshold, setThreshold] = useState(1.0);

  useEffect(() => {
    const sockets = {};

    exchanges.forEach((exchange) => {
      coins.forEach((coin) => {
        const socket = new WebSocket(`ws://localhost:8000/ws/${exchange}/${coin}`);
        socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          setPrices((prev) => ({
            ...prev,
            [`${exchange}-${coin}`]: data.price,
          }));
        };
        sockets[`${exchange}-${coin}`] = socket;
      });
    });

    return () => {
      Object.values(sockets).forEach((socket) => socket.close());
    };
  }, []);

  useEffect(() => {
    const arbitrages = [];

    coins.forEach((coin) => {
      exchanges.forEach((exchange1) => {
        exchanges.forEach((exchange2) => {
          if (exchange1 !== exchange2) {
            const price1 = prices[`${exchange1}-${coin}`];
            const price2 = prices[`${exchange2}-${coin}`];
            if (price1 && price2) {
              const spread = ((price1 - price2) / price2) * 100;
              if (spread >= threshold) {
                arbitrages.push({ coin, exchange1, exchange2, spread });
              }
            }
          }
        });
      });
    });

    if (arbitrages.length > 0) {
      const best = arbitrages.reduce((max, current) => (current.spread > max.spread ? current : max));
      setBestArbitrage(best);
    } else {
      setBestArbitrage(null);
    }
  }, [prices, threshold]);

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">거래소 간 차익거래 대시보드</h1>
      <div className="mb-4">
        <label className="block text-sm font-medium">기준 차익률 설정 (%)</label>
        <input
          type="number"
          value={threshold}
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
          className="border px-2 py-1 rounded w-20 mt-1"
        />
      </div>

      <h2 className="text-lg font-semibold mb-2">실시간 가격</h2>
      <div className="grid grid-cols-4 gap-2">
        {coins.map((coin) => (
          <div key={coin} className="p-2 border rounded">
            <h3 className="font-bold text-center">{coin}</h3>
            {exchanges.map((exchange) => (
              <div key={`${exchange}-${coin}`} className="text-center">
                {exchange.toUpperCase()}: {prices[`${exchange}-${coin}`]?.toLocaleString() || "-"} KRW
              </div>
            ))}
          </div>
        ))}
      </div>

      {bestArbitrage && (
        <div className="mt-4 p-4 border rounded bg-green-100">
          <h2 className="text-lg font-semibold text-green-700">최고 차익 거래 기회 발견!</h2>
          <p>{`${bestArbitrage.coin} - ${bestArbitrage.exchange1} ➜ ${bestArbitrage.exchange2}`}</p>
          <p className="text-green-500 font-bold">차익률: {bestArbitrage.spread.toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
}
