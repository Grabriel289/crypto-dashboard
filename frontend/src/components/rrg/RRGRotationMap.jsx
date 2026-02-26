import React from 'react';
import { Target, TrendingUp, TrendingDown, AlertCircle, CheckCircle, XCircle, Minus } from 'lucide-react';

// Exact colors from specification
const COLORS = {
  background: '#0d1117',
  cardBg: '#161b22',
  border: '#30363d',
  
  quadrant: {
    leading: 'rgba(63, 185, 80, 0.08)',
    weakening: 'rgba(210, 153, 34, 0.08)',
    lagging: 'rgba(248, 81, 73, 0.08)',
    improving: 'rgba(88, 166, 255, 0.08)',
  },
  
  quadrantLabel: {
    leading: '#3fb950',
    weakening: '#d29922',
    lagging: '#f85149',
    improving: '#58a6ff',
  },
  
  regime: {
    risk_on: '#3fb950',
    risk_off: '#f85149',
    neutral: '#d29922',
  },
  
  textPrimary: '#f0f6fc',
  textSecondary: '#8b949e',
  textMuted: '#6e7681',
  
  safeHavenBorder: '#ffd700',
  safeHavenGlow: 'rgba(255, 215, 0, 0.4)',
};

const ETF_COLORS = {
  IBIT: '#f7931a',
  ETHA: '#627eea',
  BOTZ: '#8b5cf6',
  QQQ: '#00d4aa',
  IWM: '#f85149',
  GLD: '#ffd700',
  TLT: '#4ade80',
  SHY: '#22d3ee',
  UUP: '#a3e635',
};

const QUADRANT_EMOJIS = {
  leading: '🚀',
  weakening: '⚠️',
  lagging: '📉',
  improving: '📈',
};

