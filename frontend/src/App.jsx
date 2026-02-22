import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Header from './components/layout/Header'
import MacroTide from './components/macro/MacroTide'
import MarketPrices from './components/crypto/MarketPrices'
import CryptoPulse from './components/crypto/CryptoPulse'
import SectorRotation from './components/sectors/SectorRotation'
import ActionItems from './components/actions/ActionItems'
import ConflictingSignals from './components/alerts/ConflictingSignals'
import KeyLevelsCDC from './components/indicators/KeyLevelsCDC'
import LiquidationHeatmap from './components/indicators/LiquidationHeatmap'
import StablecoinFlow from './components/indicators/StablecoinFlow'
import EconomicCalendar from './components/indicators/EconomicCalendar'
import CorrelationMatrix from './components/indicators/CorrelationMatrix'
import Footer from './components/layout/Footer'

const API_URL = import.meta.env.VITE_API_URL || ''

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [refreshing, setRefreshing] = useState(false)

  const fetchData = async () => {
    try {
      setRefreshing(true)
      const response = await axios.get(`${API_URL}/api/full`)
      setData(response.data)
      setLastUpdated(new Date())
      setError(null)
    } catch (err) {
      console.error('Error fetching data:', err)
      setError('Failed to fetch dashboard data')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchData()
    // Auto-refresh every 30 seconds for live prices
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading && !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cyber-bg-primary">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyber-accent-green mx-auto mb-4"></div>
          <p className="text-cyber-text-secondary">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error && !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cyber-bg-primary">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-cyber-accent-red mb-2">Error Loading Dashboard</h2>
          <p className="text-cyber-text-secondary mb-4">{error}</p>
          <button 
            onClick={fetchData}
            className="px-6 py-2 bg-cyber-accent-green text-cyber-bg-primary font-semibold rounded-lg hover:bg-cyber-accent-green-dim transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-cyber-bg-primary grid-lines">
      <div className="max-w-[1600px] mx-auto px-4 py-6">
        <Header 
          lastUpdated={lastUpdated} 
          onRefresh={fetchData}
          isLoading={refreshing}
          regime={data?.macro?.regime}
        />
        
        <main className="space-y-6">
          {/* Section: Live Market Prices */}
          <section className="animate-fade-in">
            <MarketPrices data={data?.market_prices} />
          </section>
          
          {/* Section: Conflicting Signals Alert */}
          {data?.conflicts?.has_conflict && (
            <section className="animate-fade-in">
              <ConflictingSignals data={data?.conflicts} />
            </section>
          )}
          
          {/* Section: Key Levels & CDC Signal */}
          <section className="animate-fade-in" style={{ animationDelay: '0.05s' }}>
            <KeyLevelsCDC data={data?.key_levels} />
          </section>
          
          {/* Section: Liquidation Heatmap */}
          <section className="animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <LiquidationHeatmap data={data?.liquidation} />
          </section>
          
          {/* Section: Stablecoin Flow */}
          <section className="animate-fade-in" style={{ animationDelay: '0.15s' }}>
            <StablecoinFlow data={data?.stablecoin} />
          </section>
          
          {/* Section: Economic Calendar */}
          <section className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <EconomicCalendar data={data?.calendar} />
          </section>
          
          {/* Section: Correlation Matrix & PAXG/BTC */}
          <section className="animate-fade-in" style={{ animationDelay: '0.25s' }}>
            <CorrelationMatrix data={data?.correlation} />
          </section>
          
          {/* Section 1: Macro Tide */}
          <section className="animate-fade-in" style={{ animationDelay: '0.3s' }}>
            <MacroTide data={data?.macro} />
          </section>
          
          {/* Section 2: Crypto Pulse */}
          <section className="animate-fade-in" style={{ animationDelay: '0.35s' }}>
            <CryptoPulse data={data?.crypto_pulse} />
          </section>
          
          {/* Section 3: Sector Rotation */}
          <section className="animate-fade-in" style={{ animationDelay: '0.4s' }}>
            <SectorRotation data={data?.sectors} />
          </section>
          
          {/* Section 4: Action Items */}
          <section className="animate-fade-in" style={{ animationDelay: '0.45s' }}>
            <ActionItems data={data?.actions} summary={data?.macro} />
          </section>
        </main>
        
        <Footer />
      </div>
    </div>
  )
}

export default App
