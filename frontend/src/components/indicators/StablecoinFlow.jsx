import React from 'react';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

function StablecoinFlow({ data }) {
  if (!data) return null;

  const { stablecoins, total_supply, total_change_7d, insight } = data;

  const getMaxSupply = () => {
    if (!stablecoins?.length) return 150;
    return Math.max(...stablecoins.map(s => s.supply));
  };

  const maxSupply = getMaxSupply();

  return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
      <div className="flex items-center gap-2 mb-6">
        <span className="text-2xl">💵</span>
        <h2 className="text-xl font-bold text-cyber-text-primary">STABLECOIN FLOW MONITOR</h2>
      </div>

      <div className="space-y-6">
        {stablecoins?.map((coin) => {
          const isPositive = coin.change_7d >= 0;
          const barWidth = (coin.supply / maxSupply) * 100;
          
          return (
            <div key={coin.symbol} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="font-bold text-lg">{coin.symbol}</span>
                  <span className="font-mono text-cyber-text-primary">${coin.supply}B</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`flex items-center gap-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                    {isPositive ? '+' : ''}{coin.change_7d}B (7d)
                  </span>
                  <span className={`px-2 py-1 rounded text-sm font-bold ${isPositive ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                    {coin.emoji} {coin.status}
                  </span>
                </div>
              </div>
              
              {/* Progress Bar */}
              <div className="h-4 bg-cyber-surface rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${isPositive ? 'bg-green-500' : 'bg-red-500'}`}
                  style={{ width: `${barWidth}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Total */}
      <div className="mt-6 pt-6 border-t border-cyber-border-subtle">
        <div className="flex items-center justify-between text-lg font-bold">
          <span>Total:</span>
          <span className="text-cyber-text-primary">${total_supply}B</span>
          <span className={`flex items-center gap-1 ${total_change_7d >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {total_change_7d >= 0 ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
            {total_change_7d >= 0 ? '+' : ''}{total_change_7d}B (7d)
          </span>
        </div>
      </div>

      {/* Insight */}
      <div className="mt-4 bg-cyber-surface rounded-lg p-4 border border-cyber-border-subtle">
        <p className="text-cyber-text-primary">{insight}</p>
      </div>
    </section>
  );
}

export default StablecoinFlow;
