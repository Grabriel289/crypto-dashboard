import React, { useState } from 'react'
import { RefreshCw, TrendingUp, ChevronDown, ChevronUp, Trophy } from 'lucide-react'

function SectorRotation({ data }) {
  const [expandedSector, setExpandedSector] = useState(null)

  // DEBUG
  console.log('SectorRotation data:', data)

  if (!data) return null

  const { sectors, verdict, btc_momentum, macro_score } = data

  const getSignalColor = (signal) => {
    if (signal.includes('🟢')) return 'text-cyber-accent-green'
    if (signal.includes('🔴')) return 'text-cyber-accent-red'
    if (signal.includes('🟡')) return 'text-cyber-accent-yellow'
    if (signal.includes('🟠')) return 'text-cyber-accent-orange'
    return 'text-cyber-text-secondary'
  }

  const getSignalBg = (signal) => {
    if (signal.includes('🟢')) return 'bg-cyber-accent-green/10 border-cyber-accent-green'
    if (signal.includes('🔴')) return 'bg-cyber-accent-red/10 border-cyber-accent-red'
    if (signal.includes('🟡')) return 'bg-cyber-accent-yellow/10 border-cyber-accent-yellow'
    if (signal.includes('🟠')) return 'bg-cyber-accent-orange/10 border-cyber-accent-orange'
    return 'bg-cyber-bg-secondary border-cyber-border-subtle'
  }

  const getMomentumColor = (score) => {
    if (score >= 70) return 'text-cyber-accent-green'
    if (score >= 50) return 'text-cyber-accent-yellow'
    if (score >= 30) return 'text-cyber-accent-orange'
    return 'text-cyber-accent-red'
  }

  const getReturnColor = (value) => {
    if (value > 0) return 'text-cyber-accent-green'
    if (value < 0) return 'text-cyber-accent-red'
    return 'text-cyber-text-secondary'
  }

  const toggleExpand = (sectorName) => {
    setExpandedSector(expandedSector === sectorName ? null : sectorName)
  }

  return (
    <div className="dashboard-card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <RefreshCw className="w-6 h-6 text-cyber-accent-cyan" />
          <h2 className="text-xl font-bold text-white">🔄 Sector Momentum Ranking (14D vs BTC)</h2>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-cyber-text-secondary">BTC Momentum: <span className="text-white font-mono">{btc_momentum}</span></span>
          <span className="text-cyber-text-secondary">Macro Score: <span className="text-white font-mono">{macro_score}</span></span>
        </div>
      </div>

      {/* Verdict */}
      <div className="mb-6 p-4 bg-cyber-bg-secondary rounded-lg border border-cyber-border-subtle">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm text-cyber-text-secondary">Verdict</span>
        </div>
        <div className="text-xl font-bold text-white">
          {verdict?.verdict}
        </div>
        <div className="text-sm text-cyber-text-muted mt-1">
          {verdict?.reason}
        </div>
      </div>

      {/* Sector Table */}
      <div className="overflow-x-auto">
        <table className="sector-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Sector</th>
              <th>14D Return</th>
              <th>vs BTC</th>
              <th>Mom Score</th>
              <th>Signal</th>
              <th>Top 3 Coins</th>
            </tr>
          </thead>
          <tbody>
            {sectors?.map((sector, index) => {
              // Signal logic aligned with backend verdict
              const signal = sector.avg_vs_btc_14d > 5 ? '🟢 ROTATE IN' :
                            sector.avg_vs_btc_14d > 2 ? '🟡 WATCH' :
                            sector.avg_vs_btc_14d > 0 ? '⚪ NEUTRAL' :
                            sector.avg_vs_btc_14d > -5 ? '🟠 UNDERPERFORM' :
                            sector.avg_vs_btc_14d > -10 ? '🔴 AVOID' : '⚫ CAPITULATE'
              
              const isExpanded = expandedSector === sector.sector
              
              return (
                <React.Fragment key={sector.sector}>
                  <tr 
                    className="hover:bg-cyber-bg-hover cursor-pointer"
                    onClick={() => toggleExpand(sector.sector)}
                  >
                    <td className="font-mono text-cyber-text-secondary">{index + 1}</td>
                    <td>
                      <div className="flex flex-col">
                        <span className="font-bold text-white">{sector.sector}</span>
                        <span className="text-xs text-cyber-text-muted">{sector.description}</span>
                      </div>
                    </td>
                    <td className={`font-mono ${getReturnColor(sector.avg_return_14d)}`}>
                      {typeof sector.avg_return_14d === 'number' 
                        ? `${sector.avg_return_14d > 0 ? '+' : ''}${sector.avg_return_14d.toFixed(2)}%` 
                        : 'N/A'}
                    </td>
                    <td className={`font-mono ${getReturnColor(sector.avg_vs_btc_14d)}`}>
                      {typeof sector.avg_vs_btc_14d === 'number' 
                        ? `${sector.avg_vs_btc_14d > 0 ? '+' : ''}${sector.avg_vs_btc_14d.toFixed(2)}%` 
                        : 'N/A'}
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="w-16 panic-bar">
                          <div 
                            className={`panic-bar-fill ${sector.momentum_score >= 50 ? 'bg-cyber-accent-green' : sector.momentum_score >= 30 ? 'bg-cyber-accent-yellow' : 'bg-cyber-accent-red'}`}
                            style={{ width: `${sector.momentum_score}%` }}
                          />
                        </div>
                        <span className={`font-mono font-bold ${getMomentumColor(sector.momentum_score)}`}>
                          {sector.momentum_score}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className={`px-2 py-1 rounded text-xs font-semibold border ${getSignalBg(signal)} ${getSignalColor(signal)}`}>
                        {signal}
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-cyber-accent-cyan" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-cyber-text-muted" />
                        )}
                        <span className="text-xs text-cyber-text-secondary">
                          {sector.top_3_coins?.length || 0} coins
                        </span>
                      </div>
                    </td>
                  </tr>
                  
                  {/* Expanded row with top 3 coins */}
                  {isExpanded && sector.top_3_coins && (
                    <tr className="bg-cyber-bg-secondary/50">
                      <td colSpan="7" className="py-4">
                        <div className="px-4">
                          <h4 className="text-sm font-semibold text-cyber-text-secondary mb-3 flex items-center gap-2">
                            <Trophy className="w-4 h-4 text-cyber-accent-yellow" />
                            Top 3 Performers in {sector.sector}
                          </h4>
                          <div className="grid grid-cols-3 gap-4">
                            {sector.top_3_coins.map((coin, idx) => {
                              // DEBUG
                              console.log(`Coin ${coin.symbol}:`, { return_14d: coin.return_14d, vs_btc: coin.vs_btc })
                              
                              // Ensure values are numbers
                              const return14d = typeof coin.return_14d === 'number' ? coin.return_14d : 0
                              const vsBtc = typeof coin.vs_btc === 'number' ? coin.vs_btc : 0
                              
                              return (
                                <div 
                                  key={coin.symbol}
                                  className="bg-cyber-bg-card rounded-lg p-3 border border-cyber-border-subtle"
                                >
                                  <div className="flex items-center gap-2 mb-2">
                                    <span className="text-lg">
                                      {idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉'}
                                    </span>
                                    <span className="font-bold text-white">{coin.symbol}</span>
                                  </div>
                                  <div className={`text-sm font-mono ${getReturnColor(return14d)}`}>
                                    {return14d > 0 ? '+' : ''}{return14d.toFixed(2)}%
                                  </div>
                                  <div className={`text-xs ${getReturnColor(vsBtc)}`}>
                                    vs BTC: {vsBtc > 0 ? '+' : ''}{vsBtc.toFixed(2)}%
                                  </div>
                                  {coin.data_source && (
                                    <div className="text-xs text-cyber-text-muted mt-1">
                                      {coin.data_source === '14d_klines' ? '✓ 14D' :
                                       coin.data_source === 'kucoin' ? '🔶 KuCoin' :
                                       coin.data_source === 'coingecko' ? '🌎 CoinGecko' : '~24h'}
                                    </div>
                                  )}
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Recommended Allocation */}
      {verdict?.recommended_allocation && (
        <div className="mt-6 pt-4 border-t border-cyber-border-subtle">
          <h4 className="text-sm text-cyber-text-secondary mb-3">Recommended Allocation</h4>
          <div className="flex flex-wrap gap-3">
            {Object.entries(verdict.recommended_allocation).map(([key, value]) => (
              <div key={key} className="px-4 py-2 bg-cyber-bg-secondary rounded-lg border border-cyber-border-subtle">
                <span className="text-xs text-cyber-text-muted">{key}</span>
                <div className="font-bold text-white">{value}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default SectorRotation