function RRGRotationMap({ data }) {
  if (!data) {
    return (
      <div style={{ 
        background: COLORS.cardBg, 
        border: `1px solid ${COLORS.border}`,
        borderRadius: '12px',
        padding: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Target size={24} color="#22d3ee" />
          <h2 style={{ fontSize: '18px', fontWeight: 'bold', color: COLORS.textPrimary, margin: 0 }}>
            🔄 RRG Rotation Map — Fund Flow Analysis
          </h2>
        </div>
        <p style={{ color: COLORS.textSecondary }}>Loading RRG data...</p>
      </div>
    );
  }

  if (data.error) {
    return (
      <div style={{ 
        background: COLORS.cardBg, 
        border: `1px solid ${COLORS.border}`,
        borderRadius: '12px',
        padding: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Target size={24} color="#22d3ee" />
          <h2 style={{ fontSize: '18px', fontWeight: 'bold', color: COLORS.textPrimary, margin: 0 }}>
            🔄 RRG Rotation Map
          </h2>
        </div>
        <p style={{ color: '#f85149' }}>Error: {data.error}</p>
      </div>
    );
  }

  const { 
    risk_assets = [], 
    safe_haven_assets = [], 
    regime = {}, 
    top_picks = [], 
    action_groups = [],
    insights = []
  } = data;

  // Combine all assets
  const allAssets = [...risk_assets, ...safe_haven_assets];
  
  if (allAssets.length === 0) {
    return (
      <div style={{ 
        background: COLORS.cardBg, 
        border: `1px solid ${COLORS.border}`,
        borderRadius: '12px',
        padding: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Target size={24} color="#22d3ee" />
          <h2 style={{ fontSize: '18px', fontWeight: 'bold', color: COLORS.textPrimary, margin: 0 }}>
            🔄 RRG Rotation Map
          </h2>
        </div>
        <p style={{ color: COLORS.textSecondary }}>No RRG data available</p>
      </div>
    );
  }

  // Calculate chart scaling
  const rsRatios = allAssets.map(a => a.coordinate?.rs_ratio).filter(v => typeof v === 'number');
  const rsMomentums = allAssets.map(a => a.coordinate?.rs_momentum).filter(v => typeof v === 'number');
  
  const minX = Math.min(...rsRatios, 95);
  const maxX = Math.max(...rsRatios, 105);
  const minY = Math.min(...rsMomentums, 95);
  const maxY = Math.max(...rsMomentums, 105);
  
  const rangeX = maxX - minX || 20;
  const rangeY = maxY - minY || 20;

  const scaleX = (val) => ((val - minX) / rangeX) * 100;
  const scaleY = (val) => 100 - ((val - minY) / rangeY) * 100;

  // Get regime color
  const regimeColor = COLORS.regime[regime.regime] || COLORS.regime.neutral;
  
  // Separate action groups
  const buyGroup = action_groups.find(g => g.action === 'buy');
  const watchGroup = action_groups.find(g => g.action === 'watch');
  const reduceGroup = action_groups.find(g => g.action === 'reduce');
  const avoidGroup = action_groups.find(g => g.action === 'avoid');

  return (
    <div style={{ 
      background: COLORS.cardBg, 
      border: `1px solid ${COLORS.border}`,
      borderRadius: '12px',
      padding: '20px'
    }}>
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Target size={24} color="#22d3ee" />
            <h2 style={{ 
              fontSize: '18px', 
              fontWeight: 'bold', 
              color: COLORS.textPrimary, 
              margin: 0 
            }}>
              🔄 RRG Rotation Map — Fund Flow Analysis
            </h2>
          </div>
          <p style={{ 
            fontSize: '12px', 
            color: COLORS.textMuted, 
            margin: '4px 0 0 36px' 
          }}>
            Relative Rotation Graph: Risk Assets vs Safe Haven (Benchmark: SPY)
          </p>
        </div>
        
        {/* Regime Badge */}
        {regime.regime && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            backgroundColor: `${regimeColor}20`,
            border: `1px solid ${regimeColor}40`,
            borderRadius: '8px'
          }}>
            <span style={{ fontSize: '20px' }}>{regime.emoji}</span>
            <span style={{ 
              fontWeight: 'bold', 
              color: regimeColor,
              fontSize: '14px'
            }}>
              {regime.regime.replace('_', '-').toUpperCase()}
            </span>
          </div>
        )}
      </div>

      {/* Main Content - 2 Columns */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 0.7fr', gap: '20px', alignItems: 'stretch' }}>
        {/* Left Column - RRG Chart */}
        <div>
          <div style={{
            background: COLORS.background,
            border: `2px solid ${COLORS.border}`,
            borderRadius: '8px',
            padding: '20px',
            position: 'relative',
            height: '460px'
          }}>
            {/* Quadrant Backgrounds */}
            <div style={{
              position: 'absolute',
              inset: '20px',
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gridTemplateRows: '1fr 1fr',
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              {/* Improving (Top-Left) - Blue */}
              <div style={{ background: COLORS.quadrant.improving, position: 'relative' }}>
                <span style={{
                  position: 'absolute',
                  top: '10px',
                  left: '10px',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: COLORS.quadrantLabel.improving,
                  background: 'rgba(88,166,255,0.2)',
                  padding: '4px 8px',
                  borderRadius: '4px'
                }}>
                  📈 Improving
                </span>
              </div>
              
              {/* Leading (Top-Right) - Green */}
              <div style={{ background: COLORS.quadrant.leading, position: 'relative' }}>
                <span style={{
                  position: 'absolute',
                  top: '10px',
                  right: '10px',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: COLORS.quadrantLabel.leading,
                  background: 'rgba(63,185,80,0.2)',
                  padding: '4px 8px',
                  borderRadius: '4px'
                }}>
                  🚀 Leading
                </span>
              </div>
              
              {/* Lagging (Bottom-Left) - Red */}
              <div style={{ background: COLORS.quadrant.lagging, position: 'relative' }}>
                <span style={{
                  position: 'absolute',
                  bottom: '10px',
                  left: '10px',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: COLORS.quadrantLabel.lagging,
                  background: 'rgba(248,81,73,0.2)',
                  padding: '4px 8px',
                  borderRadius: '4px'
                }}>
                  📉 Lagging
                </span>
              </div>
              
              {/* Weakening (Bottom-Right) - Yellow */}
              <div style={{ background: COLORS.quadrant.weakening, position: 'relative' }}>
                <span style={{
                  position: 'absolute',
                  bottom: '10px',
                  right: '10px',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: COLORS.quadrantLabel.weakening,
                  background: 'rgba(210,153,34,0.2)',
                  padding: '4px 8px',
                  borderRadius: '4px'
                }}>
                  ⚠️ Weakening
                </span>
              </div>
            </div>

            {/* Center Lines */}
            <div style={{
              position: 'absolute',
              left: '50%',
              top: '20px',
              bottom: '20px',
              width: '1px',
              background: COLORS.border,
              borderLeft: `1px dashed ${COLORS.border}`
            }} />
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '20px',
              right: '20px',
              height: '1px',
              background: COLORS.border,
              borderTop: `1px dashed ${COLORS.border}`
            }} />

            {/* Axis Labels */}
            <span style={{
              position: 'absolute',
              left: '50%',
              bottom: '4px',
              transform: 'translateX(-50%)',
              fontSize: '10px',
              color: COLORS.textMuted
            }}>
              ▼ Falling Momentum
            </span>
            <span style={{
              position: 'absolute',
              left: '50%',
              top: '4px',
              transform: 'translateX(-50%)',
              fontSize: '10px',
              color: COLORS.textMuted
            }}>
              ▲ Rising Momentum
            </span>
            <span style={{
              position: 'absolute',
              left: '4px',
              top: '50%',
              transform: 'translateY(-50%) rotate(-90deg)',
              fontSize: '10px',
              color: COLORS.textMuted,
              transformOrigin: 'left center'
            }}>
              ◀ Weak RS
            </span>
            <span style={{
              position: 'absolute',
              right: '4px',
              top: '50%',
              transform: 'translateY(-50%) rotate(90deg)',
              fontSize: '10px',
              color: COLORS.textMuted,
              transformOrigin: 'right center'
            }}>
              Strong RS ▶
            </span>

            {/* ETF Dots */}
            {allAssets.map((asset) => {
              const x = scaleX(asset.coordinate.rs_ratio);
              const y = scaleY(asset.coordinate.rs_momentum);
              const isSafeHaven = asset.category === 'safe_haven';
              const color = ETF_COLORS[asset.symbol] || '#6b7280';
              
              return (
                <div
                  key={asset.symbol}
                  style={{
                    position: 'absolute',
                    left: `calc(20px + (100% - 40px) * ${x / 100})`,
                    top: `calc(20px + (100% - 40px) * ${y / 100})`,
                    transform: 'translate(-50%, -50%)',
                    zIndex: 10
                  }}
                >
                  {/* Dot */}
                  <div
                    style={{
                      width: '14px',
                      height: '14px',
                      borderRadius: '50%',
                      backgroundColor: color,
                      border: isSafeHaven 
                        ? `2px solid ${COLORS.safeHavenBorder}` 
                        : '2px solid #ffffff',
                      boxShadow: isSafeHaven 
                        ? `0 0 8px ${COLORS.safeHavenGlow}` 
                        : '0 2px 8px rgba(0,0,0,0.5)',
                      cursor: 'pointer',
                      transition: 'transform 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.transform = 'scale(1.4)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.transform = 'scale(1)';
                    }}
                  />
                  {/* Label */}
                  <div style={{
                    position: 'absolute',
                    top: '18px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    fontSize: '10px',
                    fontWeight: 600,
                    color: COLORS.textPrimary,
                    background: 'rgba(22,27,34,0.95)',
                    padding: '2px 5px',
                    borderRadius: '3px',
                    whiteSpace: 'nowrap'
                  }}>
                    {asset.symbol}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column - Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Regime Indicator Card */}
          <div style={{
            background: COLORS.background,
            border: `1px solid ${COLORS.border}`,
            borderRadius: '8px',
            padding: '16px'
          }}>
            <div style={{ 
              fontSize: '11px', 
              color: COLORS.textSecondary,
              textTransform: 'uppercase',
              marginBottom: '12px'
            }}>
              Market Regime
            </div>
            
            {/* Regime Badge */}
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 16px',
              backgroundColor: `${regimeColor}20`,
              border: `1px solid ${regimeColor}40`,
              borderRadius: '6px',
              marginBottom: '16px'
            }}>
              <span style={{ fontSize: '18px' }}>{regime.emoji}</span>
              <span style={{ 
                fontWeight: 'bold', 
                color: regimeColor,
                fontSize: '14px'
              }}>
                {regime.regime?.replace('_', '-').toUpperCase()}
              </span>
            </div>

            {/* Score Gauge */}
            <div style={{ marginTop: '12px' }}>
              <div style={{
                display: 'flex',
                gap: '4px',
                marginBottom: '8px'
              }}>
                {[0, 1, 2, 3, 4, 5].map((i) => {
                  const isActive = (regime.score + 10) / 20 * 6 > i;
                  const segmentColors = ['#f85149', '#f85149', '#d29922', '#d29922', '#3fb950', '#3fb950'];
                  return (
                    <div
                      key={i}
                      style={{
                        flex: 1,
                        height: '8px',
                        backgroundColor: isActive ? segmentColors[i] : `${COLORS.border}`,
                        borderRadius: '2px',
                        boxShadow: isActive ? `0 0 6px ${segmentColors[i]}` : 'none'
                      }}
                    />
                  );
                })}
              </div>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '9px',
                color: COLORS.textMuted
              }}>
                <span>Risk-Off</span>
                <span>Neutral</span>
                <span>Risk-On</span>
              </div>
              <div style={{
                fontSize: '11px',
                color: COLORS.textSecondary,
                marginTop: '8px'
              }}>
                Score: {regime.score} / 10
              </div>
            </div>
          </div>

          {/* Risk Assets Card */}
          <div style={{
            background: COLORS.background,
            border: `1px solid ${COLORS.border}`,
            borderRadius: '8px',
            padding: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '12px',
              paddingBottom: '12px',
              borderBottom: `1px solid ${COLORS.border}`
            }}>
              <span>🔴</span>
              <span style={{ 
                fontSize: '13px', 
                fontWeight: 600, 
                color: COLORS.textPrimary 
              }}>
                Risk Assets
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {[...risk_assets].sort((a, b) => b.period_return - a.period_return).map((asset) => (
                <div key={asset.symbol} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px'
                }}>
                  <div style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    backgroundColor: ETF_COLORS[asset.symbol] || '#6b7280',
                    border: '2px solid #ffffff',
                    flexShrink: 0
                  }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontSize: '12px',
                      fontWeight: 500,
                      color: COLORS.textPrimary
                    }}>
                      {asset.symbol} <span style={{ color: COLORS.textMuted }}>({asset.name})</span>
                    </div>
                  </div>
                  <span style={{
                    fontSize: '10px',
                    color: COLORS.textSecondary
                  }}>
                    {QUADRANT_EMOJIS[asset.coordinate.quadrant]} {asset.coordinate.quadrant.charAt(0).toUpperCase() + asset.coordinate.quadrant.slice(1)}
                  </span>
                  <span style={{
                    fontSize: '12px',
                    fontWeight: 600,
                    color: asset.period_return >= 0 ? '#3fb950' : '#f85149'
                  }}>
                    {asset.period_return >= 0 ? '+' : ''}{asset.period_return.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Safe Haven Card */}
          <div style={{
            background: COLORS.background,
            border: `1px solid ${COLORS.border}`,
            borderRadius: '8px',
            padding: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '12px',
              paddingBottom: '12px',
              borderBottom: `1px solid ${COLORS.border}`
            }}>
              <span>🟡</span>
              <span style={{ 
                fontSize: '13px', 
                fontWeight: 600, 
                color: COLORS.textPrimary 
              }}>
                Safe Haven
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {[...safe_haven_assets].sort((a, b) => b.period_return - a.period_return).map((asset) => (
                <div key={asset.symbol} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px'
                }}>
                  <div style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    backgroundColor: ETF_COLORS[asset.symbol] || '#6b7280',
                    border: `2px solid ${COLORS.safeHavenBorder}`,
                    flexShrink: 0
                  }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontSize: '12px',
                      fontWeight: 500,
                      color: COLORS.textPrimary
                    }}>
                      {asset.symbol} <span style={{ color: COLORS.textMuted }}>({asset.name})</span>
                    </div>
                  </div>
                  <span style={{
                    fontSize: '10px',
                    color: COLORS.textSecondary
                  }}>
                    {QUADRANT_EMOJIS[asset.coordinate.quadrant]} {asset.coordinate.quadrant.charAt(0).toUpperCase() + asset.coordinate.quadrant.slice(1)}
                  </span>
                  <span style={{
                    fontSize: '12px',
                    fontWeight: 600,
                    color: asset.period_return >= 0 ? '#3fb950' : '#f85149'
                  }}>
                    {asset.period_return >= 0 ? '+' : ''}{asset.period_return.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recommendation Section */}
      <div style={{
        marginTop: '20px',
        background: 'linear-gradient(135deg, #161b22 0%, #1c2128 100%)',
        border: `1px solid ${COLORS.border}`,
        borderRadius: '12px',
        padding: '25px'
      }}>
        {/* Section Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Target size={20} color="#22d3ee" />
            <span style={{
              fontSize: '16px',
              fontWeight: 'bold',
              color: COLORS.textPrimary
            }}>
              🎯 Investment Recommendation
            </span>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            {regime.risk_summary && (
              <span style={{
                padding: '6px 12px',
                backgroundColor: 'rgba(63,185,80,0.15)',
                color: '#3fb950',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: 500
              }}>
                Risk: {regime.risk_summary}
              </span>
            )}
            {regime.safe_summary && (
              <span style={{
                padding: '6px 12px',
                backgroundColor: 'rgba(255,215,0,0.15)',
                color: '#ffd700',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: 500
              }}>
                Safe: {regime.safe_summary}
              </span>
            )}
          </div>
        </div>

        {/* Top Picks Box */}
        {top_picks.length > 0 && (
          <div style={{
            background: 'linear-gradient(135deg, rgba(63,185,80,0.12) 0%, rgba(63,185,80,0.04) 100%)',
            border: '1px solid rgba(63,185,80,0.25)',
            borderRadius: '10px',
            padding: '20px',
            marginBottom: '20px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              marginBottom: '16px'
            }}>
              <span style={{
                background: '#3fb950',
                color: '#0d1117',
                fontSize: '11px',
                fontWeight: 'bold',
                padding: '4px 10px',
                borderRadius: '4px',
                textTransform: 'uppercase'
              }}>
                🏆 Top Pick
              </span>
              <span style={{
                fontSize: '13px',
                color: COLORS.textSecondary
              }}>
                Recommended Sectors to Invest
              </span>
            </div>
            
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '16px'
            }}>
              {top_picks.map((pick) => (
                <div key={pick.symbol} style={{
                  background: COLORS.background,
                  border: `1px solid ${COLORS.border}`,
                  borderRadius: '8px',
                  padding: '16px'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '8px'
                  }}>
                    <div style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      background: '#3fb950',
                      color: '#0d1117',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '13px',
                      fontWeight: 'bold'
                    }}>
                      {pick.rank}
                    </div>
                    <div style={{
                      width: '12px',
                      height: '12px',
                      borderRadius: '50%',
                      backgroundColor: pick.color
                    }} />
                    <span style={{
                      fontSize: '15px',
                      fontWeight: 'bold',
                      color: COLORS.textPrimary
                    }}>
                      {pick.symbol}
                    </span>
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: COLORS.textSecondary,
                    marginBottom: '4px'
                  }}>
                    {pick.name}
                  </div>
                  <div style={{
                    fontSize: '11px',
                    color: COLORS.textMuted,
                    marginBottom: '8px'
                  }}>
                    {pick.reason}
                  </div>
                  <div style={{
                    fontSize: '15px',
                    fontWeight: 700,
                    color: '#3fb950'
                  }}>
                    +{pick.period_return.toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Grid - 4 Boxes */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '12px',
          marginBottom: '20px'
        }}>
          {/* BUY */}
          <div style={{
            border: '2px solid #3fb950',
            background: 'rgba(63, 185, 80, 0.08)',
            borderRadius: '10px',
            padding: '15px',
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '11px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              color: '#3fb950',
              marginBottom: '10px',
              fontWeight: 600
            }}>
              ✅ Buy / Add
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {buyGroup?.symbols?.map(sym => (
                <div key={sym} style={{
                  fontSize: '12px',
                  fontWeight: 500,
                  color: COLORS.textPrimary,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: ETF_COLORS[sym]
                  }} />
                  {sym}
                </div>
              )) || <span style={{ color: COLORS.textMuted, fontSize: '11px' }}>—</span>}
            </div>
          </div>

          {/* WATCH */}
          <div style={{
            border: '2px solid #58a6ff',
            background: 'rgba(88, 166, 255, 0.08)',
            borderRadius: '10px',
            padding: '15px',
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '11px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              color: '#58a6ff',
              marginBottom: '10px',
              fontWeight: 600
            }}>
              📌 Watch / Entry
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {watchGroup?.symbols?.map(sym => (
                <div key={sym} style={{
                  fontSize: '12px',
                  fontWeight: 500,
                  color: COLORS.textPrimary,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: ETF_COLORS[sym],
                    border: sym === 'GLD' || sym === 'TLT' || sym === 'SHY' || sym === 'UUP' ? `1px solid ${COLORS.safeHavenBorder}` : 'none'
                  }} />
                  {sym}
                </div>
              )) || <span style={{ color: COLORS.textMuted, fontSize: '11px' }}>—</span>}
            </div>
          </div>

          {/* REDUCE */}
          <div style={{
            border: '2px solid #d29922',
            background: 'rgba(210, 153, 34, 0.08)',
            borderRadius: '10px',
            padding: '15px',
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '11px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              color: '#d29922',
              marginBottom: '10px',
              fontWeight: 600
            }}>
              ⚠️ Take Profit
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {reduceGroup?.symbols?.map(sym => (
                <div key={sym} style={{
                  fontSize: '12px',
                  fontWeight: 500,
                  color: COLORS.textPrimary,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: ETF_COLORS[sym],
                    border: sym === 'GLD' || sym === 'TLT' || sym === 'SHY' || sym === 'UUP' ? `1px solid ${COLORS.safeHavenBorder}` : 'none'
                  }} />
                  {sym}
                </div>
              )) || <span style={{ color: COLORS.textMuted, fontSize: '11px' }}>—</span>}
            </div>
          </div>

          {/* AVOID */}
          <div style={{
            border: '2px solid #f85149',
            background: 'rgba(248, 81, 73, 0.08)',
            borderRadius: '10px',
            padding: '15px',
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '11px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              color: '#f85149',
              marginBottom: '10px',
              fontWeight: 600
            }}>
              🚫 Avoid
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {avoidGroup?.symbols?.map(sym => (
                <div key={sym} style={{
                  fontSize: '12px',
                  fontWeight: 500,
                  color: COLORS.textPrimary,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: ETF_COLORS[sym],
                    border: sym === 'GLD' || sym === 'TLT' || sym === 'SHY' || sym === 'UUP' ? `1px solid ${COLORS.safeHavenBorder}` : 'none'
                  }} />
                  {sym}
                </div>
              )) || <span style={{ color: COLORS.textMuted, fontSize: '11px' }}>—</span>}
            </div>
          </div>
        </div>

        {/* Key Insights */}
        {insights.length > 0 && (
          <div style={{
            background: '#21262d',
            borderRadius: '10px',
            padding: '20px',
            marginBottom: '16px'
          }}>
            <div style={{
              fontSize: '13px',
              color: COLORS.textSecondary,
              marginBottom: '12px'
            }}>
              📊 Key Insights
            </div>
            <ul style={{
              listStyle: 'none',
              padding: 0,
              margin: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              {insights.slice(0, 5).map((insight, idx) => (
                <li key={idx} style={{
                  fontSize: '13px',
                  color: '#c9d1d9',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '8px'
                }}>
                  <span style={{ flexShrink: 0 }}>{insight.emoji}</span>
                  <span>
                    {insight.highlight ? (
                      <>
                        {insight.text.split(insight.highlight)[0]}
                        <strong style={{ color: COLORS.textPrimary }}>{insight.highlight}</strong>
                        {insight.text.split(insight.highlight)[1]}
                      </>
                    ) : insight.text}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Disclaimer */}
        <div style={{
          fontSize: '11px',
          color: COLORS.textMuted,
          fontStyle: 'italic',
          textAlign: 'center'
        }}>
          ⚠️ Disclaimer: RRG Rotation Map is for informational purposes only. Not financial advice.
        </div>
      </div>
    </div>
  );
}

export default RRGRotationMap;
