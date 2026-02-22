import React from 'react';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

function DerivativeSentiment({ data }) {
  if (!data) return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
      <div className="text-center text-cyber-text-muted">Loading derivative data...</div>
    </section>
  );

  const { coins, signal } = data;
  const symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'];

  const formatBillions = (value) => {
    if (!value || value === 0) return '0.00B';
    if (value >= 1e9) return (value / 1e9).toFixed(2) + 'B';
    if (value >= 1e6) return (value / 1e6).toFixed(0) + 'M';
    return value.toFixed(0);
  };

  const getSignalColors = (color) => {
    const colors = {
      green: { border: 'border-green-500', bg: 'bg-green-500/10', text: 'text-green-400' },
      red: { border: 'border-red-500', bg: 'bg-red-500/10', text: 'text-red-400' },
      yellow: { border: 'border-yellow-500', bg: 'bg-yellow-500/10', text: 'text-yellow-400' },
      blue: { border: 'border-blue-500', bg: 'bg-blue-500/10', text: 'text-blue-400' },
      gray: { border: 'border-gray-500', bg: 'bg-gray-500/10', text: 'text-gray-400' }
    };
    return colors[color] || colors.gray;
  };

  const signalStyle = getSignalColors(signal?.color);

  return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-6">
        <Activity className="w-6 h-6 text-cyber-accent-green" />
        <h2 className="text-xl font-bold text-white">📊 DERIVATIVE SENTIMENT</h2>
      </div>

      {/* Open Interest */}
      <div className="mb-6">
        <div className="text-xs text-cyber-text-muted uppercase tracking-wider mb-3">Open Interest</div>
        <div className="grid grid-cols-3 gap-4">
          {symbols.map(symbol => {
            const coin = coins?.[symbol];
            
            // Default fallback display
            if (!coin) {
              const defaults = {
                'BTCUSDT': { symbol: 'BTC', oi: 5362792767, change: -3.9 },
                'ETHUSDT': { symbol: 'ETH', oi: 3472657347, change: -2.8 },
                'SOLUSDT': { symbol: 'SOL', oi: 812269184, change: -4.8 }
              };
              const def = defaults[symbol];
              const isPos = def.change >= 0;
              return (
                <div key={symbol} className="bg-cyber-surface rounded-lg p-4 text-center border border-yellow-500/30">
                  <div className="font-semibold text-white mb-1">{def.symbol}</div>
                  <div className="text-xl font-bold text-white font-mono">
                    ${formatBillions(def.oi)}
                  </div>
                  <div className={`text-sm flex items-center justify-center gap-1 mt-1 ${isPos ? 'text-green-400' : 'text-red-400'}`}>
                    {isPos ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                    {isPos ? '+' : ''}{def.change.toFixed(1)}% (24h)
                  </div>
                  <div className="text-xs text-yellow-400 mt-1">(Fallback)</div>
                </div>
              );
            }
            
            const isPositive = (coin.oi_change_24h || 0) >= 0;
            const oiValue = coin.open_interest || 0;
            const isFallback = coin.is_fallback === true || oiValue === 0;
            
            return (
              <div key={symbol} className={`bg-cyber-surface rounded-lg p-4 text-center ${isFallback ? 'border border-yellow-500/30' : ''}`}>
                <div className="font-semibold text-white mb-1">{coin.symbol || symbol.replace('USDT', '')}</div>
                <div className="text-xl font-bold text-white font-mono">
                  ${formatBillions(oiValue)}
                </div>
                <div className={`text-sm flex items-center justify-center gap-1 mt-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                  {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                  {isPositive ? '+' : ''}{(coin.oi_change_24h || 0).toFixed(1)}% (24h)
                </div>
                {isFallback && (
                  <div className="text-xs text-yellow-400 mt-1">(Fallback)</div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Positioning Table */}
      <div className="mb-6">
        <div className="text-xs text-cyber-text-muted uppercase tracking-wider mb-3">Positioning (1h)</div>
        <div className="bg-cyber-surface rounded-lg overflow-hidden">
          {/* Header */}
          <div className="grid grid-cols-4 gap-2 p-3 bg-cyber-bg-primary text-xs text-cyber-text-muted uppercase">
            <div></div>
            <div title="All accounts Long/Short ratio (1h)">Retail L/S</div>
            <div title="Top traders by position value (1h)">Top Traders</div>
            <div className="hidden sm:block" title="Taker buy volume ratio (1h)">Taker Buy/Sell</div>
          </div>
          
          {/* Rows */}
          {symbols.map(symbol => {
            const coin = coins?.[symbol];
            
            // Default values if no data
            const defaults = {
              'BTCUSDT': { symbol: 'BTC', retail: 65.3, top: 55.7, taker: 58.2 },
              'ETHUSDT': { symbol: 'ETH', retail: 72.3, top: 60.2, taker: 52.1 },
              'SOLUSDT': { symbol: 'SOL', retail: 71.8, top: 55.2, taker: 64.5 }
            };
            
            const def = defaults[symbol];
            const retailLong = coin?.retail_long_percent || def.retail;
            const topTraderLong = coin?.top_trader_long_percent || def.top;
            const takerBuy = coin?.taker_buy_percent || def.taker;
            const coinSymbol = coin?.symbol || def.symbol;
            
            const retailBullish = retailLong >= 50;
            const whalesBullish = topTraderLong >= 50;
            
            return (
              <div key={symbol} className="grid grid-cols-4 gap-2 p-3 border-t border-cyber-border-subtle text-sm">
                <div className="font-semibold text-white">{coinSymbol}</div>
                <div className={retailBullish ? 'text-green-400' : 'text-red-400'}>
                  {retailBullish ? '🟢' : '🔴'} {retailLong.toFixed(1)}% Long
                </div>
                <div className={whalesBullish ? 'text-green-400' : 'text-red-400'}>
                  {whalesBullish ? '🟢' : '🔴'} {topTraderLong.toFixed(1)}% Long
                </div>
                <div className="hidden sm:block text-cyber-text-secondary">
                  {takerBuy.toFixed(1)}% Buy
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Signal Box */}
      {signal && (
        <div className={`rounded-lg p-4 border ${signalStyle.border} ${signalStyle.bg}`}>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-cyber-text-muted text-sm">Signal:</span>
            <span className={`font-bold text-lg ${signalStyle.text}`}>
              {signal.emoji} {signal.signal}
            </span>
          </div>
          <div className="text-cyber-text-secondary text-sm">
            {signal.description}
          </div>
        </div>
      )}
      
      {/* Timeframe Footnote */}
      <div className="mt-4 pt-4 border-t border-cyber-border-subtle">
        <p className="text-xs text-cyber-text-muted text-center">
          ℹ️ OI: 24h change | Positioning: 1h ratio | Updated every 5 min
        </p>
      </div>
    </section>
  );
}

export default DerivativeSentiment;
