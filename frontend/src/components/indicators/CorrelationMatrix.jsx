import React from 'react';
import { TrendingUp, TrendingDown, Minus, Shield } from 'lucide-react';

function CorrelationMatrix({ data }) {
  if (!data) return null;

  const { correlations, paxg_btc } = data;

  const getBarWidth = (correlation) => {
    // Correlation ranges from -1 to 1, map to 0-100%
    return ((correlation + 1) / 2) * 100;
  };

  const getBarColor = (correlation) => {
    if (correlation > 0.3) return 'bg-green-500';
    if (correlation < -0.3) return 'bg-red-500';
    return 'bg-yellow-500';
  };

  const renderCorrelationBar = (item) => {
    const width = getBarWidth(item.correlation);
    const color = getBarColor(item.correlation);
    
    return (
      <div key={item.asset} className="flex items-center gap-4 py-3 border-b border-cyber-border-subtle last:border-0">
        <div className="w-28 text-cyber-text-secondary">vs {item.asset}</div>
        <div className="w-16 font-mono text-cyber-text-primary">
          {item.correlation > 0 ? '+' : ''}{item.correlation.toFixed(2)}
        </div>
        <div className="flex-1 flex items-center gap-2">
          <div className="flex-1 h-3 bg-cyber-surface rounded-full overflow-hidden">
            <div 
              className={`h-full ${color}`}
              style={{ width: `${width}%` }}
            />
          </div>
          <span className="w-24 text-sm text-cyber-text-muted">{item.label}</span>
        </div>
      </div>
    );
  };

  return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
      <div className="flex items-center gap-2 mb-6">
        <span className="text-2xl">🔗</span>
        <h2 className="text-xl font-bold text-cyber-text-primary">CORRELATION MATRIX & PAXG/BTC</h2>
      </div>

      {/* Correlations */}
      <div className="mb-6">
        <h3 className="text-lg font-bold text-cyber-text-secondary mb-3">
          BTC CORRELATION (30D Rolling)
        </h3>
        <div>
          {correlations?.correlations?.map(renderCorrelationBar)}
        </div>
        
        {/* Insight */}
        {correlations?.insight && (
          <div className="mt-4 text-cyber-text-primary">
            {correlations.insight}
          </div>
        )}
      </div>

      <hr className="border-cyber-border-subtle my-6" />

      {/* PAXG/BTC */}
      <div>
        <h3 className="text-lg font-bold text-cyber-text-secondary mb-4 flex items-center gap-2">
          🪙 PAXG/BTC RATIO
        </h3>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-cyber-surface rounded-lg p-4">
            <div className="text-sm text-cyber-text-secondary">Current</div>
            <div className="text-2xl font-mono font-bold text-cyber-text-primary">
              {paxg_btc?.current_ratio?.toFixed(5)}
            </div>
          </div>
          <div className="bg-cyber-surface rounded-lg p-4">
            <div className="text-sm text-cyber-text-secondary">24h</div>
            <div className={`text-2xl font-mono font-bold ${paxg_btc?.change_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {paxg_btc?.change_24h >= 0 ? '↑' : '↓'} {Math.abs(paxg_btc?.change_24h || 0).toFixed(2)}%
            </div>
          </div>
          <div className="bg-cyber-surface rounded-lg p-4">
            <div className="text-sm text-cyber-text-secondary">7d</div>
            <div className={`text-2xl font-mono font-bold ${paxg_btc?.change_7d >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {paxg_btc?.change_7d >= 0 ? '↑' : '↓'} {Math.abs(paxg_btc?.change_7d || 0).toFixed(2)}%
            </div>
          </div>
          <div className="bg-cyber-surface rounded-lg p-4">
            <div className="text-sm text-cyber-text-secondary">30d</div>
            <div className={`text-2xl font-mono font-bold ${paxg_btc?.change_30d >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {paxg_btc?.change_30d >= 0 ? '↑' : '↓'} {Math.abs(paxg_btc?.change_30d || 0).toFixed(2)}%
            </div>
          </div>
        </div>

        {/* Trend Signal */}
        {paxg_btc?.trend && (
          <div className="bg-cyber-surface rounded-lg p-4 border border-cyber-border-subtle">
            <div className={`text-lg font-bold mb-2 ${
              paxg_btc.trend.signal === 'GOLD OUTPERFORMING BTC' ? 'text-yellow-400' :
              paxg_btc.trend.signal === 'BTC OUTPERFORMING GOLD' ? 'text-green-400' :
              'text-gray-400'
            }`}>
              {paxg_btc.trend.emoji} {paxg_btc.trend.signal}
            </div>
            <div className="flex items-center gap-2 text-cyber-text-secondary">
              <Shield size={16} />
              <span>{paxg_btc.trend.bitgold}</span>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

export default CorrelationMatrix;
