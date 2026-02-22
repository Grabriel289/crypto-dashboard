import React from 'react';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

function DerivativeSentiment({ data }) {
  if (!data) return null;

  const { coins, signal } = data;
  const symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'];

  const formatBillions = (value) => {
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
            if (!coin) return null;
            const isPositive = coin.oi_change_24h >= 0;
            
            return (
              <div key={symbol} className="bg-cyber-surface rounded-lg p-4 text-center">
                <div className="font-semibold text-white mb-1">{coin.symbol}</div>
                <div className="text-xl font-bold text-white font-mono">
                  ${formatBillions(coin.open_interest)}
                </div>
                <div className={`text-sm flex items-center justify-center gap-1 mt-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                  {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                  {isPositive ? '+' : ''}{coin.oi_change_24h.toFixed(1)}% (24h)
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Positioning Table */}
      <div className="mb-6">
        <div className="text-xs text-cyber-text-muted uppercase tracking-wider mb-3">Positioning</div>
        <div className="bg-cyber-surface rounded-lg overflow-hidden">
          {/* Header */}
          <div className="grid grid-cols-4 gap-2 p-3 bg-cyber-bg-primary text-xs text-cyber-text-muted uppercase">
            <div></div>
            <div>Retail L/S</div>
            <div>Top Traders</div>
            <div className="hidden sm:block">Taker Buy/Sell</div>
          </div>
          
          {/* Rows */}
          {symbols.map(symbol => {
            const coin = coins?.[symbol];
            if (!coin) return null;
            
            const retailBullish = coin.retail_long_percent >= 50;
            const whalesBullish = coin.top_trader_long_percent >= 50;
            
            return (
              <div key={symbol} className="grid grid-cols-4 gap-2 p-3 border-t border-cyber-border-subtle text-sm">
                <div className="font-semibold text-white">{coin.symbol}</div>
                <div className={retailBullish ? 'text-green-400' : 'text-red-400'}>
                  {retailBullish ? '🟢' : '🔴'} {coin.retail_long_percent.toFixed(1)}% Long
                </div>
                <div className={whalesBullish ? 'text-green-400' : 'text-red-400'}>
                  {whalesBullish ? '🟢' : '🔴'} {coin.top_trader_long_percent.toFixed(1)}% Long
                </div>
                <div className="hidden sm:block text-cyber-text-secondary">
                  {coin.taker_buy_percent.toFixed(1)}% Buy
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
    </section>
  );
}

export default DerivativeSentiment;
