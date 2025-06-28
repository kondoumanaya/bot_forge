import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Activity, TrendingUp, TrendingDown } from "lucide-react";

interface TickData {
  id: number;
  exchange: string;
  symbol: string;
  price: number;
  volume: number;
  side: string;
  timestamp: string;
}

interface OrderBookData {
  id: number;
  exchange: string;
  symbol: string;
  bids: [number, number][];
  asks: [number, number][];
  timestamp: string;
}

interface DataPreviewProps {
  exchange: string;
  symbol: string;
  timeframe: string;
  isCollecting: boolean;
}

export default function DataPreview({
  exchange,
  symbol,
  timeframe,
  isCollecting,
}: DataPreviewProps) {
  const [tickData, setTickData] = useState<TickData[]>([]);
  const [orderBookData, setOrderBookData] = useState<OrderBookData | null>(
    null
  );
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [lastPrice, setLastPrice] = useState<number>(0);
  const [priceChange, setPriceChange] = useState<number>(0);

  useEffect(() => {
    fetchTickData();
    fetchOrderBookData();

    if (isCollecting) {
      const ws = new WebSocket(`ws://localhost:8000/ws/${exchange}/${symbol}`);

      ws.onopen = () => {
        console.log("WebSocket connected");
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        if (message.type === "tick_data") {
          const newTick = message.data;
          setTickData((prev) => [newTick, ...prev.slice(0, 99)]); // Keep last 100 ticks

          if (lastPrice > 0) {
            setPriceChange(newTick.price - lastPrice);
          }
          setLastPrice(newTick.price);
        } else if (message.type === "orderbook_data") {
          setOrderBookData(message.data);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      setWsConnection(ws);

      return () => {
        ws.close();
      };
    }
  }, [exchange, symbol, isCollecting, lastPrice]);

  const fetchTickData = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/data/tick?exchange=${exchange}&symbol=${symbol}&limit=50`
      );
      if (response.ok) {
        const data = await response.json();
        setTickData(data);
        if (data.length > 0) {
          setLastPrice(data[0].price);
        }
      }
    } catch (error) {
      console.error("Failed to fetch tick data:", error);
    }
  };

  const fetchOrderBookData = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/data/orderbook?exchange=${exchange}&symbol=${symbol}&limit=1`
      );
      if (response.ok) {
        const data = await response.json();
        if (data.length > 0) {
          setOrderBookData(data[0]);
        }
      }
    } catch (error) {
      console.error("Failed to fetch orderbook data:", error);
    }
  };

  const chartData = tickData
    .slice(0, 20)
    .reverse()
    .map((tick, index) => ({
      time: new Date(tick.timestamp).toLocaleTimeString(),
      price: tick.price,
      volume: tick.volume,
    }));

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Live Price Data</span>
            <Badge variant={isCollecting ? "default" : "secondary"}>
              {isCollecting ? "Live" : "Paused"}
            </Badge>
          </CardTitle>
          <CardDescription>
            Real-time tick data for {symbol} on {exchange.toUpperCase()}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-2xl font-bold">
                  ¥{lastPrice.toLocaleString()}
                </p>
                <div className="flex items-center space-x-2">
                  {priceChange > 0 ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : priceChange < 0 ? (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  ) : (
                    <Activity className="h-4 w-4 text-gray-500" />
                  )}
                  <span
                    className={`text-sm ${
                      priceChange > 0
                        ? "text-green-500"
                        : priceChange < 0
                        ? "text-red-500"
                        : "text-gray-500"
                    }`}
                  >
                    {priceChange > 0 ? "+" : ""}
                    {priceChange.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke="#8884d8"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Order Book</CardTitle>
          <CardDescription>Current bid/ask spread for {symbol}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium text-green-600 mb-2">
                  Bids
                </h4>
                <ScrollArea className="h-[200px]">
                  <div className="space-y-1">
                    {orderBookData?.bids.slice(0, 10).map((bid, index) => (
                      <div key={index} className="flex justify-between text-sm">
                        <span className="text-green-600">
                          ¥{bid[0].toLocaleString()}
                        </span>
                        <span className="text-muted-foreground">{bid[1]}</span>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>

              <div>
                <h4 className="text-sm font-medium text-red-600 mb-2">Asks</h4>
                <ScrollArea className="h-[200px]">
                  <div className="space-y-1">
                    {orderBookData?.asks.slice(0, 10).map((ask, index) => (
                      <div key={index} className="flex justify-between text-sm">
                        <span className="text-red-600">
                          ¥{ask[0].toLocaleString()}
                        </span>
                        <span className="text-muted-foreground">{ask[1]}</span>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Recent Trades</CardTitle>
          <CardDescription>
            Latest tick data from {exchange.toUpperCase()}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[300px]">
            <div className="space-y-2">
              {tickData.map((tick) => (
                <div
                  key={tick.id}
                  className="flex items-center justify-between p-2 rounded-lg border"
                >
                  <div className="flex items-center space-x-4">
                    <Badge
                      variant={tick.side === "buy" ? "default" : "secondary"}
                    >
                      {tick.side.toUpperCase()}
                    </Badge>
                    <span className="font-mono">
                      ¥{tick.price.toLocaleString()}
                    </span>
                    <span className="text-muted-foreground">{tick.volume}</span>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {new Date(tick.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
