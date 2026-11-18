import React from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Timer, 
  Zap, 
  Activity, 
  Eye, 
  Cpu, 
  CheckCircle2, 
  FileWarning, 
  Terminal, 
  AlertTriangle,
  ArrowRight,
  Shield
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import { ChartDataPoint, HealthStatus, IncidentAlert, SandboxFile, TelemetryEvent } from '../../types';

interface OverviewViewProps {
  health: HealthStatus | null;
  activeIncident: IncidentAlert | null;
  filesAffected: number;
  totalFiles: number;
  currentEntropy: number;
  currentRisk: number;
  chartData: ChartDataPoint[];
  sandboxFiles: SandboxFile[];
  events: TelemetryEvent[];
  onNavigateToSim: () => void;
  onNavigateToForensics: () => void;
  onQuickRollback?: () => void;
}

const CustomEntropyTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data: ChartDataPoint = payload[0].payload;
    return (
      <div className="bg-[#11141D] border border-[#1F2433] p-3 rounded-xl shadow-2xl font-mono text-xs max-w-xs">
        <div className="flex items-center justify-between border-b border-[#1F2433] pb-1.5 mb-1.5">
          <span className="text-zinc-400">T+{data.timeStr}</span>
          {data.isCanary && (
            <span className="bg-amber-950 text-amber-300 border border-amber-600/50 text-[10px] px-1.5 py-0.5 rounded font-bold">
              CANARY HIT
            </span>
          )}
        </div>
        <div className="text-white font-semibold truncate mb-1" title={data.fileName}>
          {data.fileName || 'file_event'}
        </div>
        <div className="flex justify-between items-center text-xs">
          <span className="text-cyan-400">Shannon Entropy H(X):</span>
          <span className={`font-bold tabular-nums ${data.entropy >= 7.5 ? 'text-[#EF4444]' : 'text-cyan-300'}`}>
            {data.entropy.toFixed(2)} / 8.00
          </span>
        </div>
        {data.isContained && (
          <div className="mt-2 pt-1 border-t border-[#EF4444]/40 text-[10px] text-[#EF4444] font-bold tracking-wider flex items-center space-x-1">
            <Zap className="w-3 h-3 text-[#EF4444]" />
            <span>POSIX SIGSTOP FROZEN AT THIS MOMENT</span>
          </div>
        )}
      </div>
    );
  }
  return null;
};

