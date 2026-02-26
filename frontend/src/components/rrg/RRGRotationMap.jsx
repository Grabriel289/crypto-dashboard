import React from 'react';
import { TrendingUp, TrendingDown, Minus, Target, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

function RRGRotationMap({ data }) {
  // Debug logging
  console.log('RRGRotationMap data:', data);
  
  if (!data) {
    return (
      <div className="dashboard-card">
        <div className="flex items-center gap-3 mb-4">
          <Target className="w-6 h-6 text-cyber-accent-cyan" />
          <h2 className="text-xl font-bold text-white">🔄 RRG Rotation Map</h2>
        </div>
        <p className="text-cyber-text-secondary">Loading RRG data...</p>
      </div>
    );
  }
  
  if (data.error) {
    return (
      <div className="dashboard-card">
        <div className="flex items-center gap-3 mb-4">
          <Target className="w-6 h-6 text-cyber-accent-cyan" />
          <h2 className="text-xl font-bold text-white">🔄 RRG Rotation Map</h2>
        </div>
        <p className="text-cyber-text-secondary text-red-400">
          Error: {data.error}
        </p>
      </div>
    );
  }

  const { 
    risk_assets = [], 
    safe_haven_assets = [], 
    regime = {}, 
    top_picks = [], 
    action_groups = [],
    insights = []
  } = data;

  // Combine all assets for the chart
  const allAssets = [...risk_assets, ...safe_haven_assets];

  // Calculate chart scaling
  const minX = Math.min(...allAssets.map(a => a.coordinate.rs_ratio), 95);
  const maxX = Math.max(...allAssets.map(a => a.coordinate.rs_ratio), 105);
  const minY = Math.min(...allAssets.map(a => a.coordinate.rs_momentum), 95);
  const maxY = Math.max(...allAssets.map(a => a.coordinate.rs_momentum), 105);
  
  const rangeX = maxX - minX || 20;
  const rangeY = maxY - minY || 20;

  const scaleX = (val) => ((val - minX) / rangeX) * 100;
  const scaleY = (val) => 100 - ((val - minY) / rangeY) * 100; // Invert Y for chart

  // Quadrant colors
  const quadrantColors = {
    leading: 'bg-green-500/10 border-green-500/30',
    weakening: 'bg-yellow-500/10 border-yellow-500/30',
    lagging: 'bg-red-500/10 border-red-500/30',
    improving: 'bg-blue-500/10 border-blue-500/30'
  };

  const quadrantLabels = {
    leading: { text: 'LEADING', color: 'text-green-400', emoji: '🚀' },
    weakening: { text: 'WEAKENING', color: 'text-yellow-400', emoji: '⚠️' },
    lagging: { text: 'LAGGING', color: 'text-red-400', emoji: '📉' },
    improving: { text: 'IMPROVING', color: 'text-blue-400', emoji: '📈' }
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'buy': return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'reduce': return <TrendingDown className="w-4 h-4 text-yellow-400" />;
      case 'avoid': return <XCircle className="w-4 h-4 text-red-400" />;
      default: return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="dashboard-card">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Target className="w-6 h-6 text-cyber-accent-cyan" />
          <h2 className="text-xl font-bold text-white">🔄 RRG Rotation Map</h2>
        </div>
        {regime.regime && (
          <div 
            className="px-4 py-2 rounded-lg border flex items-center gap-2"
            style={{ 
              backgroundColor: `${regime.color}20`,
              borderColor: regime.color 
            }}
          >
            <span className="text-xl">{regime.emoji}</span>
            <span 
              className="font-bold"
              style={{ color: regime.color }}
            >
              {regime.regime.replace('_', '-').toUpperCase()}
            </span>
            <span className="text-cyber-text-muted text-sm ml-2">
              (Score: {regime.score})
            </span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* RRG Chart */}
        <div className="relative">
          {/* Chart Container */}
          <div className="relative h-80 bg-cyber-bg-secondary rounded-lg border border-cyber-border-subtle overflow-hidden">
            {/* Quadrant Backgrounds */}
            <div className="absolute inset-0 grid grid-cols-2 grid-rows-2">
              <div className="bg-green-500/5 border-r border-b border-cyber-border-subtle" />
              <div className="bg-yellow-500/5 border-b border-cyber-border-subtle" />
              <div className="bg-blue-500/5 border-r border-cyber-border-subtle" />
              <div className="bg-red-500/5" />
            </div>

            {/* Center Lines */}
            <div className="absolute left-1/2 top-0 bottom-1 w-px bg-cyber-border-accent" />
            <div className="absolute top-1/2 left-0 right-1 h-px bg-cyber-border-accent" />

            {/* Center Label */}
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 
                          bg-cyber-bg-primary px-2 py-1 rounded text-xs text-cyber-text-muted">
              100
            </div>

            {/* Quadrant Labels */}
            <div className="absolute top-2 right-2 text-xs font-bold text-green-400">LEADING</div>
            <div className="absolute top-2 left-2 text-xs font-bold text-blue-400">IMPROVING</div>
            <div className="absolute bottom-2 right-2 text-xs font-bold text-yellow-400">WEAKENING</div>
            <div className="absolute bottom-2 left-2 text-xs font-bold text-red-400">LAGGING</div>

            {/* Axis Labels */}
            <div className="absolute bottom-1 left-1/2 -translate-x-1/2 text-xs text-cyber-text-muted">
              RS-Ratio →
            </div>
            <div className="absolute left-1 top-1/2 -translate-y-1/2 -rotate-90 text-xs text-cyber-text-muted">
              RS-Momentum →
            </div>

            {/* ETF Dots */}
            {allAssets.map((asset) => {
              const x = scaleX(asset.coordinate.rs_ratio);
              const y = scaleY(asset.coordinate.rs_momentum);
              const isSafeHaven = asset.category === 'safe_haven';
              
              return (
                <div
                  key={asset.symbol}
                  className="absolute transform -translate-x-1/2 -translate-y-1/2 group cursor-pointer"
                  style={{ left: `${x}%`, top: `${y}%` }}
                >
                  {/* Dot */}
                  <div
                    className={`w-4 h-4 rounded-full border-2 transition-all duration-200 
                              group-hover:scale-125 ${isSafeHaven ? 'border-dashed' : 'border-solid'}`}
                    style={{ 
                      backgroundColor: asset.color,
                      borderColor: isSafeHaven ? '#ffd700' : asset.color
                    }}
                  />
                  {/* Label */}
                  <div className="absolute top-5 left-1/2 -translate-x-1/2 whitespace-nowrap
                                text-xs font-bold text-white opacity-0 group-hover:opacity-100
                                transition-opacity bg-cyber-bg-primary px-2 py-1 rounded">
                    {asset.symbol}
                  </div>
                  
                  {/* Tooltip */}
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2
                                bg-cyber-bg-card border border-cyber-border-subtle rounded-lg p-3
                                opacity-0 group-hover:opacity-100 transition-opacity
                                pointer-events-none z-10 w-48">
                    <div className="text-sm font-bold text-white mb-1">{asset.name}</div>
                    <div className="text-xs text-cyber-text-muted mb-2">{asset.symbol}</div>
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span className="text-cyber-text-muted">RS-Ratio:</span>
                        <span className="text-white">{asset.coordinate.rs_ratio.toFixed(1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-cyber-text-muted">RS-Momentum:</span>
                        <span className="text-white">{asset.coordinate.rs_momentum.toFixed(1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-cyber-text-muted">Return:</span>
                        <span className={asset.period_return >= 0 ? 'text-green-400' : 'text-red-400'}>
                          {asset.period_return >= 0 ? '+' : ''}{asset.period_return.toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between items-center pt-1 border-t border-cyber-border-subtle mt-1">
                        <span className="text-cyber-text-muted">Status:</span>
                        <span className={quadrantLabels[asset.coordinate.quadrant].color}>
                          {quadrantLabels[asset.coordinate.quadrant].emoji} {quadrantLabels[asset.coordinate.quadrant].text}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Legend */}
          <div className="mt-4 flex flex-wrap gap-4">
            {/* Risk Assets */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-cyber-text-muted uppercase">Risk:</span>
              {risk_assets.map(asset => (
                <div key={asset.symbol} className="flex items-center gap-1">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: asset.color }}
                  />
                  <span className="text-xs text-white">{asset.symbol}</span>
                </div>
              ))}
            </div>
            
            {/* Safe Haven */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-cyber-text-muted uppercase">Safe Haven:</span>
              {safe_haven_assets.map(asset => (
                <div key={asset.symbol} className="flex items-center gap-1">
                  <div 
                    className="w-3 h-3 rounded-full border border-dashed border-yellow-400"
                    style={{ backgroundColor: asset.color }}
                  />
                  <span className="text-xs text-white">{asset.symbol}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel - Recommendations & Insights */}
        <div className="space-y-4">
          {/* Top Picks */}
          {top_picks.length > 0 && (
            <div className="bg-cyber-bg-secondary rounded-lg p-4 border border-cyber-border-subtle">
              <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-green-400" />
                Top Picks
              </h3>
              <div className="space-y-2">
                {top_picks.map((pick) => (
                  <div 
                    key={pick.symbol}
                    className="flex items-center justify-between p-2 bg-cyber-bg-card rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-bold text-cyber-text-muted">#{pick.rank}</span>
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: pick.color }}
                      />
                      <div>
                        <div className="text-sm font-bold text-white">{pick.symbol}</div>
                        <div className="text-xs text-cyber-text-muted">{pick.name}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-sm font-bold ${pick.period_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {pick.period_return >= 0 ? '+' : ''}{pick.period_return.toFixed(1)}%
                      </div>
                      <div className="text-xs text-cyber-text-muted">{pick.reason}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Groups */}
          {action_groups.length > 0 && (
            <div className="bg-cyber-bg-secondary rounded-lg p-4 border border-cyber-border-subtle">
              <h3 className="text-sm font-bold text-white mb-3">Action Signals</h3>
              <div className="space-y-2">
                {action_groups.map((group) => (
                  <div key={group.action} className="flex items-center gap-3">
                    <div className="flex items-center gap-2 min-w-[120px]">
                      {group.action === 'buy' && <CheckCircle className="w-4 h-4 text-green-400" />}
                      {group.action === 'watch' && <AlertCircle className="w-4 h-4 text-blue-400" />}
                      {group.action === 'reduce' && <TrendingDown className="w-4 h-4 text-yellow-400" />}
                      {group.action === 'avoid' && <XCircle className="w-4 h-4 text-red-400" />}
                      <span className={`text-sm font-bold capitalize
                        ${group.action === 'buy' ? 'text-green-400' : ''}
                        ${group.action === 'watch' ? 'text-blue-400' : ''}
                        ${group.action === 'reduce' ? 'text-yellow-400' : ''}
                        ${group.action === 'avoid' ? 'text-red-400' : ''}
                      `}>
                        {group.label}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {group.symbols.map(sym => (
                        <span key={sym} className="text-xs bg-cyber-bg-card px-2 py-1 rounded text-cyber-text-secondary">
                          {sym}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Key Insights */}
          {insights.length > 0 && (
            <div className="bg-cyber-bg-secondary rounded-lg p-4 border border-cyber-border-subtle">
              <h3 className="text-sm font-bold text-white mb-3">Key Insights</h3>
              <div className="space-y-2">
                {insights.map((insight, idx) => (
                  <div key={idx} className="flex items-start gap-3 text-sm">
                    <span className="text-lg">{insight.emoji}</span>
                    <span className="text-cyber-text-secondary">
                      {insight.highlight ? (
                        <>
                          {insight.text.split(insight.highlight)[0]}
                          <span className="text-white font-bold">{insight.highlight}</span>
                          {insight.text.split(insight.highlight)[1]}
                        </>
                      ) : insight.text}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Summary */}
          {(regime.risk_summary || regime.safe_summary) && (
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-cyber-bg-secondary rounded-lg p-3 border border-cyber-border-subtle">
                <div className="text-xs text-cyber-text-muted mb-1">Risk Assets</div>
                <div className="text-sm text-white">{regime.risk_summary || 'None'}</div>
              </div>
              <div className="bg-cyber-bg-secondary rounded-lg p-3 border border-cyber-border-subtle">
                <div className="text-xs text-cyber-text-muted mb-1">Safe Haven</div>
                <div className="text-sm text-white">{regime.safe_summary || 'None'}</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default RRGRotationMap;
