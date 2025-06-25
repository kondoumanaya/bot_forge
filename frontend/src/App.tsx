import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Activity, TrendingUp, Database, Settings, Play, Square, BarChart3, TestTube, FolderOpen, Menu } from 'lucide-react'
import { SUPPORTED_EXCHANGES } from '@/constants/exchanges'
import DataPreview from './components/DataPreview'
import BacktestPanel from './components/BacktestPanel'
import AnalysisPanel from './components/AnalysisPanel'
import DataManagement from './components/DataManagement'
import SettingsPanel from './components/SettingsPanel'
import './App.css'

interface SystemConfig {
  supported_exchanges: string[]
  supported_timeframes: string[]
  default_exchange: string
  default_timeframe: string
}

function App() {
  const [selectedExchange, setSelectedExchange] = useState<string>('binance')
  const [selectedSymbol, setSelectedSymbol] = useState<string>('BTC_JPY')
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('1m')
  const [isCollecting, setIsCollecting] = useState<boolean>(false)
  const [systemConfig, setSystemConfig] = useState<SystemConfig | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected')
  const [activeView, setActiveView] = useState<string>('data-preview')
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true)

  useEffect(() => {
    fetch('http://localhost:8000/api/config')
      .then(res => res.json())
      .then(config => {
        setSystemConfig(config)
        setSelectedExchange(config.default_exchange)
        setSelectedTimeframe(config.default_timeframe)
      })
      .catch(err => console.error('Failed to load config:', err))
  }, [])

  const handleStartCollection = async () => {
    try {
      setIsCollecting(true)
      const response = await fetch('http://localhost:8000/api/data/start-collection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          exchange: selectedExchange,
          symbol: selectedSymbol,
          data_types: ['tick', 'orderbook', 'ohlc']
        })
      })
      
      if (response.ok) {
        setConnectionStatus('connected')
      } else {
        throw new Error('Failed to start collection')
      }
    } catch (error) {
      console.error('Error starting collection:', error)
      setIsCollecting(false)
      setConnectionStatus('disconnected')
    }
  }

  const handleStopCollection = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/data/stop-collection?exchange=${selectedExchange}&symbol=${selectedSymbol}`, {
        method: 'POST'
      })
      
      if (response.ok) {
        setIsCollecting(false)
        setConnectionStatus('disconnected')
      }
    } catch (error) {
      console.error('Error stopping collection:', error)
    }
  }

  const renderMainContent = () => {
    switch (activeView) {
      case 'data-preview':
        return (
          <DataPreview 
            exchange={selectedExchange}
            symbol={selectedSymbol}
            timeframe={selectedTimeframe}
            isCollecting={isCollecting}
          />
        );
      case 'backtest':
        return (
          <BacktestPanel 
            exchange={selectedExchange}
            symbol={selectedSymbol}
          />
        );
      case 'analysis':
        return (
          <AnalysisPanel 
            exchange={selectedExchange}
            symbol={selectedSymbol}
          />
        );
      case 'data-management':
        return (
          <DataManagement 
            exchange={selectedExchange}
            symbol={selectedSymbol}
          />
        );
      case 'settings':
        return (
          <SettingsPanel 
            selectedExchange={selectedExchange}
          />
        );
      default:
        return (
          <DataPreview 
            exchange={selectedExchange}
            symbol={selectedSymbol}
            timeframe={selectedTimeframe}
            isCollecting={isCollecting}
          />
        );
    }
  };

  const sidebarItems = [
    { id: 'data-preview', label: 'Data Preview', icon: Database },
    { id: 'backtest', label: 'Backtest', icon: TestTube },
    { id: 'analysis', label: 'Analysis', icon: BarChart3 },
    { id: 'data-management', label: 'Data Management', icon: FolderOpen },
    { id: 'settings', label: 'ルート設定', icon: Settings },
  ];

  return (
    <div className="min-h-screen flex w-full bg-background">
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300 border-r bg-card`}>
        <div className="border-b px-6 py-4">
          <div className="flex items-center space-x-2">
            <Activity className="h-6 w-6" />
            {sidebarOpen && <h1 className="text-xl font-semibold">Bot Forge</h1>}
          </div>
        </div>
        <div className="px-3 py-2">
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeView === item.id
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                }`}
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                {sidebarOpen && <span>{item.label}</span>}
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <div className="border-b">
          <div className="flex h-16 items-center px-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="mr-4"
            >
              <Menu className="h-4 w-4" />
            </Button>
            <div className="flex items-center space-x-2">
              <Badge variant={connectionStatus === 'connected' ? 'default' : 'secondary'}>
                {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </Badge>
            </div>
          </div>
        </div>

        <div className="flex-1 space-y-4 p-4">
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Exchange</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <Select value={selectedExchange} onValueChange={setSelectedExchange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select exchange" />
                  </SelectTrigger>
                  <SelectContent>
                    {systemConfig?.supported_exchanges.map((exchange) => {
                      const exchangeInfo = SUPPORTED_EXCHANGES.find(e => e.id === exchange);
                      return (
                        <SelectItem key={exchange} value={exchange}>
                          {exchangeInfo?.displayName || exchange.toUpperCase()}
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Symbol</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select symbol" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="BTC_JPY">BTC/JPY</SelectItem>
                    <SelectItem value="ETH_JPY">ETH/JPY</SelectItem>
                    <SelectItem value="BTC_USDT">BTC/USDT</SelectItem>
                    <SelectItem value="ETH_USDT">ETH/USDT</SelectItem>
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Timeframe</CardTitle>
                <Settings className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <Select value={selectedTimeframe} onValueChange={setSelectedTimeframe}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select timeframe" />
                  </SelectTrigger>
                  <SelectContent>
                    {systemConfig?.supported_timeframes.map((timeframe) => (
                      <SelectItem key={timeframe} value={timeframe}>
                        {timeframe}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Data Collection</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex space-x-2">
                  <Button
                    onClick={handleStartCollection}
                    disabled={isCollecting}
                    size="sm"
                    className="flex-1"
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Start
                  </Button>
                  <Button
                    onClick={handleStopCollection}
                    disabled={!isCollecting}
                    variant="outline"
                    size="sm"
                    className="flex-1"
                  >
                    <Square className="h-4 w-4 mr-1" />
                    Stop
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <Separator />

          <div className="space-y-4">
            {renderMainContent()}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