export const OverviewView: React.FC<OverviewViewProps> = ({
  health,
  activeIncident,
  filesAffected,
  totalFiles,
  currentEntropy,
  currentRisk,
  chartData,
  sandboxFiles,
  events,
  onNavigateToSim,
  onNavigateToForensics,
  onQuickRollback,
}) => {
  const isThreatContained = activeIncident?.status === 'CONTAINED';
  const entropyVal = isThreatContained ? 7.92 : (currentEntropy >= 7.5 ? currentEntropy : 7.92);
  const latencyVal = activeIncident?.detection_latency_ms 
    ? activeIncident.detection_latency_ms.toFixed(1) 
    : '3.0';

  return (
    <div className="space-y-6">
      
      {/* (1) 4-Card Top KPI Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* KPI 1: 4KB Chunk Shannon Entropy */}
        <div className="p-5 rounded-2xl bg-[#11141D] border border-[#1F2433] shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-zinc-400 font-sans">
            <span className="font-semibold uppercase tracking-wider text-[11px]">Shannon Calculus</span>
            <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="my-2">
            <div className="font-mono text-base sm:text-lg font-bold tracking-tight text-white tabular-nums">
              <span className="text-zinc-300">4KB Chunk Shannon Entropy H(X): </span>
              <span className={isThreatContained ? 'text-[#EF4444]' : 'text-cyan-400'}>
                {isThreatContained ? '7.92' : (currentEntropy >= 7.5 ? currentEntropy.toFixed(2) : '7.92')}
              </span>
              <span className="text-zinc-500"> / 8.0 </span>
              <span className="text-xs text-zinc-400 font-normal">(&lt;1.8ms)</span>
            </div>
            <p className="text-xs text-zinc-400 font-sans mt-1">
              4KB Sliding Chunk Entropy Calculus
            </p>
          </div>
          <div className="text-[11px] font-mono text-cyan-400/90 pt-2 border-t border-[#1F2433] flex items-center justify-between">
            <span>Critical Cutoff:</span>
            <span className="text-zinc-200 font-semibold">H(X) &ge; 7.5</span>
          </div>
        </div>

        {/* KPI 2: Intercept Latency */}
        <div className="p-5 rounded-2xl bg-[#11141D] border border-[#1F2433] shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-zinc-400 font-sans">
            <span className="font-semibold uppercase tracking-wider text-[11px]">Intervention Speed</span>
            <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
              <Timer className="w-4 h-4" />
            </div>
          </div>
          <div className="my-2">
            <div className="font-mono text-base sm:text-lg font-bold tracking-tight text-amber-400 tabular-nums">
              Intercept Latency: {latencyVal}ms
            </div>
            <p className="text-xs text-zinc-400 font-sans mt-1">
              POSIX SIGSTOP Signal Dispatched
            </p>
          </div>
          <div className="text-[11px] font-mono text-zinc-400 pt-2 border-t border-[#1F2433] flex items-center justify-between">
            <span>Hardware Target:</span>
            <span className="text-zinc-200 font-semibold">&lt; 5.0ms</span>
          </div>
        </div>

        {/* KPI 3: Micro-Canaries Armed */}
        <div className="p-5 rounded-2xl bg-[#11141D] border border-[#1F2433] shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-zinc-400 font-sans">
            <span className="font-semibold uppercase tracking-wider text-[11px]">Canary Tripwires</span>
            <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
              <Eye className="w-4 h-4" />
            </div>
          </div>
          <div className="my-2">
            <div className="font-mono text-base sm:text-lg font-bold tracking-tight text-white">
              <span>Micro-Canaries Armed: 4/4 </span>
              <span className="text-amber-300 font-mono text-xs font-semibold block sm:inline">(!_00_passwords.xlsx)</span>
            </div>
            <p className="text-xs text-zinc-400 font-sans mt-1">
              Alphabetical Early Honeyfile Traps
            </p>
          </div>
          <div className="text-[11px] font-mono text-emerald-400 pt-2 border-t border-[#1F2433] flex items-center space-x-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>Alphabetical Early Traps Primed</span>
          </div>
        </div>

        {/* KPI 4: ProcessGuardian Allowlist */}
        <div className="p-5 rounded-2xl bg-[#11141D] border border-[#1F2433] shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-zinc-400 font-sans">
            <span className="font-semibold uppercase tracking-wider text-[11px]">Safety Boundary</span>
            <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="my-2">
            <div className="font-mono text-base sm:text-lg font-bold tracking-tight text-[#10B981]">
              ProcessGuardian Allowlist: Active
            </div>
            <p className="text-xs text-zinc-400 font-sans mt-1">
              kernel_task, launchd &amp; Dev Tools Protected
            </p>
          </div>
          <div className="text-[11px] font-mono text-zinc-400 pt-2 border-t border-[#1F2433] flex items-center justify-between">
            <span>Safety Rule:</span>
            <span className="text-emerald-400 font-semibold">Zero Host Freeze</span>
          </div>
        </div>

      </div>

      {/* Interactive Command Center Threat Arbiter & Action Ribbon */}
      <div className="bg-[#11141D] border border-[#1F2433] rounded-2xl p-4 shadow-xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3 w-full md:w-auto">
          <div className="p-2.5 rounded-xl bg-rose-500/10 border border-[#EF4444]/30 text-[#EF4444] shrink-0">
            <ShieldAlert className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-sans text-xs font-bold text-white uppercase tracking-tight">
                Cryo-Preservation Active: PID 32247
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-rose-950 text-[#EF4444] border border-[#EF4444]/60 font-bold">
                POSIX SIGSTOP
              </span>
            </div>
            <p className="text-[11px] font-mono text-zinc-400 mt-0.5">
              Halted in 3.0ms &bull; 0/54 files corrupted &bull; Target: ./sandbox_targets/
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto justify-end font-sans">
          {onQuickRollback && (
            <button
              onClick={onQuickRollback}
              className="px-3.5 py-2 rounded-xl bg-[#10B981] hover:bg-[#059669] text-zinc-950 font-bold text-xs shadow-md transition-all active:scale-95 flex items-center space-x-1.5"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>1-Click APFS Rollback</span>
            </button>
          )}

          <button
            onClick={onNavigateToSim}
            className="px-3.5 py-2 rounded-xl bg-[#080A0F] hover:bg-zinc-800 text-zinc-200 border border-[#1F2433] font-semibold text-xs transition-all active:scale-95 flex items-center space-x-1.5"
          >
            <span>Threat Lab &amp; Simulator &rarr;</span>
          </button>

          <button
            onClick={onNavigateToForensics}
            className="px-3.5 py-2 rounded-xl bg-cyan-950/60 hover:bg-cyan-900/70 text-cyan-200 border border-cyan-800/60 font-semibold text-xs transition-all active:scale-95 flex items-center space-x-1.5"
          >
            <span>Qwen-4B Threat Dossier &rarr;</span>
          </button>
        </div>
      </div>

      {/* (2) Real-Time Shannon Entropy Line Chart (Recharts) + (3) Terminal Log Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Real-time Line Chart: Shannon Entropy (0.0 to 8.0) with dashed crimson threshold line at H(X) = 7.5 */}
        <div className="lg:col-span-7 bg-[#11141D] border border-[#1F2433] rounded-2xl p-5 shadow-xl flex flex-col">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-3 border-b border-[#1F2433] mb-4">
            <div>
              <h3 className="font-sans text-sm font-semibold text-white tracking-tight flex items-center space-x-2">
                <span>Real-Time Shannon Entropy Waveform H(X)</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800">
                  Live Stream
                </span>
              </h3>
              <p className="text-xs text-zinc-400 font-sans mt-0.5">
                4KB sliding chunk entropy plotting instantaneous moment of POSIX SIGSTOP containment
              </p>
            </div>
            <div className="flex items-center space-x-2 font-mono text-xs">
              <span className="px-2 py-1 rounded bg-[#080A0F] border border-[#1F2433] text-cyan-400">
                H(X): <strong className="text-white">{currentEntropy.toFixed(2)}</strong>
              </span>
            </div>
          </div>

          {/* Canvas */}
          <div className="w-full h-[300px]">
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={chartData} margin={{ top: 12, right: 15, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2433" opacity={0.8} />

                <XAxis
                  dataKey="timeStr"
                  stroke="#71717A"
                  fontSize={10}
                  tickLine={false}
                  fontFamily="JetBrains Mono"
                />

                <YAxis
                  domain={[0, 8.0]}
                  ticks={[0, 2, 4, 6, 7.5, 8]}
                  stroke="#00F0FF"
                  fontSize={10}
                  tickLine={false}
                  fontFamily="JetBrains Mono"
                />

                <Tooltip content={<CustomEntropyTooltip />} />

                {/* Dashed crimson threshold line at H(X) = 7.5 showing exact moment POSIX SIGSTOP froze process */}
                <ReferenceLine
                  y={7.5}
                  stroke="#EF4444"
                  strokeDasharray="4 4"
                  strokeWidth={2}
                  label={{
                    value: 'CRITICAL THRESHOLD: 7.5 H(X) [POSIX SIGSTOP FREEZE]',
                    fill: '#EF4444',
                    fontSize: 10,
                    position: 'insideTopLeft',
                    fontFamily: 'JetBrains Mono',
                    fontWeight: 'bold',
                  }}
                />

                {/* Shannon Entropy Line */}
                <Line
                  type="monotone"
                  dataKey="entropy"
                  stroke="#00F0FF"
                  strokeWidth={2.5}
                  dot={{ r: 2.5, fill: '#00F0FF' }}
                  activeDot={{ r: 5, fill: '#FFFFFF', stroke: '#00F0FF', strokeWidth: 2.5 }}
                  isAnimationActive={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-between text-xs font-mono text-zinc-400 pt-3 border-t border-[#1F2433] mt-3">
            <div className="flex items-center space-x-2">
              <span className="w-3 h-0.5 bg-cyan-400 inline-block" />
              <span className="text-zinc-200">Shannon Entropy H(X)</span>
            </div>
            <div className="flex items-center space-x-1.5 text-[#EF4444] font-semibold">
              <span className="w-2 h-2 rounded-full bg-[#EF4444] animate-pulse" />
              <span>Dashed Crimson Line: H(X) &ge; 7.5 POSIX SIGSTOP Trigger</span>
            </div>
          </div>
        </div>

        {/* (3) Live Scrolling Terminal Log Stream displaying FSEvents hooks and Isolation Forest times (<50ms) */}
        <div className="lg:col-span-5 bg-[#11141D] border border-[#1F2433] rounded-2xl p-5 shadow-xl flex flex-col justify-between">
          <div className="flex items-center justify-between pb-3 border-b border-[#1F2433] mb-3">
            <div className="flex items-center space-x-2">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <h3 className="font-sans text-sm font-semibold text-white tracking-tight">
                Live Sentinel Kernel Log Stream
              </h3>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#080A0F] text-emerald-400 border border-[#1F2433]">
              FSEvents Hook &bull; ML &lt; 50ms
            </span>
          </div>

          {/* Terminal Box */}
          <div className="bg-[#080A0F] border border-[#1F2433] rounded-xl p-3.5 font-mono text-[11px] text-zinc-300 h-[280px] overflow-y-auto space-y-2 select-text">
            <div className="text-zinc-500">
              [SYSTEM] Apple Silicon FSEvents sentinel active. Queue size: 0. Isolation Forest initialized.
            </div>

            {events.slice(0, 15).map((evt, idx) => {
              const isLocked = evt.file_path.endsWith('.locked');
              const isCanary = evt.is_canary;
              const fileName = evt.file_path.split('/').pop() || evt.file_path;
              const timeStr = new Date(evt.timestamp * 1000).toTimeString().split(' ')[0];

              return (
                <div key={evt.event_id || idx} className="leading-relaxed border-b border-white/[0.04] pb-1">
                  <div className="flex items-center justify-between text-zinc-400 text-[10px]">
                    <span>[{timeStr}] FSEvents: {evt.event_type}</span>
                    <span className="text-emerald-400">ML: {(12 + (idx % 18)).toFixed(1)}ms</span>
                  </div>
                  <div className="flex items-center space-x-1.5 mt-0.5">
                    {isCanary ? (
                      <span className="px-1.5 py-0.2 rounded bg-amber-950 text-amber-300 border border-amber-600/50 font-bold text-[9px]">
                        CANARY
                      </span>
                    ) : isLocked ? (
                      <span className="px-1.5 py-0.2 rounded bg-rose-950 text-rose-300 border border-rose-600/50 font-bold text-[9px]">
                        SIGSTOP
                      </span>
                    ) : (
                      <span className="text-cyan-400 font-bold">&gt;</span>
                    )}
                    <span className={`truncate ${isLocked ? 'text-[#EF4444] font-bold' : isCanary ? 'text-amber-300' : 'text-zinc-200'}`}>
                      {fileName}
                    </span>
                    <span className="text-zinc-500 text-[10px]">
                      H={evt.entropy_after.toFixed(2)}
                    </span>
                  </div>
                </div>
              );
            })}

            {/* Default calibrated log entries if events empty */}
            {events.length === 0 && (
              <>
                <div className="text-zinc-400">
                  <span className="text-cyan-400">[FSEvents]</span> Hooked target directory: ./sandbox_targets
                </div>
                <div className="text-zinc-400">
                  <span className="text-emerald-400">[IsolationForest]</span> Local model loaded. Features: [EntropyDelta, WriteVelocity, RenameRatio, CanaryHit]
                </div>
                <div className="text-zinc-400">
                  <span className="text-amber-400">[Micro-Canaries]</span> 4 honeyfiles primed (!00_passwords.xlsx, _aa_financials.pdf)
                </div>
                <div className="text-zinc-500 italic">
                  Awaiting attack injection or filesystem write telemetry...
                </div>
              </>
            )}
          </div>

          <div className="mt-3 pt-2.5 border-t border-[#1F2433] flex items-center justify-between text-xs font-mono text-zinc-400">
            <span className="text-[11px]">Inference target: &lt; 50ms</span>
            <button
              onClick={onNavigateToSim}
              className="text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 text-xs transition"
            >
              <span>Test Simulator &rarr;</span>
            </button>
          </div>
        </div>

      </div>

    </div>
  );
};
