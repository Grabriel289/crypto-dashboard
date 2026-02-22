import React from 'react';
import { Scale, CheckCircle, XCircle, Clock } from 'lucide-react';

function FinalVerdict({ data }) {
  if (!data) {
    return (
      <section className="bg-cyber-bg-secondary rounded-xl border-2 border-dashed border-cyber-border-subtle p-6 mt-6">
        <div className="text-center text-cyber-text-muted">
          <Scale className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p>Final Verdict loading...</p>
        </div>
      </section>
    );
  }

  const { stance, do_list, dont_list, wait_for } = data;

  // Color mapping for stance
  const stanceColors = {
    'AGGRESSIVE': { bg: 'bg-green-500/20', border: 'border-green-500', text: 'text-green-400', emoji: '🟢' },
    'BALANCED': { bg: 'bg-yellow-500/20', border: 'border-yellow-500', text: 'text-yellow-400', emoji: '🟡' },
    'DEFENSIVE ACCUMULATION': { bg: 'bg-orange-500/20', border: 'border-orange-500', text: 'text-orange-400', emoji: '🟠' },
    'RISK-OFF / WAIT': { bg: 'bg-red-500/20', border: 'border-red-500', text: 'text-red-400', emoji: '🔴' }
  };

  const stanceStyle = stance ? stanceColors[stance.text] || stanceColors['BALANCED'] : stanceColors['BALANCED'];

  return (
    <section className="relative bg-gradient-to-br from-cyber-bg-secondary to-cyber-surface rounded-xl border-2 border-cyber-border-accent p-6 mt-8 overflow-hidden">
      {/* Glow effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-cyber-accent-green/5 via-transparent to-cyber-accent-blue/5 pointer-events-none" />
      
      {/* Header */}
      <div className="relative flex items-center gap-3 mb-6 pb-4 border-b-2 border-cyber-border-accent">
        <div className="p-2 bg-cyber-accent-green/20 rounded-lg">
          <Scale className="w-6 h-6 text-cyber-accent-green" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white tracking-wide">FINAL VERDICT</h2>
          <p className="text-xs text-cyber-text-muted uppercase tracking-wider">Action Summary</p>
        </div>
      </div>

      {/* Stance Badge - Big and Centered */}
      {stance && (
        <div className="relative flex justify-center mb-8">
          <div className={`flex items-center gap-3 px-8 py-4 rounded-xl border-2 ${stanceStyle.bg} ${stanceStyle.border} shadow-lg`}>
            <span className="text-3xl">{stance.emoji}</span>
            <div>
              <div className="text-xs text-cyber-text-muted uppercase tracking-wider mb-1">Current Stance</div>
              <div className={`text-xl font-bold ${stanceStyle.text}`}>{stance.text}</div>
            </div>
          </div>
        </div>
      )}

      {/* DO and DON'T columns */}
      <div className="relative grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* DO Column */}
        <div className="bg-green-500/5 border border-green-500/30 rounded-xl p-5">
          <div className="flex items-center gap-2 text-green-400 font-bold mb-4 text-lg pb-2 border-b border-green-500/30">
            <CheckCircle className="w-5 h-5" />
            <span>DO</span>
          </div>
          <ul className="space-y-3">
            {do_list?.length > 0 ? do_list.map((item, i) => (
              <li key={i} className="text-cyber-text-secondary flex items-start gap-3">
                <span className="text-green-400 mt-0.5">✓</span>
                <span className="text-sm">{item}</span>
              </li>
            )) : (
              <li className="text-cyber-text-muted text-sm italic">No specific actions recommended</li>
            )}
          </ul>
        </div>

        {/* DON'T Column */}
        <div className="bg-red-500/5 border border-red-500/30 rounded-xl p-5">
          <div className="flex items-center gap-2 text-red-400 font-bold mb-4 text-lg pb-2 border-b border-red-500/30">
            <XCircle className="w-5 h-5" />
            <span>DON&apos;T</span>
          </div>
          <ul className="space-y-3">
            {dont_list?.length > 0 ? dont_list.map((item, i) => (
              <li key={i} className="text-cyber-text-secondary flex items-start gap-3">
                <span className="text-red-400 mt-0.5">✗</span>
                <span className="text-sm">{item}</span>
              </li>
            )) : (
              <li className="text-cyber-text-muted text-sm italic">No specific warnings</li>
            )}
          </ul>
        </div>
      </div>

      {/* WAIT FOR tags */}
      {wait_for && wait_for.length > 0 && (
        <div className="relative bg-cyber-surface/50 rounded-xl p-4 border border-cyber-border-subtle">
          <div className="flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-2 text-cyber-accent-blue">
              <Clock className="w-4 h-4" />
              <span className="font-semibold text-sm">WAIT FOR:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {wait_for.map((item, i) => (
                <span
                  key={i}
                  className="bg-cyber-accent-blue/20 text-cyber-accent-blue px-4 py-1.5 rounded-full text-sm font-medium border border-cyber-accent-blue/30"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default FinalVerdict;
