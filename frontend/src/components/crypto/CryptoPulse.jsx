import React from 'react'
import { Activity, Heart, TrendingUp, Anchor, DollarSign } from 'lucide-react'
import FragilityCard from './FragilityCard'
import FundingCard from './FundingCard'
import WhaleCard from './WhaleCard'

function CryptoPulse({ data }) {
  if (!data) return null

  const { fear_greed, fragility, funding, whale } = data

  const getFearGreedColor = (value) => {
    if (value <= 10) return 'text-cyber-accent-red'
    if (value <= 25) return 'text-cyber-accent-orange'
    if (value <= 45) return 'text-cyber-accent-yellow'
    if (value <= 55) return 'text-cyber-accent-yellow'
    if (value <= 75) return 'text-cyber-accent-green'
    return 'text-cyber-accent-green'
  }

  const getFearGreedBg = (value) => {
    if (value <= 25) return 'from-cyber-accent-red to-cyber-accent-orange'
    if (value <= 50) return 'from-cyber-accent-yellow to-cyber-accent-orange'
    if (value <= 75) return 'from-cyber-accent-green to-cyber-accent-yellow'
    return 'from-cyber-accent-green to-cyber-accent-cyan'
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <Activity className="w-6 h-6 text-cyber-accent-green" />
        <h2 className="text-xl font-bold text-white">═══════════════════════ SECTION 2: CRYPTO PULSE ═══════════════════════</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Fear & Greed */}
        <div className="dashboard-card">
          <div className="flex items-center gap-2 mb-4">
            <Heart className="w-5 h-5 text-cyber-accent-red" />
            <span className="text-lg font-semibold text-white">😱 Fear & Greed</span>
          </div>
          
          {fear_greed ? (
            <div className="text-center">
              <div className={`text-5xl font-bold font-mono mb-2 ${getFearGreedColor(fear_greed.value)} text-glow`}>
                {fear_greed.value} <span className="text-2xl text-cyber-text-muted">/ 100</span>
              </div>
              
              {/* Gauge */}
              <div className="panic-bar my-4">
                <div 
                  className={`panic-bar-fill bg-gradient-to-r ${getFearGreedBg(fear_greed.value)}`}
                  style={{ width: `${fear_greed.value}%` }}
                />
              </div>
              
              <div className={`text-xl font-bold ${getFearGreedColor(fear_greed.value)}`}>
                {fear_greed.label}
              </div>
              
              {fear_greed.probability && (
                <div className="mt-3 p-3 bg-cyber-bg-secondary rounded-lg">
                  <div className="text-sm text-cyber-text-secondary">{fear_greed.probability}</div>
                  <div className="text-xs text-cyber-text-muted mt-1">Action: {fear_greed.action}</div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-cyber-text-muted">No data</div>
          )}
        </div>

        {/* Market Fragility */}
        <FragilityCard data={fragility} />

        {/* Funding Rates */}
        <FundingCard data={funding} />

        {/* Whale Activity */}
        <WhaleCard data={whale} />
      </div>
    </div>
  )
}

export default CryptoPulse
