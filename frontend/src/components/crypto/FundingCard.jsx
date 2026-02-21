import React from 'react'
import { Scale } from 'lucide-react'

function FundingCard({ data }) {
  if (!data) return null

  const { rates, aggregate } = data

  const getFundingColor = (bias) => {
    if (bias === 'bullish') return 'text-cyber-accent-green'
    if (bias === 'bearish') return 'text-cyber-accent-red'
    return 'text-cyber-accent-yellow'
  }

  const getFundingBg = (bias) => {
    if (bias === 'bullish') return 'bg-cyber-accent-green/10 border-cyber-accent-green'
    if (bias === 'bearish') return 'bg-cyber-accent-red/10 border-cyber-accent-red'
    return 'bg-cyber-accent-yellow/10 border-cyber-accent-yellow'
  }

  return (
    <div className="dashboard-card">
      <div className="flex items-center gap-2 mb-4">
        <Scale className="w-5 h-5 text-cyber-accent-cyan" />
        <span className="text-lg font-semibold text-white">⚖️ Funding Rates</span>
      </div>
      
      {/* Individual rates */}
      <div className="space-y-2 mb-4">
        {rates && Object.entries(rates).map(([coin, info]) => (
          <div 
            key={coin}
            className={`flex items-center justify-between p-2 rounded-lg border ${getFundingBg(info.bias)}`}
          >
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-white">{coin}</span>
            </div>
            <div className="text-right">
              <div className={`font-mono text-sm font-bold ${getFundingColor(info.bias)}`}>
                {(info.rate * 100).toFixed(3)}%
              </div>
              <div className="text-xs text-cyber-text-muted">{info.emoji}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Aggregate signal */}
      {aggregate && (
        <div className="pt-3 border-t border-cyber-border-subtle">
          <div className="text-xs text-cyber-text-muted mb-1">Signal</div>
          <div className={`font-semibold ${getFundingColor(aggregate.bias)}`}>
            {aggregate.overall_signal}
          </div>
          <div className="text-xs text-cyber-text-muted mt-1">
            {aggregate.description}
          </div>
        </div>
      )}
    </div>
  )
}

export default FundingCard
