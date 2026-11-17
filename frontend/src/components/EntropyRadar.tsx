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
import { Activity, AlertTriangle, ShieldCheck } from 'lucide-react';
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
      <div className="bg-cyber-900 border border-cyber-700/80 p-3 rounded-lg shadow-2xl font-mono text-xs max-w-xs backdrop-blur-md">
        <div className="flex items-center justify-between border-b border-cyber-800 pb-1.5 mb-1.5">
          <span className="text-slate-400">T+{data.timeStr}</span>
          {data.isCanary && (
            <span className="bg-amber-950 text-amber-300 border border-amber-500/50 text-[10px] px-1.5 py-0.2 rounded font-bold">
              CANARY HIT
            </span>
          )}
        </div>
        <div className="text-slate-200 font-semibold truncate mb-1" title={data.fileName}>
          {data.fileName || 'file_event'}
        </div>
        <div className="space-y-1">
          <div className="flex justify-between items-center">
            <span className="text-cyan-400">Entropy H(X):</span>
            <span className={`font-bold ${data.entropy >= 7.5 ? 'text-red-400 font-extrabold' : 'text-cyan-300'}`}>
              {data.entropy.toFixed(2)} / 8.00
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-rose-400">Composite Risk:</span>
            <span className={`font-bold ${data.riskScore >= 80 ? 'text-red-400 font-extrabold' : 'text-slate-200'}`}>
              {data.riskScore.toFixed(1)} / 100
            </span>
          </div>
        </div>
        {data.isContained && (
          <div className="mt-2 pt-1 border-t border-red-500/30 text-[10px] text-red-400 font-bold tracking-wider">
            SIGSTOP FROZEN AT THIS POINT
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
    <div className="bg-cyber-900 border border-cyber-800 rounded-xl p-4 shadow-xl flex flex-col h-full">
      {/* Header Info Strip */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-3 border-b border-cyber-800/80 mb-3">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h3 className="font-mono text-sm font-bold tracking-wider text-slate-200 uppercase">
            Shannon Entropy & AI Risk Timeline
          </h3>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyber-800 text-slate-400 border border-cyber-700">
            Streaming
          </span>
        </div>

        {/* Live Gauges */}
        <div className="flex items-center space-x-3 font-mono text-xs">
          <div className={`px-2.5 py-1 rounded border flex items-center space-x-1.5 ${
            isHighEntropy 
              ? 'bg-red-950/80 border-red-500/60 text-red-300 animate-pulse' 
              : 'bg-cyber-850 border-cyber-700/80 text-cyan-300'
          }`}>
            <span className="text-[10px] text-slate-400">ENTROPY:</span>
            <span className="font-bold">{currentEntropy.toFixed(2)}</span>
            <span className="text-[10px] text-slate-500">H(X)</span>
          </div>

          <div className={`px-2.5 py-1 rounded border flex items-center space-x-1.5 ${
            isHighRisk 
              ? 'bg-rose-950/80 border-rose-500/60 text-rose-300 animate-pulse' 
              : 'bg-cyber-850 border-cyber-700/80 text-slate-300'
          }`}>
            <span className="text-[10px] text-slate-400">RISK:</span>
            <span className="font-bold">{currentRisk.toFixed(1)}</span>
            <span className="text-[10px] text-slate-500">/100</span>
          </div>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="w-full flex-1 min-h-[260px] relative">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 12, right: 10, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id="riskAreaGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />

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
              stroke="#06b6d4"
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
              stroke="#f43f5e"
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
              stroke="#ef4444"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: 'Entropy Threshold: 7.5',
                fill: '#ef4444',
                fontSize: 10,
                position: 'insideTopLeft',
                fontFamily: 'monospace',
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
              }}
            />

            {/* Risk Score Area */}
            <Area
              yAxisId="risk"
              type="monotone"
              dataKey="riskScore"
              stroke="#f43f5e"
              strokeWidth={2}
              fill="url(#riskAreaGradient)"
              isAnimationActive={false}
            />

            {/* Shannon Entropy Line */}
            <Line
              yAxisId="entropy"
              type="monotone"
              dataKey="entropy"
              stroke="#06b6d4"
              strokeWidth={2.5}
              dot={{ r: 2, fill: '#06b6d4' }}
              activeDot={{ r: 5, fill: '#22d3ee', stroke: '#0891b2', strokeWidth: 2 }}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Legend & Flatline Status Bar */}
      <div className="flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-cyber-800/80 mt-2">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-0.5 bg-cyan-400 inline-block" />
            <span className="text-slate-300">Shannon Entropy H(X)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-0.5 bg-rose-500 inline-block" />
            <span className="text-slate-300">Offline AI Risk Score</span>
          </div>
        </div>

        <div>
          {isContained ? (
            <span className="text-red-400 font-bold flex items-center space-x-1 animate-pulse">
              <AlertTriangle className="w-3.5 h-3.5 inline" />
              <span>POSIX SIGSTOP ACTIVE: Flatlined Execution</span>
            </span>
          ) : (
            <span className="text-emerald-400/90 flex items-center space-x-1">
              <ShieldCheck className="w-3.5 h-3.5 inline" />
              <span>Entropy Baseline Normal (&lt; 4.5)</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
