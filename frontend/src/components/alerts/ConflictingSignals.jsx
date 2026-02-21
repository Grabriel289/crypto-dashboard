import React from 'react'
import { AlertTriangle, TrendingUp, TrendingDown, Shield } from 'lucide-react'

function ConflictingSignals({ data }) {
  if (!data || !data.has_conflict) return null

  const { conflict_level, bullish_signals, bearish_signals, recommendation, summary } = data

  const getLevelColor = () => {
    if (conflict_level === 'HIGH') return 'border-cyber-accent-red bg-cyber-accent-red/10'
    return 'border-cyber-accent-yellow bg-cyber-accent-yellow/10'
  }

  const getLevelTextColor = () => {
    if (conflict_level === 'HIGH') return 'text-cyber-accent-red'
    return 'text-cyber-accent-yellow'
  }

  return (
    <div className={`dashboard-card mb-6 border-2 ${getLevelColor()}`}>
      <div className="flex items-center gap-3 mb-4">
        <AlertTriangle className={`w-6 h-6 ${getLevelTextColor()}`} />
        <h2 className={`text-xl font-bold ${getLevelTextColor()}`}>
          ⚠️ Conflicting Signals Detected
        </h2>
        <span className={`ml-auto px-2 py-1 rounded text-xs font-bold uppercase ${getLevelTextColor()} bg-cyber-bg-secondary`}>
          {conflict_level} PRIORITY
        </span>
      </div>

      <p className="text-cyber-text-secondary mb-4">{summary}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Bullish Signals */}
        <div className="bg-cyber-bg-secondary rounded-lg p-4 border border-cyber-accent-green/30">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-5 h-5 text-cyber-accent-green" />
            <h3 className="font-bold text-cyber-accent-green">Bullish Signals</h3>
          </div>
          {bullish_signals.length > 0 ? (
            <ul className="space-y-2">
              {bullish_signals.map((sig, idx) => (
                <li key={idx} className="text-sm">
                  <span className="text-white font-medium">{sig.indicator}:</span>
                  <span className="text-cyber-text-secondary ml-1">{sig.signal}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-cyber-text-muted">No strong bullish signals</p>
          )}
        </div>

        {/* Bearish Signals */}
        <div className="bg-cyber-bg-secondary rounded-lg p-4 border border-cyber-accent-red/30">
          <div className="flex items-center gap-2 mb-3">
            <TrendingDown className="w-5 h-5 text-cyber-accent-red" />
            <h3 className="font-bold text-cyber-accent-red">Bearish Signals</h3>
          </div>
          {bearish_signals.length > 0 ? (
            <ul className="space-y-2">
              {bearish_signals.map((sig, idx) => (
                <li key={idx} className="text-sm">
                  <span className="text-white font-medium">{sig.indicator}:</span>
                  <span className="text-cyber-text-secondary ml-1">{sig.signal}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-cyber-text-muted">No strong bearish signals</p>
          )}
        </div>
      </div>

      {/* Recommendation */}
      {recommendation && (
        <div className="bg-cyber-bg-secondary rounded-lg p-4 border border-cyber-border-subtle">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="w-5 h-5 text-cyber-accent-cyan" />
            <h3 className="font-bold text-cyber-accent-cyan">Recommendation</h3>
          </div>
          <p className="text-white">{recommendation}</p>
        </div>
      )}
    </div>
  )
}

export default ConflictingSignals
