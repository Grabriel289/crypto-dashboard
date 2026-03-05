import React from 'react'
import { AlertTriangle } from 'lucide-react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error(`[${this.props.name || 'Section'}] Error:`, error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
          <div className="flex items-center gap-3 text-cyber-text-muted">
            <AlertTriangle className="w-5 h-5 text-cyber-accent-orange" />
            <span className="text-sm">
              {this.props.name || 'Section'} failed to render
            </span>
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              className="ml-auto text-xs px-3 py-1 rounded border border-cyber-border-subtle hover:border-cyber-accent-green text-cyber-text-secondary hover:text-white transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

export default ErrorBoundary
