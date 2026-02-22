import React from 'react';
import { Calendar, AlertCircle } from 'lucide-react';

function EconomicCalendar({ data }) {
  if (!data) return null;

  const { macro_events, crypto_events, key_event, date_range } = data;

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getDayName = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  };

  return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
      <div className="flex items-center gap-2 mb-6">
        <span className="text-2xl">📅</span>
        <h2 className="text-xl font-bold text-cyber-text-primary">
          ECONOMIC CALENDAR (Next 7 Days)
        </h2>
      </div>

      {/* Macro Events */}
      <div className="mb-6">
        <h3 className="text-lg font-bold text-cyber-text-secondary mb-3 flex items-center gap-2">
          🏛️ MACRO EVENTS
        </h3>
        <div className="space-y-2">
          {macro_events?.map((event, idx) => (
            <div key={idx} className="flex items-center gap-4 py-2 border-b border-cyber-border-subtle last:border-0">
              <div className="w-24 text-cyber-text-secondary">
                {formatDate(event.date)} {getDayName(event.date)}
              </div>
              <div className="w-16 text-cyber-text-muted">{event.time}</div>
              <div className="w-8 text-lg">{event.flag}</div>
              <div className="flex-1 text-cyber-text-primary">{event.event}</div>
              <div className={`px-2 py-1 rounded text-xs font-bold ${
                event.impact?.includes('CRITICAL') ? 'bg-red-500/20 text-red-400' :
                event.impact?.includes('HIGH') ? 'bg-orange-500/20 text-orange-400' :
                'bg-yellow-500/20 text-yellow-400'
              }`}>
                {event.impact}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Crypto Events */}
      <div className="mb-6">
        <h3 className="text-lg font-bold text-cyber-text-secondary mb-3 flex items-center gap-2">
          🪙 CRYPTO EVENTS
        </h3>
        <div className="space-y-2">
          {crypto_events?.map((event, idx) => (
            <div key={idx} className="flex items-center gap-4 py-2 border-b border-cyber-border-subtle last:border-0">
              <div className="w-24 text-cyber-text-secondary">
                {formatDate(event.date)} {getDayName(event.date)}
              </div>
              <div className="flex-1">
                <span className="text-cyber-text-primary">{event.event}</span>
                {event.amount && <span className="text-cyber-text-muted ml-2">({event.amount})</span>}
              </div>
              <div className={`text-sm ${
                event.impact?.includes('Bullish') ? 'text-green-400' :
                event.impact?.includes('Bearish') ? 'text-red-400' :
                'text-yellow-400'
              }`}>
                {event.impact}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Event */}
      {key_event && (
        <div className="bg-cyber-surface rounded-lg p-4 border border-cyber-border-subtle">
          <div className="flex items-center gap-2 text-yellow-400 mb-2">
            <AlertCircle size={18} />
            <span className="font-bold">KEY EVENT: {formatDate(key_event.date)} — {key_event.event}</span>
          </div>
          {key_event.insight && (
            <p className="text-cyber-text-secondary text-sm">{key_event.insight}</p>
          )}
        </div>
      )}
    </section>
  );
}

export default EconomicCalendar;
