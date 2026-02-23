import React from 'react';

function LiquidationHeatmap({ data }) {
  return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
      <h2 className="text-xl font-bold text-cyber-text-primary mb-4">💥 BTC LIQUIDATION HEATMAP</h2>
      
      {!data ? (
        <div className="text-cyber-text-secondary">Loading...</div>
      ) : (
        <div>
          <div className="flex justify-between items-center mb-4">
            <span className="text-cyber-text-secondary">Current Price:</span>
            <span className="font-mono text-cyber-accent-green">${data.current_price?.toLocaleString()}</span>
          </div>
          
          <div className="flex justify-between items-center mb-4">
            <span className="text-cyber-text-secondary">Fragility Score:</span>
            <span className="font-mono">
              {data.fragility?.emoji} {data.fragility?.score}/100 {data.fragility?.level}
            </span>
          </div>

          {/* Short Liquidations */}
          <div className="mb-3">
            <div className="text-xs text-cyber-text-secondary mb-1">SHORT LIQUIDATIONS (Above)</div>
            {data.estimated?.short_liquidations && Object.entries(data.estimated.short_liquidations).length > 0 ? (
              Object.entries(data.estimated.short_liquidations)
                .sort((a, b) => parseInt(b[0]) - parseInt(a[0]))
                .slice(0, 5)
                .map(([price, amount]) => (
                  <div key={price} className="flex justify-between text-sm py-1">
                    <span className="font-mono">${(parseInt(price)/1000).toFixed(0)}k</span>
                    <span className="text-red-400">${(amount/1e9).toFixed(1)}B</span>
                  </div>
                ))
            ) : (
              <div className="text-sm text-cyber-text-muted">No data</div>
            )}
          </div>

          {/* Current Price Divider */}
          <div className="text-center py-2 border-y border-cyber-border-subtle my-2">
            <span className="font-mono font-bold text-cyber-accent-green">
              ▶ ${data.current_price?.toLocaleString()} ◀
            </span>
          </div>

          {/* Long Liquidations */}
          <div className="mb-3">
            <div className="text-xs text-cyber-text-secondary mb-1">LONG LIQUIDATIONS (Below)</div>
            {data.estimated?.long_liquidations && Object.entries(data.estimated.long_liquidations).length > 0 ? (
              Object.entries(data.estimated.long_liquidations)
                .sort((a, b) => parseInt(b[0]) - parseInt(a[0]))
                .slice(0, 5)
                .map(([price, amount]) => (
                  <div key={price} className="flex justify-between text-sm py-1">
                    <span className="font-mono">${(parseInt(price)/1000).toFixed(0)}k</span>
                    <span className="text-green-400">${(amount/1e9).toFixed(1)}B</span>
                  </div>
                ))
            ) : (
              <div className="text-sm text-cyber-text-muted">No data</div>
            )}
          </div>

          {/* Summary */}
          <div className="grid grid-cols-2 gap-3 mt-4">
            <div className="bg-cyber-surface rounded p-2 text-center">
              <div className="text-xs text-cyber-text-secondary">Longs at Risk</div>
              <div className="text-green-400 font-mono">
                ${((data.estimated?.total_long_at_risk || 0)/1e9).toFixed(1)}B
              </div>
            </div>
            <div className="bg-cyber-surface rounded p-2 text-center">
              <div className="text-xs text-cyber-text-secondary">Shorts at Risk</div>
              <div className="text-red-400 font-mono">
                ${((data.estimated?.total_short_at_risk || 0)/1e9).toFixed(1)}B
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default LiquidationHeatmap;
