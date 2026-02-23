import React from 'react';

function LiquidationHeatmap({ data }) {
  // DEBUG - always render something
  console.log('LiquidationHeatmap rendering, data:', data);
  
  return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-red-500 p-6">
      <h2 className="text-xl font-bold text-white mb-4">💥 BTC LIQUIDATION HEATMAP (TEST)</h2>
      
      {!data && (
        <div className="text-yellow-400 mb-4">⚠️ No data received yet</div>
      )}
      
      {data && (
        <div className="text-green-400 mb-4">
          ✓ Data received! Keys: {Object.keys(data).join(', ')}
        </div>
      )}
      
      <div className="bg-cyber-surface rounded p-4">
        <div className="text-cyber-text-secondary mb-2">Current Price:</div>
        <div className="text-2xl font-mono text-cyber-accent-green">
          {data?.current_price ? `$${data.current_price.toLocaleString()}` : '$---'}
        </div>
        
        {data?.fragility && (
          <div className="mt-4">
            <div className="text-cyber-text-secondary mb-2">Fragility Score:</div>
            <div className="text-xl font-mono">
              {data.fragility.emoji || '⚪'} {data.fragility.score !== undefined ? data.fragility.score.toFixed(1) : 'N/A'}/100
              <span className="ml-2 text-cyber-text-secondary">({data.fragility.level || 'Unknown'})</span>
            </div>
          </div>
        )}
        
        {data?.estimated && (
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div className="bg-cyber-bg-primary rounded p-3">
              <div className="text-xs text-cyber-text-secondary">Longs at Risk</div>
              <div className="text-green-400 font-mono text-lg">
                ${((data.estimated.total_long_at_risk || 0) / 1e9).toFixed(1)}B
              </div>
            </div>
            <div className="bg-cyber-bg-primary rounded p-3">
              <div className="text-xs text-cyber-text-secondary">Shorts at Risk</div>
              <div className="text-red-400 font-mono text-lg">
                ${((data.estimated.total_short_at_risk || 0) / 1e9).toFixed(1)}B
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

export default LiquidationHeatmap;
