import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import {
  Play,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
} from "lucide-react";

interface BacktestResult {
  strategy_name: string;
  exchange: string;
  symbol: string;
  period: string;
  initial_balance: number;
  final_balance: number;
  total_return: number;
  max_drawdown: number;
  sharpe_ratio: number;
  total_trades: number;
  win_rate: number;
  status: string;
}

interface BacktestPanelProps {
  exchange: string;
  symbol: string;
}

export default function BacktestPanel({
  exchange,
  symbol,
}: BacktestPanelProps) {
  const [strategyName, setStrategyName] = useState<string>(
    "simple_ma_crossover"
  );
  const [initialBalance, setInitialBalance] = useState<number>(10000);
  const [startDate, setStartDate] = useState<string>("2024-01-01");
  const [endDate, setEndDate] = useState<string>("2024-12-31");
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [result, setResult] = useState<BacktestResult | null>(null);

  const handleRunBacktest = async () => {
    setIsRunning(true);
    setProgress(0);
    setResult(null);

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);

    try {
      const response = await fetch("http://localhost:8000/api/backtest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          strategy_name: strategyName,
          exchange: exchange,
          symbol: symbol,
          start_date: new Date(startDate).toISOString(),
          end_date: new Date(endDate).toISOString(),
          initial_balance: initialBalance,
          parameters: {},
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        setProgress(100);
      } else {
        throw new Error("Backtest failed");
      }
    } catch (error) {
      console.error("Backtest error:", error);
    } finally {
      clearInterval(progressInterval);
      setIsRunning(false);
    }
  };

  const performanceData = result
    ? [
        { month: "Jan", pnl: 500, drawdown: -200 },
        { month: "Feb", pnl: 800, drawdown: -150 },
        { month: "Mar", pnl: 600, drawdown: -300 },
        { month: "Apr", pnl: 1200, drawdown: -100 },
        { month: "May", pnl: 900, drawdown: -250 },
        { month: "Jun", pnl: 1500, drawdown: -80 },
      ]
    : [];

  const tradeDistribution = result
    ? [
        {
          type: "Wins",
          count: Math.floor(result.total_trades * result.win_rate),
        },
        {
          type: "Losses",
          count:
            result.total_trades -
            Math.floor(result.total_trades * result.win_rate),
        },
      ]
    : [];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Backtest Configuration</CardTitle>
          <CardDescription>
            Configure and run backtests for trading strategies
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="strategy">Strategy</Label>
              <Select value={strategyName} onValueChange={setStrategyName}>
                <SelectTrigger>
                  <SelectValue placeholder="Select strategy" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="simple_ma_crossover">
                    Simple MA Crossover
                  </SelectItem>
                  <SelectItem value="rsi_mean_reversion">
                    RSI Mean Reversion
                  </SelectItem>
                  <SelectItem value="bollinger_bands">
                    Bollinger Bands
                  </SelectItem>
                  <SelectItem value="momentum_strategy">
                    Momentum Strategy
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="balance">Initial Balance (¥)</Label>
              <Input
                id="balance"
                type="number"
                value={initialBalance}
                onChange={(e) => setInitialBalance(Number(e.target.value))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="start-date">Start Date</Label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="end-date">End Date</Label>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium">
                Target: {symbol} on {exchange.toUpperCase()}
              </p>
              <p className="text-sm text-muted-foreground">
                Period: {startDate} to {endDate}
              </p>
            </div>
            <Button onClick={handleRunBacktest} disabled={isRunning}>
              <Play className="h-4 w-4 mr-2" />
              {isRunning ? "Running..." : "Run Backtest"}
            </Button>
          </div>

          {isRunning && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Progress</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} />
            </div>
          )}
        </CardContent>
      </Card>

      {result && (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Return
                </CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  +{result.total_return.toFixed(1)}%
                </div>
                <p className="text-xs text-muted-foreground">
                  ¥
                  {(
                    result.final_balance - result.initial_balance
                  ).toLocaleString()}{" "}
                  profit
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Max Drawdown
                </CardTitle>
                <TrendingDown className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {result.max_drawdown.toFixed(1)}%
                </div>
                <p className="text-xs text-muted-foreground">
                  Maximum loss from peak
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Sharpe Ratio
                </CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {result.sharpe_ratio.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground">
                  Risk-adjusted return
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(result.win_rate * 100).toFixed(1)}%
                </div>
                <p className="text-xs text-muted-foreground">
                  {result.total_trades} total trades
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Performance Over Time</CardTitle>
                <CardDescription>
                  Monthly P&L and drawdown analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="pnl"
                        stroke="#22c55e"
                        strokeWidth={2}
                        name="P&L"
                      />
                      <Line
                        type="monotone"
                        dataKey="drawdown"
                        stroke="#ef4444"
                        strokeWidth={2}
                        name="Drawdown"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Trade Distribution</CardTitle>
                <CardDescription>Win/Loss ratio breakdown</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={tradeDistribution}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="type" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Backtest Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Strategy:</span>
                    <Badge variant="outline">{result.strategy_name}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Period:</span>
                    <span>{result.period}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Initial Balance:</span>
                    <span>¥{result.initial_balance.toLocaleString()}</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Final Balance:</span>
                    <span>¥{result.final_balance.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Trades:</span>
                    <span>{result.total_trades}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <Badge variant="default">{result.status}</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
