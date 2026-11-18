import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import { Activity, AlertTriangle, ShieldCheck, Zap } from 'lucide-react';
import { ChartDataPoint } from '../types';

interface EntropyRadarProps {
  data: ChartDataPoint[];
  currentEntropy: number;
  currentRisk: number;
  isContained: boolean;
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data: ChartDataPoint = payload[0].payload;
    return (
      <div className="bg-[#080c16]/95 border border-[#1e293b] p-3 rounded-lg shadow-2xl font-mono text-xs max-w-xs backdrop-blur-md">
        <div className="flex items-center justify-between border-b border-[#1e293b] pb-1.5 mb-1.5">
          <span className="text-slate-400 font-semibold">T+{data.timeStr}</span>
          {data.isCanary && (
            <span className="bg-tactical-amber/20 text-tactical-amber border border-tactical-amber/50 text-[10px] px-1.5 py-0.5 rounded font-black">
              CANARY TRIPWIRE
            </span>
          )}
        </div>
        <div className="text-slate-100 font-bold truncate mb-2 text-[11px]" title={data.fileName}>
          {data.fileName || 'file_event'}
        </div>
        <div className="space-y-1.5">
          <div className="flex justify-between items-center">
            <span className="text-tactical-cyan font-medium">Shannon Entropy H(X):</span>
            <span className={`font-black tabular-nums ${data.entropy >= 7.5 ? 'text-tactical-crimson' : 'text-tactical-cyan'}`}>
              {data.entropy.toFixed(2)} / 8.00
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-rose-400 font-medium">Composite Risk:</span>
            <span className={`font-black tabular-nums ${data.riskScore >= 80 ? 'text-tactical-crimson' : 'text-slate-200'}`}>
              {data.riskScore.toFixed(1)} / 100
            </span>
          </div>
        </div>
        {data.isContained && (
          <div className="mt-2 pt-1.5 border-t border-tactical-crimson/40 text-[10px] text-tactical-crimson font-black tracking-wider flex items-center space-x-1">
            <Zap className="w-3 h-3 text-tactical-crimson" />
            <span>POSIX SIGSTOP FREEZE POINT</span>
          </div>
        )}
      </div>
    );
  }
  return null;
};

