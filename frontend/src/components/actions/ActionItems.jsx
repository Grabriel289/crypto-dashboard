import React from 'react'
import { Target, AlertCircle, CheckCircle, TrendingUp, TrendingDown, Shield } from 'lucide-react'

function ActionItems({ data, summary }) {
  if (!data || data.length === 0) {
    return (
      <div className="dashboard-card">
        <div className="flex items-center gap-3 mb-4">
          <Target className="w-6 h-6 text-cyber-accent-green" />
          <h2 className="text-xl font-bold text-white">🎯 Prioritized Actions</h2>
        </div>
        <p className="text-cyber-text-secondary">No action items at this time. Market conditions are neutral.</p>
      </div>
    )
  }

  const getPriorityColor = (priority) => {
    if (priority === 'HIGH') return 'border-cyber-accent-red bg-cyber-accent-red/5'
    if (priority === 'MEDIUM') return 'border-cyber-accent-yellow bg-cyber-accent-yellow/5'
    return 'border-cyber-border-subtle bg-cyber-bg-secondary'
  }

  const getPriorityBadge = (priority) => {
    if (priority === 'HIGH') return 'bg-cyber-accent-red/20 text-cyber-accent-red'
    if (priority === 'MEDIUM') return 'bg-cyber-accent-yellow/20 text-cyber-accent-yellow'
    return 'bg-cyber-border-subtle text-cyber-text-secondary'
  }

  const getActionIcon = (action) => {
    const text = action.toLowerCase()
    if (text.includes('caution') || text.includes('reduce') || text.includes('avoid')) {
      return <TrendingDown className="w-5 h-5 text-cyber-accent-red" />
    }
    if (text.includes('accumul') || text.includes('add') || text.includes('buy')) {
      return <TrendingUp className="w-5 h-5 text-cyber-accent-green" />
    }
    if (text.includes('defensive') || text.includes('protect')) {
      return <Shield className="w-5 h-5 text-cyber-accent-cyan" />
    }
    return <Target className="w-5 h-5 text-cyber-accent-yellow" />
  }

  return (
    <div className="dashboard-card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Target className="w-6 h-6 text-cyber-accent-green" />
          <h2 className="text-xl font-bold text-white">🎯 Prioritized Actions</h2>
        </div>
        <span className="text-sm text-cyber-text-muted">
          {data.length} actionable items
        </span>
      </div>

      {/* Action List */}
      <div className="space-y-3">
        {data.map((action, index) => (
          <div 
            key={index}
            className={`p-4 rounded-lg border ${getPriorityColor(action.priority)} transition-all hover:border-cyber-border-accent`}
          >
            <div className="flex items-start gap-4">
              {/* Priority Badge */}
              <div className="flex flex-col items-center gap-1 min-w-[60px]">
                <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${getPriorityBadge(action.priority)}`}>
                  {action.priority}
                </span>
                <span className="text-2xl">{action.emoji}</span>
              </div>

              {/* Action Content */}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  {getActionIcon(action.action)}
                  <h3 className="text-lg font-bold text-white">
                    {action.action}
                  </h3>
                </div>
                <p className="text-sm text-cyber-text-secondary mb-2">
                  {action.reason}
                </p>
                {action.condition && (
                  <div className="flex items-center gap-2 text-xs text-cyber-accent-cyan bg-cyber-bg-secondary px-3 py-2 rounded">
                    <AlertCircle className="w-4 h-4" />
                    <span>{action.condition}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer Summary */}
      {summary && (
        <div className="mt-6 pt-4 border-t border-cyber-border-subtle">
          <div className="flex flex-wrap items-center justify-between gap-4 text-sm">
            <div className="flex items-center gap-4">
              <span className="text-cyber-text-muted">Regime:</span>
              <span className="font-bold text-white">{summary.regime}</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-cyber-text-muted">Stance:</span>
              <span className="font-bold text-white">{summary.stance}</span>
            </div>
            <div className="flex items-center gap-2 text-cyber-accent-green">
              <CheckCircle className="w-4 h-4" />
              <span>{data.length} items generated</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ActionItems
