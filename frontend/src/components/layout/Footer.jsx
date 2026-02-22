import React from 'react'
import { Github, Twitter, Globe } from 'lucide-react'

function Footer() {
  return (
    <footer className="mt-12 py-6 border-t border-cyber-border-subtle">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-cyber-text-muted">
        <div>
          <p>Crypto Market Dashboard v2.0</p>
          <p className="text-xs mt-1">
            Data sources: FRED, Binance, OKX, Alternative.me
          </p>
          <p className="text-xs mt-1 text-cyber-accent-blue">
            Built by <a href="https://github.com/0xAobby28" target="_blank" rel="noopener noreferrer" className="hover:underline">0xAobby28</a>
          </p>
        </div>
        
        <div className="flex items-center gap-6">
          <span>Not financial advice</span>
          <span className="text-cyber-text-secondary">|</span>
          <span>Updated hourly</span>
        </div>
      </div>
    </footer>
  )
}

export default Footer
