import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { Textarea } from "@/components/ui/textarea";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
} from "recharts";
import { Brain, TrendingUp, BarChart3, Download, Sparkles } from "lucide-react";

interface AnalysisPanelProps {
  exchange: string;
  symbol: string;
}

interface FeatureData {
  timestamp: string;
  price: number;
  volume: number;
  rsi: number;
  macd: number;
  bollinger_upper: number;
  bollinger_lower: number;
}

export default function AnalysisPanel({
  exchange,
  symbol,
}: AnalysisPanelProps) {
  const [analysisType, setAnalysisType] = useState<string>(
    "technical_indicators"
  );
  const [timeRange, setTimeRange] = useState<string>("7d");
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [features, setFeatures] = useState<FeatureData[]>([]);
  const [o3Analysis, setO3Analysis] = useState<string>("");
  const [mlInsights, setMlInsights] = useState<any>(null);

  useEffect(() => {
    generateSampleFeatures();
  }, [exchange, symbol, timeRange]);

  const generateSampleFeatures = () => {
    const sampleData: FeatureData[] = [];
    const basePrice = 50000;

    for (let i = 0; i < 100; i++) {
      const timestamp = new Date(
        Date.now() - (100 - i) * 3600000
      ).toISOString();
      const price = basePrice + Math.sin(i * 0.1) * 2000 + Math.random() * 1000;
      const volume = 0.5 + Math.random() * 2;
      const rsi = 30 + Math.random() * 40;
      const macd = -10 + Math.random() * 20;

      sampleData.push({
        timestamp,
        price,
        volume,
        rsi,
        macd,
        bollinger_upper: price + 1000,
        bollinger_lower: price - 1000,
      });
    }

    setFeatures(sampleData);
  };

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);

    setTimeout(() => {
      const analysis = `
# Market Analysis for ${symbol} on ${exchange.toUpperCase()}
## Technical Indicators Summary
- **RSI**: Currently showing ${features[features.length - 1]?.rsi.toFixed(
        1
      )} (neutral territory)
- **MACD**: ${
        features[features.length - 1]?.macd > 0 ? "Bullish" : "Bearish"
      } signal detected
- **Bollinger Bands**: Price is ${
        features[features.length - 1]?.price >
        features[features.length - 1]?.bollinger_upper
          ? "above upper band (overbought)"
          : features[features.length - 1]?.price <
            features[features.length - 1]?.bollinger_lower
          ? "below lower band (oversold)"
          : "within normal range"
      }
## Pattern Recognition
- Identified potential support level at ¥${(
        Math.min(...features.map((f) => f.price)) + 500
      ).toFixed(0)}
- Resistance level observed at ¥${(
        Math.max(...features.map((f) => f.price)) - 500
      ).toFixed(0)}
- Volume profile suggests ${
        Math.random() > 0.5 ? "accumulation" : "distribution"
      } phase
## ML Model Recommendations
- **Trend Prediction**: ${
        Math.random() > 0.5 ? "Upward" : "Sideways"
      } movement expected in next 24h
- **Volatility Forecast**: ${
        Math.random() > 0.5 ? "High" : "Low"
      } volatility anticipated
- **Entry Signal Strength**: ${(Math.random() * 10).toFixed(1)}/10
## Risk Assessment
- Current market conditions: ${Math.random() > 0.5 ? "Favorable" : "Cautious"}
- Recommended position size: ${(Math.random() * 5 + 1).toFixed(1)}% of portfolio
- Stop-loss suggestion: ${(features[features.length - 1]?.price * 0.95).toFixed(
        0
      )}
      `;

      setO3Analysis(analysis);

      setMlInsights({
        trend_probability: Math.random(),
        volatility_score: Math.random() * 100,
        momentum_strength: Math.random() * 10,
        support_levels: [48000, 47500, 47000],
        resistance_levels: [52000, 52500, 53000],
      });

      setIsAnalyzing(false);
    }, 2000);
  };

  const handleExportAnalysis = () => {
    const exportData = {
      exchange,
      symbol,
      analysis_type: analysisType,
      time_range: timeRange,
      timestamp: new Date().toISOString(),
      features: features,
      o3_analysis: o3Analysis,
      ml_insights: mlInsights,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analysis_${exchange}_${symbol}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const correlationData = features.map((f) => ({
    price: f.price,
    volume: f.volume * 10000,
    rsi: f.rsi,
  }));

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>Market Analysis & ML Features</span>
          </CardTitle>
          <CardDescription>
            Generate features for machine learning models and o3 analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Analysis Type</label>
              <Select value={analysisType} onValueChange={setAnalysisType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="technical_indicators">
                    Technical Indicators
                  </SelectItem>
                  <SelectItem value="pattern_recognition">
                    Pattern Recognition
                  </SelectItem>
                  <SelectItem value="sentiment_analysis">
                    Sentiment Analysis
                  </SelectItem>
                  <SelectItem value="correlation_analysis">
                    Correlation Analysis
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Time Range</label>
              <Select value={timeRange} onValueChange={setTimeRange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1d">1 Day</SelectItem>
                  <SelectItem value="7d">7 Days</SelectItem>
                  <SelectItem value="30d">30 Days</SelectItem>
                  <SelectItem value="90d">90 Days</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Actions</label>
              <div className="flex space-x-2">
                <Button
                  onClick={handleRunAnalysis}
                  disabled={isAnalyzing}
                  className="flex-1"
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  {isAnalyzing ? "Analyzing..." : "Run o3 Analysis"}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Technical Indicators</CardTitle>
            <CardDescription>RSI, MACD, and Bollinger Bands</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={features.slice(-50)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={(value) =>
                      new Date(value).toLocaleDateString()
                    }
                  />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="rsi"
                    stroke="#8884d8"
                    strokeWidth={2}
                    name="RSI"
                  />
                  <Line
                    type="monotone"
                    dataKey="macd"
                    stroke="#82ca9d"
                    strokeWidth={2}
                    name="MACD"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Price vs Volume Correlation</CardTitle>
            <CardDescription>Scatter plot analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart data={correlationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="price" name="Price" />
                  <YAxis dataKey="volume" name="Volume" />
                  <Tooltip cursor={{ strokeDasharray: "3 3" }} />
                  <Scatter dataKey="volume" fill="#8884d8" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {mlInsights && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Trend Probability
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(mlInsights.trend_probability * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">
                Bullish trend likelihood
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Volatility Score
              </CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {mlInsights.volatility_score.toFixed(1)}
              </div>
              <p className="text-xs text-muted-foreground">
                Market volatility index
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Momentum</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {mlInsights.momentum_strength.toFixed(1)}/10
              </div>
              <p className="text-xs text-muted-foreground">
                Current momentum strength
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Export Analysis
              </CardTitle>
              <Download className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <Button
                onClick={handleExportAnalysis}
                size="sm"
                className="w-full"
              >
                <Download className="h-4 w-4 mr-2" />
                Export JSON
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {o3Analysis && (
        <Card>
          <CardHeader>
            <CardTitle>o3 Market Analysis</CardTitle>
            <CardDescription>
              AI-powered market insights and recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              value={o3Analysis}
              readOnly
              className="min-h-[400px] font-mono text-sm"
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
