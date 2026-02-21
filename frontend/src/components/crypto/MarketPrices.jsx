import React from 'react'
import { DollarSign, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react'

function MarketPrices({ data }) {
  // Debug: log what we receive
  console.log('MarketPrices received data:', data)

  if (!data) {
    return (
      <div className="dashboard-card mb-6">
        <div className="flex items-center gap-3 mb-4">
          <DollarSign className="w-6 h-6 text-cyber-accent-green" />
          <h2 className="text-xl font-bold text-white">💰 Market Prices</h2>
        </div>
        <p className="text-cyber-text-secondary">Loading prices...</p>
      </div>
    )
  }

  if (!data.prices) {
    return (
      <div className="dashboard-card mb-6">
        <div className="flex items-center gap-3 mb-4">
          <DollarSign className="w-6 h-6 text-cyber-accent-green" />
          <h2 className="text-xl font-bold text-white">💰 Market Prices</h2>
        </div>
        <p className="text-cyber-text-secondary">No price data available. Backend may need restart.</p>
      </div>
    )
  }

  const { prices } = data

  const formatPrice = (price) => {
    if (price >= 1000) {
      return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    }
    return `$${price.toFixed(2)}`
  }

  const formatVolume = (volume) => {
    if (volume >= 1e9) return `$${(volume / 1e9).toFixed(1)}B`
    if (volume >= 1e6) return `$${(volume / 1e6).toFixed(1)}M`
    return `$${volume.toFixed(0)}`
  }

  const getChangeColor = (change) => {
    if (change > 0) return 'text-cyber-accent-green'
    if (change < 0) return 'text-cyber-accent-red'
    return 'text-cyber-text-secondary'
  }

  const getChangeIcon = (change) => {
    if (change > 0) return <TrendingUp className="w-4 h-4" />
    if (change < 0) return <TrendingDown className="w-4 h-4" />
    return null
  }

  const coins = ['BTC', 'ETH', 'SOL']

  return (
    <div className="dashboard-card mb-6">
      <div className="flex items-center gap-3 mb-4">
        <DollarSign className="w-6 h-6 text-cyber-accent-green" />
        <h2 className="text-xl font-bold text-white">💰 Market Prices</h2>
        <span className="text-xs text-cyber-text-muted ml-auto">Live Data</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {coins.map((coin) => {
          const coinData = prices[coin]
          if (!coinData) {
            return (
              <div key={coin} className="bg-cyber-bg-secondary rounded-lg p-4 border border-cyber-border-subtle">
                <span className="text-white font-bold">{coin}</span>
                <p className="text-sm text-cyber-text-muted">No data</p>
              </div>
            )
          }

          const change = coinData.change_24h || 0
          const isPositive = change >= 0

          return (
            <div 
              key={coin} 
              className="bg-cyber-bg-secondary rounded-lg p-4 border border-cyber-border-subtle hover:border-cyber-border-accent transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-lg font-bold text-white">{coin}</span>
                <span className={`flex items-center gap-1 text-sm font-medium ${getChangeColor(change)}`}>
                  {getChangeIcon(change)}
                  {isPositive ? '+' : ''}{change.toFixed(2)}%
                </span>
              </div>
              
              <div className="text-2xl font-mono font-bold text-white mb-2">
                {formatPrice(coinData.price)}
              </div>
              
              <div className="flex items-center justify-between text-xs text-cyber-text-secondary">
                <span className="flex items-center gap-1">
                  <BarChart3 className="w-3 h-3" />
                  24h Vol: {formatVolume(coinData.volume_24h || 0)}
                </span>
                <span className="text-cyber-text-muted">
                  {coinData.source || 'binance'}
                </span>
              </div>
              
              <div className="mt-2 flex items-center justify-between text-xs">
                <span className="text-cyber-text-muted">H: {formatPrice(coinData.high_24h || 0)}</span>
                <span className="text-cyber-text-muted">L: {formatPrice(coinData.low_24h || 0)}</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default MarketPrices
