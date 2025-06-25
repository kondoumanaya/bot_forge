export interface ExchangeInfo {
  id: string;
  name: string;
  displayName: string;
  hasPassphrase?: boolean;
  hasSandbox?: boolean;
}

export const SUPPORTED_EXCHANGES: ExchangeInfo[] = [
  { id: 'bitflyer', name: 'bitflyer', displayName: 'bitFlyer', hasSandbox: true },
  { id: 'gmocoin', name: 'gmocoin', displayName: 'GMO Coin', hasSandbox: true },
  { id: 'bitbank', name: 'bitbank', displayName: 'bitbank', hasSandbox: true },
  { id: 'coincheck', name: 'coincheck', displayName: 'Coincheck', hasSandbox: true },
  { id: 'okj', name: 'okj', displayName: 'OKJ', hasSandbox: true },
  { id: 'bittrade', name: 'bittrade', displayName: 'BitTrade', hasSandbox: true },
  { id: 'bybit', name: 'bybit', displayName: 'Bybit', hasSandbox: true },
  { id: 'binance', name: 'binance', displayName: 'Binance', hasSandbox: true },
  { id: 'okx', name: 'okx', displayName: 'OKX', hasSandbox: true },
  { id: 'phemex', name: 'phemex', displayName: 'Phemex', hasSandbox: true },
  { id: 'bitget', name: 'bitget', displayName: 'Bitget', hasSandbox: true },
  { id: 'mexc', name: 'mexc', displayName: 'MEXC', hasSandbox: true },
  { id: 'kucoin', name: 'kucoin', displayName: 'KuCoin', hasPassphrase: true, hasSandbox: true },
  { id: 'bitmex', name: 'bitmex', displayName: 'BitMEX', hasSandbox: true },
  { id: 'hyperliquid', name: 'hyperliquid', displayName: 'Hyperliquid', hasSandbox: true },
];

export const getExchangeById = (id: string): ExchangeInfo | undefined => {
  return SUPPORTED_EXCHANGES.find(exchange => exchange.id === id);
};

export const getExchangeDisplayName = (id: string): string => {
  const exchange = getExchangeById(id);
  return exchange ? exchange.displayName : id.toUpperCase();
};
