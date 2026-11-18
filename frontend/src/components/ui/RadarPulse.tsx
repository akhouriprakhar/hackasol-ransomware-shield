import React from 'react';

interface RadarPulseProps {
  status?: 'safe' | 'alert' | 'warning';
  size?: number;
  className?: string;
}

export const RadarPulse: React.FC<RadarPulseProps> = ({
  status = 'safe',
  size = 28,
  className = '',
}) => {
  const colorMap = {
    safe: {
      ring: 'rgba(16, 185, 129, 0.35)',
      dot: '#10b981',
      shadow: '0 0 12px #10b981',
    },
    alert: {
      ring: 'rgba(255, 46, 84, 0.45)',
      dot: '#ff2e54',
      shadow: '0 0 15px #ff2e54',
    },
    warning: {
      ring: 'rgba(245, 158, 11, 0.45)',
      dot: '#f59e0b',
      shadow: '0 0 12px #f59e0b',
    },
  };

  const theme = colorMap[status];

  return (
    <div
      className={`relative inline-flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
    >
      {/* Outer pulsing ring 1 */}
      <span
        className="absolute inline-flex rounded-full animate-ping opacity-75"
        style={{
          width: '100%',
          height: '100%',
          backgroundColor: theme.ring,
          animationDuration: status === 'alert' ? '0.8s' : '2s',
        }}
      />
      {/* Outer pulsing ring 2 */}
      <span
        className="absolute inline-flex rounded-full opacity-30 animate-pulse"
        style={{
          width: '140%',
          height: '140%',
          border: `1px solid ${theme.dot}`,
        }}
      />
      {/* Center Beacon Dot */}
      <span
        className="relative inline-flex rounded-full"
        style={{
          width: size * 0.4,
          height: size * 0.4,
          backgroundColor: theme.dot,
          boxShadow: theme.shadow,
        }}
      />
    </div>
  );
};
