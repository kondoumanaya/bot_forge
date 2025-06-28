import { useState, useEffect } from "react";
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
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Download, Database, Trash2, Search } from "lucide-react";

interface DataStats {
  tick_data: {
    total_records: number;
    latest_timestamp: string | null;
  };
  orderbook_data: {
    total_records: number;
    latest_timestamp: string | null;
  };
  ohlc_data: {
    total_records: number;
    latest_timestamp: string | null;
  };
}

interface DataManagementProps {
  exchange: string;
  symbol: string;
}

export default function DataManagement({
  exchange,
  symbol,
}: DataManagementProps) {
  const [dataStats, setDataStats] = useState<DataStats | null>(null);
  const [exportFormat, setExportFormat] = useState<string>("csv");
  const [exportType, setExportType] = useState<string>("tick");
  const [startDate, setStartDate] = useState<Date | undefined>(
    new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  );
  const [endDate, setEndDate] = useState<Date | undefined>(new Date());
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>("");

  useEffect(() => {
    fetchDataStats();
  }, [exchange, symbol]);

  const fetchDataStats = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/data/stats?exchange=${exchange}&symbol=${symbol}`
      );
      if (response.ok) {
        const stats = await response.json();
        setDataStats(stats);
      }
    } catch (error) {
      console.error("Failed to fetch data stats:", error);
    }
  };

  const handleExportData = async () => {
    if (!startDate || !endDate) return;

    setIsExporting(true);
    try {
      const endpoint = exportFormat === "json" ? "export/json" : "export/csv";
      const response = await fetch(
        `http://localhost:8000/api/data/${endpoint}?exchange=${exchange}&symbol=${symbol}&data_type=${exportType}&start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`
      );

      if (response.ok) {
        const result = await response.json();

        const blob = new Blob(
          [
            exportFormat === "json"
              ? JSON.stringify(result.data, null, 2)
              : result.data,
          ],
          {
            type: exportFormat === "json" ? "application/json" : "text/csv",
          }
        );

        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${exchange}_${symbol}_${exportType}_${
          startDate.toISOString().split("T")[0]
        }_to_${endDate.toISOString().split("T")[0]}.${exportFormat}`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error("Export failed:", error);
    } finally {
      setIsExporting(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const getStorageInfo = (records: number) => {
    const estimatedSize = records * 0.1; // Rough estimate in KB
    if (estimatedSize >= 1024 * 1024)
      return `${(estimatedSize / (1024 * 1024)).toFixed(1)} GB`;
    if (estimatedSize >= 1024) return `${(estimatedSize / 1024).toFixed(1)} MB`;
    return `${estimatedSize.toFixed(1)} KB`;
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tick Data</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dataStats
                ? formatNumber(dataStats.tick_data.total_records)
                : "0"}
            </div>
            <p className="text-xs text-muted-foreground">
              {dataStats
                ? getStorageInfo(dataStats.tick_data.total_records)
                : "0 KB"}{" "}
              estimated
            </p>
            {dataStats?.tick_data.latest_timestamp && (
              <p className="text-xs text-muted-foreground mt-1">
                Latest:{" "}
                {new Date(
                  dataStats.tick_data.latest_timestamp
                ).toLocaleString()}
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Order Book</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dataStats
                ? formatNumber(dataStats.orderbook_data.total_records)
                : "0"}
            </div>
            <p className="text-xs text-muted-foreground">
              {dataStats
                ? getStorageInfo(dataStats.orderbook_data.total_records)
                : "0 KB"}{" "}
              estimated
            </p>
            {dataStats?.orderbook_data.latest_timestamp && (
              <p className="text-xs text-muted-foreground mt-1">
                Latest:{" "}
                {new Date(
                  dataStats.orderbook_data.latest_timestamp
                ).toLocaleString()}
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">OHLC Data</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dataStats
                ? formatNumber(dataStats.ohlc_data.total_records)
                : "0"}
            </div>
            <p className="text-xs text-muted-foreground">
              {dataStats
                ? getStorageInfo(dataStats.ohlc_data.total_records)
                : "0 KB"}{" "}
              estimated
            </p>
            {dataStats?.ohlc_data.latest_timestamp && (
              <p className="text-xs text-muted-foreground mt-1">
                Latest:{" "}
                {new Date(
                  dataStats.ohlc_data.latest_timestamp
                ).toLocaleString()}
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Data Export</CardTitle>
          <CardDescription>
            Export historical data in CSV or JSON format for analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Data Type</Label>
              <Select value={exportType} onValueChange={setExportType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="tick">Tick Data</SelectItem>
                  <SelectItem value="orderbook">Order Book</SelectItem>
                  <SelectItem value="ohlc">OHLC Data</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Export Format</Label>
              <Select value={exportFormat} onValueChange={setExportFormat}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">CSV</SelectItem>
                  <SelectItem value="json">JSON (o3 compatible)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Start Date</Label>
              <Input
                type="date"
                value={startDate ? startDate.toISOString().split("T")[0] : ""}
                onChange={(e) =>
                  setStartDate(
                    e.target.value ? new Date(e.target.value) : undefined
                  )
                }
              />
            </div>

            <div className="space-y-2">
              <Label>End Date</Label>
              <Input
                type="date"
                value={endDate ? endDate.toISOString().split("T")[0] : ""}
                onChange={(e) =>
                  setEndDate(
                    e.target.value ? new Date(e.target.value) : undefined
                  )
                }
              />
            </div>
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium">
                Export {exportType} data for {symbol} on{" "}
                {exchange.toUpperCase()}
              </p>
              <p className="text-sm text-muted-foreground">
                {startDate &&
                  endDate &&
                  `${startDate.toLocaleDateString()} to ${endDate.toLocaleDateString()}`}
              </p>
            </div>
            <Button
              onClick={handleExportData}
              disabled={isExporting || !startDate || !endDate}
            >
              <Download className="h-4 w-4 mr-2" />
              {isExporting
                ? "Exporting..."
                : `Export ${exportFormat.toUpperCase()}`}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Data Search & Filter</CardTitle>
          <CardDescription>
            Search and filter stored data by various criteria
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex space-x-2">
            <div className="flex-1">
              <Input
                placeholder="Search data by timestamp, price range, etc..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Button variant="outline">
              <Search className="h-4 w-4 mr-2" />
              Search
            </Button>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <Badge variant="outline">Last 24h</Badge>
            <Badge variant="outline">Last 7d</Badge>
            <Badge variant="outline">Last 30d</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Storage Management</CardTitle>
          <CardDescription>
            Manage data retention and storage policies
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="font-medium">SQLite (Active)</span>
              </div>
              <p className="text-muted-foreground">Last 12 months</p>
              <p className="text-muted-foreground">Real-time access</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span className="font-medium">Parquet (Compressed)</span>
              </div>
              <p className="text-muted-foreground">6 months - 2 years</p>
              <p className="text-muted-foreground">Archived data</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="font-medium">Auto-Delete</span>
              </div>
              <p className="text-muted-foreground">2+ years old</p>
              <p className="text-muted-foreground">Permanently removed</p>
            </div>
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Manual Cleanup</p>
              <p className="text-sm text-muted-foreground">
                Remove old data manually
              </p>
            </div>
            <Button variant="outline" size="sm">
              <Trash2 className="h-4 w-4 mr-2" />
              Cleanup Old Data
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
