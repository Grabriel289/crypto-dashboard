import React from 'react'
import { Anchor } from 'lucide-react'

function WhaleCard({ data }) {
  if (!data) return null

  const { total_oi, oi_change_24h, exchange_flow, signal, bias, description } = data

  const getBiasColor = (bias) => {
    if (bias === 'bullish') return 'text-cyber-accent-green'
    if (bias === 'bearish') return 'text-cyber-accent-red'
    return 'text-cyber-accent-yellow'
  }

  const formatOI = (value) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
    return `$${value.toFixed(2)}`
  }

  return (
    <div className="dashboard-card">
      <div className="flex items-center gap-2 mb-4">
        <Anchor className="w-5 h-5 text-cyber-accent-purple" />
        <span className="text-lg font-semibold text-white">🐋 Whale Activity</span>
      </div>
      
      {/* OI Stats */}
      <div className="space-y-3 mb-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-cyber-text-secondary">Total OI</span>
          <span className="font-mono font-bold text-white">{formatOI(total_oi)}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-cyber-text-secondary">OI 24h</span>
          <span className={`font-mono font-bold ${oi_change_24h > 0 ? 'text-cyber-accent-green' : 'text-cyber-accent-red'}`}>
            {oi_change_24h > 0 ? '+' : ''}{oi_change_24h.toFixed(1)}%
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-cyber-text-secondary">Exchange Flow</span>
          <span className={`font-mono font-bold ${exchange_flow < 0 ? 'text-cyber-accent-green' : 'text-cyber-accent-red'}`}>
            {exchange_flow > 0 ? '+' : ''}{exchange_flow.toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Signal */}
      <div className="pt-3 border-t border-cyber-border-subtle">
        <div className="text-xs text-cyber-text-muted mb-1">Signal</div>
        <div className={`font-semibold ${getBiasColor(bias)}`}>
          {signal}
        </div>
        <div className="text-xs text-cyber-text-muted mt-1">
          {description}
        </div>
      </div>
    </div>
  )
}

export default WhaleCard