export const EntropyRadar: React.FC<EntropyRadarProps> = ({
  data,
  currentEntropy,
  currentRisk,
  isContained,
}) => {
  const isHighEntropy = currentEntropy >= 7.5;
  const isHighRisk = currentRisk >= 80;

  return (
    <div className="bg-[#090d16] border border-[#141c30] rounded-xl p-4 shadow-xl flex flex-col h-full tactical-panel">
      {/* Header Info Strip */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-3 border-b border-[#141c30] mb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded bg-[#00f0ff]/10 text-tactical-cyan border border-[#00f0ff]/30">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-mono text-sm font-bold tracking-wider text-slate-100 uppercase">
                SHANNON ENTROPY &amp; LOCAL AI RISK TELEMETRY
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#0e1422] text-tactical-cyan border border-[#141c30] font-semibold">
                STREAMING
              </span>
            </div>
            <p className="text-[11px] font-mono text-slate-400">
              Real-time 4KB block entropy calculus H(X) &le; 8.0 &bull; Sub-50ms offline feature evaluation
            </p>
          </div>
        </div>

        {/* Live Gauges */}
        <div className="flex items-center space-x-2.5 font-mono text-xs">
          <div className={`px-2.5 py-1 rounded border flex items-center space-x-1.5 ${
            isHighEntropy 
              ? 'bg-rose-950/80 border-tactical-crimson text-tactical-crimson shadow-tactical-crimson animate-pulse' 
              : 'bg-[#0c121e] border-[#1d2944] text-tactical-cyan'
          }`}>
            <span className="text-[10px] text-slate-400">ENTROPY:</span>
            <span className="font-black tabular-nums">{currentEntropy.toFixed(2)}</span>
            <span className="text-[10px] text-slate-500 font-bold">H(X)</span>
          </div>

          <div className={`px-2.5 py-1 rounded border flex items-center space-x-1.5 ${
            isHighRisk 
              ? 'bg-rose-950/80 border-tactical-crimson text-tactical-crimson shadow-tactical-crimson animate-pulse' 
              : 'bg-[#0c121e] border-[#1d2944] text-slate-200'
          }`}>
            <span className="text-[10px] text-slate-400">RISK:</span>
            <span className="font-black tabular-nums">{currentRisk.toFixed(1)}</span>
            <span className="text-[10px] text-slate-500 font-bold">/100</span>
          </div>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="w-full flex-1 min-h-[270px] relative">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 14, right: 12, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id="riskAreaGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff2e54" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#ff2e54" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#162238" opacity={0.7} />

            <XAxis
              dataKey="timeStr"
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              fontFamily="monospace"
            />

            {/* Left Y-Axis: Shannon Entropy [0.0 - 8.0] */}
            <YAxis
              yAxisId="entropy"
              domain={[0, 8.0]}
              ticks={[0, 2, 4, 6, 7.5, 8]}
              stroke="#00f0ff"
              fontSize={10}
              tickLine={false}
              fontFamily="monospace"
              orientation="left"
            />

            {/* Right Y-Axis: Risk Score [0 - 100] */}
            <YAxis
              yAxisId="risk"
              domain={[0, 100]}
              ticks={[0, 25, 50, 75, 80, 100]}
              stroke="#ff2e54"
              fontSize={10}
              tickLine={false}
              fontFamily="monospace"
              orientation="right"
            />

            <Tooltip content={<CustomTooltip />} />

            {/* Red Threshold Line for Shannon Entropy (7.5) */}
            <ReferenceLine
              yAxisId="entropy"
              y={7.5}
              stroke="#ff2e54"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: 'Ransomware Limit: 7.5 H(X)',
                fill: '#ff2e54',
                fontSize: 10,
                position: 'insideTopLeft',
                fontFamily: 'monospace',
                fontWeight: 'bold',
              }}
            />

            {/* Amber Threshold Line for Containment Trigger (80.0) */}
            <ReferenceLine
              yAxisId="risk"
              y={80}
              stroke="#f59e0b"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: 'Cryo-Trigger: 80.0',
                fill: '#f59e0b',
                fontSize: 10,
                position: 'insideTopRight',
                fontFamily: 'monospace',
                fontWeight: 'bold',
              }}
            />

            {/* Risk Score Area */}
            <Area
              yAxisId="risk"
              type="monotone"
              dataKey="riskScore"
              stroke="#ff2e54"
              strokeWidth={2}
              fill="url(#riskAreaGradient)"
              isAnimationActive={false}
            />

            {/* Shannon Entropy Line */}
            <Line
              yAxisId="entropy"
              type="monotone"
              dataKey="entropy"
              stroke="#00f0ff"
              strokeWidth={2.5}
              dot={{ r: 2.5, fill: '#00f0ff' }}
              activeDot={{ r: 5, fill: '#ffffff', stroke: '#00f0ff', strokeWidth: 2.5 }}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Legend & Flatline Status Bar */}
      <div className="flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-400 pt-2.5 border-t border-[#141c30] mt-2">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-1 bg-tactical-cyan inline-block rounded-sm" />
            <span className="text-slate-200 font-medium">Shannon Entropy H(X)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-1 bg-tactical-crimson inline-block rounded-sm" />
            <span className="text-slate-200 font-medium">ML Risk Score</span>
          </div>
        </div>

        <div>
          {isContained ? (
            <span className="text-tactical-crimson font-bold flex items-center space-x-1.5 animate-pulse">
              <AlertTriangle className="w-3.5 h-3.5 inline" />
              <span>POSIX SIGSTOP ACTIVE &bull; Zero CPU Execution</span>
            </span>
          ) : (
            <span className="text-tactical-emerald flex items-center space-x-1.5 font-semibold">
              <ShieldCheck className="w-3.5 h-3.5 inline" />
              <span>Baseline Calibrated &bull; Zero Anomaly</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
