import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

function KeyLevelsCDC({ data }) {
  if (!data) return null;

  const { btc, eth } = data;
  
  // Check if using order block or fallback
  const btcSource = btc?.levels?.source || 'fallback';
  const ethSource = eth?.levels?.source || 'fallback';
  const isOrderBlock = btcSource === 'orderblock' || ethSource === 'orderblock';

  const renderAssetCard = (asset) => {
    const { symbol, price, cdc_signal, levels, ath_distance } = asset;
    const isPositive = ath_distance >= 0;
    
    return (
      <div className="bg-cyber-surface border border-cyber-border-subtle rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{symbol === 'BTC' ? '₿' : 'Ξ'}</span>
            <span className="text-xl font-bold">{symbol}</span>
          </div>
          <span className="text-2xl font-mono font-bold text-cyber-text-primary">
            ${price?.toLocaleString()}
          </span>
        </div>

        {/* CDC Signal */}
        <div className="mb-6">
          <div className="text-sm text-cyber-text-secondary mb-1">CDC Signal</div>
          <div className={`text-lg font-bold ${cdc_signal?.color === 'green' ? 'text-green-400' : cdc_signal?.color === 'red' ? 'text-red-400' : 'text-yellow-400'}`}>
            {cdc_signal?.emoji} {cdc_signal?.signal}
          </div>
        </div>

        {/* Key Levels - Order Block Style */}
        <div className="space-y-2 mb-4">
          {/* R2 */}
          <div className="flex items-center justify-between text-red-400">
            <div className="flex items-center gap-2">
              <span>🔴</span>
              <span className="font-semibold">R2</span>
            </div>
            <span className="font-mono">${levels?.r2?.toLocaleString()}</span>
          </div>
          
          {/* R1 */}
          <div className="flex items-center justify-between text-red-400">
            <div className="flex items-center gap-2">
              <span>🔴</span>
              <span className="font-semibold">R1</span>
            </div>
            <span className="font-mono">${levels?.r1?.toLocaleString()}</span>
          </div>
          
          {/* Current Price Marker */}
          <div className="flex items-center justify-center py-3 border-y-2 border-dashed border-cyber-border-subtle my-2">
            <span className="text-cyber-accent-blue font-mono font-bold text-lg">
              ▶ ${price?.toLocaleString()} ◀
            </span>
          </div>
          
          {/* S1 */}
          <div className="flex items-center justify-between text-green-400">
            <div className="flex items-center gap-2">
              <span>🟢</span>
              <span className="font-semibold">S1</span>
            </div>
            <span className="font-mono">${levels?.s1?.toLocaleString()}</span>
          </div>
          
          {/* S2 */}
          <div className="flex items-center justify-between text-green-400">
            <div className="flex items-center gap-2">
              <span>🟢</span>
              <span className="font-semibold">S2</span>
            </div>
            <span className="font-mono">${levels?.s2?.toLocaleString()}</span>
          </div>
        </div>

        {/* ATH Distance */}
        <div className="pt-4 border-t border-cyber-border-subtle">
          <div className={`flex items-center gap-2 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span className="text-sm">
              {isPositive ? '+' : ''}{ath_distance}% from ATH
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
      <div className="flex items-center gap-2 mb-6">
        <span className="text-2xl">📊</span>
        <h2 className="text-xl font-bold text-cyber-text-primary">KEY LEVELS & CDC SIGNAL</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {btc && renderAssetCard(btc)}
        {eth && renderAssetCard(eth)}
      </div>
      
      {/* Footnote */}
      <div className="mt-6 pt-4 border-t border-cyber-border-subtle text-center">
        <p className="text-xs text-cyber-text-muted">
          ℹ️ S/R levels based on {isOrderBlock ? 'Order Block detection (Smart Money Concept)' : 'technical analysis'}
        </p>
      </div>
    </section>
  );
}

export default KeyLevelsCDC;
