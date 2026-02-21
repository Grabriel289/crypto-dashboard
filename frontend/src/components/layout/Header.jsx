import React from 'react'
import { RefreshCw, Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react'

function Header({ lastUpdated, onRefresh, isLoading, regime }) {
  const formatTime = (date) => {
    if (!date) return '--:--:--'
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getRegimeColor = (regime) => {
    if (!regime) return 'text-cyber-text-secondary'
    if (regime.includes('🟢')) return 'text-cyber-accent-green'
    if (regime.includes('🔴')) return 'text-cyber-accent-red'
    if (regime.includes('🟡')) return 'text-cyber-accent-yellow'
    if (regime.includes('🟠')) return 'text-cyber-accent-orange'
    return 'text-cyber-text-secondary'
  }

  return (
    <header className="mb-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold flex items-center gap-3">
            <span className="gradient-text-green">Crypto</span>
            <span className="text-white">Dashboard</span>
            <Activity className="w-6 h-6 text-cyber-accent-cyan" />
          </h1>
          <p className="text-cyber-text-secondary mt-1">
            Market Condition & Sector Rotation Monitor
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Regime Badge */}
          {regime && (
            <div className={`status-badge ${getRegimeColor(regime)}`}>
              {regime}
            </div>
          )}
          
          {/* Last Updated */}
          <div className="text-right">
            <p className="text-xs text-cyber-text-muted uppercase tracking-wider">Last Updated</p>
            <p className="text-sm font-mono text-cyber-text-secondary">
              {formatTime(lastUpdated)}
            </p>
          </div>
          
          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className={`p-2 rounded-lg border border-cyber-border-subtle hover:border-cyber-accent-green hover:bg-cyber-accent-green/10 transition-all ${
              isLoading ? 'animate-spin' : ''
            }`}
          >
            <RefreshCw className="w-5 h-5 text-cyber-accent-green" />
          </button>
        </div>
      </div>
      
      {/* Date Bar */}
      <div className="mt-4 pt-4 border-t border-cyber-border-subtle flex items-center justify-between text-sm">
        <div className="text-cyber-text-secondary">
          {new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </div>
        <div className="flex items-center gap-2 text-cyber-text-muted">
          <span className="w-2 h-2 rounded-full bg-cyber-accent-green animate-pulse"></span>
          <span>Live Data</span>
        </div>
      </div>
    </header>
  )
}

export default Header
