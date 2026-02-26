import React from 'react'
import { Waves, TrendingUp, TrendingDown, Droplets, AlertTriangle, ArrowRightLeft } from 'lucide-react'

function MacroTide({ data }) {
  if (!data) return null

  const { 
    b1_raw_score, 
    b1_max_score, 
    b1_details, 
    leak_penalty, 
    leak_details,
    adjusted_score,
    regime,
    stance 
  } = data

  const getScoreColor = (score) => {
    if (score >= 4) return 'text-cyber-accent-green'
    if (score >= 3) return 'text-cyber-accent-yellow'
    if (score >= 2) return 'text-cyber-accent-orange'
    return 'text-cyber-accent-red'
  }

  const getBarGradient = (score) => {
    if (score >= 4) return 'from-cyber-accent-green to-cyber-accent-cyan'
    if (score >= 3) return 'from-cyber-accent-yellow to-cyber-accent-orange'
    if (score >= 2) return 'from-cyber-accent-orange to-cyber-accent-red'
    return 'from-cyber-accent-red to-cyber-accent-red-dim'
  }

  const indicators = [
    { key: 'NFCI', label: 'NFCI', description: 'Financial Conditions' },
    { key: 'HY_Spread', label: 'HY Spread', description: 'Credit Risk' },
    { key: 'MOVE', label: 'MOVE', description: 'Rate Volatility' },
    { key: 'CuAu_Ratio', label: 'Cu/Au', description: 'Growth Signal' },
    { key: 'Net_Liquidity', label: 'Net Liq', description: 'Fed Liquidity' }
  ]

  // Extract Gold Cannibalization data
  const goldCannibalization = leak_details?.gold_cannibalization
  const hasIndividualETFs = goldCannibalization?.individual_etfs && 
    Object.keys(goldCannibalization.individual_etfs).length > 0

  return (
    <div className="dashboard-card glow-green">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Waves className="w-6 h-6 text-cyber-accent-cyan" />
          <h2 className="text-xl font-bold text-white">🌊 Macro Tide</h2>
        </div>
        <span className="text-xs text-cyber-text-muted uppercase tracking-wider">B1 Scoring</span>
      </div>

      {/* B1 Raw Score */}
      <div className="mb-8">
        <div className="flex items-end justify-between mb-2">
          <span className="text-cyber-text-secondary">B1 Raw Score</span>
          <span className={`score-display ${getScoreColor(b1_raw_score)}`}>
            {b1_raw_score} <span className="text-2xl text-cyber-text-muted">/ {b1_max_score}</span>
          </span>
        </div>
        
        {/* Score Bar */}
        <div className="panic-bar">
          <div 
            className={`panic-bar-fill bg-gradient-to-r ${getBarGradient(b1_raw_score)}`}
            style={{ width: `${(b1_raw_score / b1_max_score) * 100}%` }}
          />
        </div>

        {/* Indicators Grid */}
        <div className="grid grid-cols-5 gap-3 mt-6">
          {indicators.map(({ key, label, description }) => {
            const detail = b1_details?.[key]
            return (
              <div key={key} className="text-center p-3 bg-cyber-bg-secondary rounded-lg">
                <div className="text-2xl mb-1">{detail?.status || '⚪'}</div>
                <div className="font-mono text-lg font-bold text-white">
                  {detail?.value !== null && detail?.value !== undefined 
                    ? detail.value : '--'}
                </div>
                <div className="text-xs text-cyber-accent-cyan font-medium">{label}</div>
                <div className="text-xs text-cyber-text-muted">{description}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Liquidity Leak Monitor */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Droplets className="w-5 h-5 text-cyber-accent-purple" />
          <h3 className="text-lg font-semibold text-white">🚰 Liquidity Leak Monitor</h3>
          <span className="ml-auto text-sm text-cyber-text-secondary">
            Leak Penalty: <span className="text-cyber-accent-red font-mono">{leak_penalty}</span>
          </span>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {leak_details && Object.entries(leak_details).map(([key, leak]) => {
            const isGoldCannibalization = key === 'gold_cannibalization'
            
            return (
              <div 
                key={key}
                className={`p-4 rounded-lg border ${
                  leak.active 
                    ? 'border-cyber-accent-red bg-cyber-accent-red/5' 
                    : 'border-cyber-border-subtle bg-cyber-bg-secondary'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-cyber-text-secondary capitalize">
                    {key.replace('_', ' ')}
                  </span>
                  <span className="text-sm font-semibold">{leak.status}</span>
                </div>
                
                {/* Gold Cannibalization Enhanced Display */}
                {isGoldCannibalization && hasIndividualETFs ? (
                  <div>
                    <div className="text-xs text-cyber-text-muted mb-2">
                      {leak.interpretation}
                      {leak.is_fallback && (
                        <span className="text-cyber-accent-orange ml-1">(Est.)</span>
                      )}
                    </div>
                    <div className="text-xs font-mono text-cyber-accent-cyan mb-2">
                      24h Flow: ${leak.flow_24h > 0 ? '+' : ''}{leak.flow_24h?.toFixed(1)}M
                      {leak.is_fallback && <span className="text-cyber-text-muted text-[10px] ml-1">~</span>}
                    </div>
                    
                    {/* Individual ETF Breakdown */}
                    <div className="mt-2 pt-2 border-t border-cyber-border-subtle">
                      <div className="text-xs text-cyber-text-muted mb-1">Top ETF Flows:</div>
                      <div className="space-y-1 max-h-24 overflow-y-auto">
                        {Object.entries(leak.individual_etfs)
                          .sort((a, b) => b[1].flow - a[1].flow)
                          .slice(0, 5)
                          .map(([ticker, etfData]) => (
                            <div key={ticker} className="flex justify-between text-xs">
                              <span className={ticker === 'GBTC' ? 'text-cyber-text-muted' : 'text-white'}>
                                {ticker}
                                {ticker === 'GBTC' && <span className="text-[10px] ml-1">(legacy)</span>}
                              </span>
                              <span className={etfData.flow >= 0 ? 'text-cyber-accent-green' : 'text-cyber-accent-red'}>
                                {etfData.flow > 0 ? '+' : ''}{etfData.flow.toFixed(1)}M
                              </span>
                            </div>
                          ))
                        }
                      </div>
                    </div>
                    
                    {/* Cumulative since launch */}
                    {leak.cumulative > 0 && (
                      <div className="mt-2 pt-2 border-t border-cyber-border-subtle text-xs text-cyber-text-muted">
                        Cumulative: ${(leak.cumulative / 1000).toFixed(1)}B since launch
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-xs text-cyber-text-muted">{leak.detail}</div>
                )}
                
                {leak.penalty !== 0 && (
                  <div className="mt-2 text-xs text-cyber-accent-red">
                    Penalty: {leak.penalty}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Adjusted Score */}
      <div className="pt-6 border-t border-cyber-border-subtle">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-cyber-text-secondary">Adjusted Score</span>
            <div className="text-sm text-cyber-text-muted mt-1">
              After liquidity leak penalties
            </div>
          </div>
          <div className="text-right">
            <span className={`score-display ${getScoreColor(adjusted_score)}`}>
              {adjusted_score} <span className="text-2xl text-cyber-text-muted">/ 5.0</span>
            </span>
            <div className={`text-lg font-bold mt-1 ${getScoreColor(adjusted_score)}`}>
              {regime}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MacroTide
