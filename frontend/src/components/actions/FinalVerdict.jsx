import React from 'react';

function FinalVerdict({ data }) {
  if (!data) return null;

  const { stance, do_list, dont_list, wait_for } = data;

  return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6 mt-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">🎯</span>
        <h2 className="text-xl font-bold text-cyber-text-primary">FINAL VERDICT</h2>
      </div>

      {/* Stance Badge */}
      {stance && (
        <div
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border mb-6"
          style={{
            backgroundColor: stance.bgColor,
            borderColor: stance.borderColor
          }}
        >
          <span className="text-xl">{stance.emoji}</span>
          <span className="font-bold text-white">STANCE: {stance.text}</span>
        </div>
      )}

      {/* DO and DON'T columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {/* DO Column */}
        <div className="bg-cyber-surface rounded-lg p-4">
          <div className="text-green-400 font-bold mb-3 text-lg border-b border-cyber-border-subtle pb-2">
            ✅ DO
          </div>
          <ul className="space-y-2">
            {do_list?.map((item, i) => (
              <li key={i} className="text-cyber-text-secondary text-sm flex items-start gap-2">
                <span className="text-gray-500 mt-1">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* DON'T Column */}
        <div className="bg-cyber-surface rounded-lg p-4">
          <div className="text-red-400 font-bold mb-3 text-lg border-b border-cyber-border-subtle pb-2">
            ❌ DON'T
          </div>
          <ul className="space-y-2">
            {dont_list?.map((item, i) => (
              <li key={i} className="text-cyber-text-secondary text-sm flex items-start gap-2">
                <span className="text-gray-500 mt-1">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* WAIT FOR tags */}
      {wait_for && wait_for.length > 0 && (
        <div className="border-t border-cyber-border-subtle pt-4">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-cyber-text-muted text-sm">⏳ WAIT FOR:</span>
            <div className="flex flex-wrap gap-2">
              {wait_for.map((item, i) => (
                <span
                  key={i}
                  className="bg-cyber-surface text-cyber-accent-blue px-3 py-1 rounded-full text-xs font-medium border border-cyber-border-subtle"
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
