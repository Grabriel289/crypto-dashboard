import React from 'react'
import { AlertTriangle } from 'lucide-react'

function FragilityCard({ data }) {
  if (!data) return null

  const { score, label, level, emoji } = data
  const displayLabel = label || level

  const getBarColor = (score) => {
    if (score >= 75) return 'from-cyber-accent-red to-cyber-accent-red-dim'
    if (score >= 50) return 'from-cyber-accent-orange to-cyber-accent-red'
    if (score >= 25) return 'from-cyber-accent-yellow to-cyber-accent-orange'
    return 'from-cyber-accent-green to-cyber-accent-cyan'
  }

  const assets = [
    { name: 'BTC', score: Math.max(0, score - 5) },
    { name: 'ETH', score: Math.max(0, score - 3) },
    { name: 'SOL', score: Math.min(100, score + 10) }
  ]

  return (
    <div className="dashboard-card">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-5 h-5 text-cyber-accent-orange" />
        <span className="text-lg font-semibold text-white">📊 Market Fragility</span>
      </div>
      
      {/* Asset fragility */}
      <div className="space-y-3 mb-4">
        {assets.map(asset => (
          <div key={asset.name} className="flex items-center gap-3">
            <span className="w-12 text-sm font-mono text-cyber-text-secondary">{asset.name}</span>
            <div className="flex-1 panic-bar">
              <div 
                className={`panic-bar-fill bg-gradient-to-r ${getBarColor(asset.score)}`}
                style={{ width: `${asset.score}%` }}
              />
            </div>
            <span className={`w-12 text-right font-mono text-sm ${
              asset.score >= 50 ? 'text-cyber-accent-red' : 
              asset.score >= 25 ? 'text-cyber-accent-yellow' : 'text-cyber-accent-green'
            }`}>
              {asset.score}
            </span>
          </div>
        ))}
      </div>

      <div className="pt-3 border-t border-cyber-border-subtle">
        <div className="flex items-center justify-between">
          <span className="text-sm text-cyber-text-secondary">Composite</span>
          <span className={`font-bold ${score >= 50 ? 'text-cyber-accent-orange' : 'text-cyber-accent-green'}`}>
            {score} {emoji} {displayLabel && <span className="text-sm font-normal opacity-75">{displayLabel}</span>}
          </span>
        </div>
      </div>
    </div>
  )
}

export default FragilityCard
