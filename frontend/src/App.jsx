import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Header from './components/layout/Header'
import MacroTide from './components/macro/MacroTide'
import MarketPrices from './components/crypto/MarketPrices'
import CryptoPulse from './components/crypto/CryptoPulse'
import SectorRotation from './components/sectors/SectorRotation'
import ActionItems from './components/actions/ActionItems'
import FinalVerdict from './components/actions/FinalVerdict'
import ConflictingSignals from './components/alerts/ConflictingSignals'
import KeyLevelsCDC from './components/indicators/KeyLevelsCDC'
import StablecoinFlow from './components/indicators/StablecoinFlow'
import EconomicCalendar from './components/indicators/EconomicCalendar'
import CorrelationMatrix from './components/indicators/CorrelationMatrix'
import { RRGRotationMap } from './components/rrg'
import ABMPanel from './components/abm'
import Footer from './components/layout/Footer'
import ErrorBoundary from './components/layout/ErrorBoundary'

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
      const response = await axios.get(`${API_URL}/api/full?t=${Date.now()}`)
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
          <section className="animate-fade-in">
            <ErrorBoundary name="Market Prices">
              <MarketPrices data={data?.market_prices} />
            </ErrorBoundary>
          </section>

          {data?.conflicts?.has_conflict && (
            <section className="animate-fade-in">
              <ErrorBoundary name="Conflicting Signals">
                <ConflictingSignals data={data?.conflicts} />
              </ErrorBoundary>
            </section>
          )}

          <section className="animate-fade-in" style={{ animationDelay: '0.05s' }}>
            <ErrorBoundary name="Key Levels & CDC">
              <KeyLevelsCDC data={data?.key_levels} />
            </ErrorBoundary>
          </section>

          <section className="animate-fade-in" style={{ animationDelay: '0.15s' }}>
            <ErrorBoundary name="Stablecoin Flow">
              <StablecoinFlow data={data?.stablecoin} />
            </ErrorBoundary>
          </section>

          <section className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <ErrorBoundary name="Economic Calendar">
              <EconomicCalendar data={data?.calendar} />
            </ErrorBoundary>
          </section>

          <section className="animate-fade-in" style={{ animationDelay: '0.22s' }}>
            <ErrorBoundary name="RRG Rotation Map">
              <RRGRotationMap data={data?.rrg_rotation} />
            </ErrorBoundary>
          </section>

          <section className="animate-fade-in" style={{ animationDelay: '0.3s' }}>
            <ErrorBoundary name="Macro Tide">
              <MacroTide data={data?.macro} />
            </ErrorBoundary>
          </section>

          <section className="animate-fade-in" style={{ animationDelay: '0.35s' }}>
            <ErrorBoundary name="Crypto Pulse">
              <CryptoPulse data={data?.crypto_pulse} />
            </ErrorBoundary>
          </section>

          <section className="animate-fade-in" style={{ animationDelay: '0.37s' }}>
            <ErrorBoundary name="Altcoin Season Index">
              <ABMPanel data={data?.abm} />
            </ErrorBoundary>
          </section>

          <section className="animate-fade-in" style={{ animationDelay: '0.4s' }}>
            <ErrorBoundary name="Sector Rotation">
              <SectorRotation data={data?.sectors} />
            </ErrorBoundary>
          </section>

          <section className="animate-fade-in" style={{ animationDelay: '0.45s' }}>
            <ErrorBoundary name="Action Items">
              <ActionItems data={data?.actions} summary={data?.macro} />
            </ErrorBoundary>
          </section>

          <section className="animate-fade-in" style={{ animationDelay: '0.5s' }}>
            <ErrorBoundary name="Final Verdict">
              <FinalVerdict data={data?.final_verdict} />
            </ErrorBoundary>
          </section>
        </main>
        
        <Footer />
      </div>
    </div>
  )
}

export default App
