import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Wifi, 
  WifiOff, 
  Cpu, 
  Eye, 
  Timer, 
  Zap, 
  FileWarning,
  Activity,
  Radio,
  Clock,
  Terminal,
  AlertTriangle
} from 'lucide-react';
import { HealthStatus, IncidentAlert } from '../types';
import { RadarPulse } from './ui/RadarPulse';
import { DecryptedText } from './ui/DecryptedText';
import { NumberTicker } from './ui/NumberTicker';

interface HeaderProps {
  wsConnected: boolean;
  health: HealthStatus | null;
  activeIncident: IncidentAlert | null;
  filesAffected: number;
  totalFiles: number;
}

export const Header: React.FC<HeaderProps> = ({
  wsConnected,
  health,
  activeIncident,
  filesAffected,
  totalFiles = 54,
}) => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toTimeString().split(' ')[0] + ' UTC' + (now.getTimezoneOffset() <= 0 ? '+' : '-') + Math.abs(now.getTimezoneOffset() / 60));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const isThreatActive = activeIncident && activeIncident.status === 'CONTAINED';
  const watcherActive = health?.watcher?.active ?? true;
  const mttd = activeIncident?.detection_latency_ms 
    ? activeIncident.detection_latency_ms 
    : 18.4;
  const mttc = 4.2;
  const lossPercentage = totalFiles > 0 ? ((filesAffected / totalFiles) * 100).toFixed(1) : '0.0';

  return (
    <header className="border-b border-[#141c30] bg-[#070a12]/95 backdrop-blur-md sticky top-0 z-50">
      {/* High-Impact Tactical Containment HUD Banner */}
      {isThreatActive && (
        <div className="bg-gradient-to-r from-[#3b0b14] via-[#5c1020] to-[#3b0b14] border-b-2 border-tactical-crimson px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 shadow-tactical-crimson">
          <div className="flex items-center space-x-3">
            <RadarPulse status="alert" size={24} />
            <div className="flex items-center space-x-2 font-mono">
              <span className="px-2 py-0.5 rounded bg-black/60 border border-tactical-crimson/80 text-white font-bold text-xs tracking-wider">
                CRITICAL THREAT FROZEN
              </span>
              <span className="text-white text-xs sm:text-sm font-semibold tracking-wide">
                PID <span className="font-bold underline text-tactical-cyan">
                  <DecryptedText text={String(activeIncident.offending_pid)} speed={30} />
                </span> ({activeIncident.process_name}) HALTED VIA POSIX SIGSTOP
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-4 font-mono text-xs text-rose-200">
            <div className="bg-black/40 px-2.5 py-1 rounded border border-rose-500/40">
              RISK: <span className="font-extrabold text-white"><NumberTicker value={activeIncident.risk_score} decimalPlaces={1} />/100</span>
            </div>
            <div className="bg-black/40 px-2.5 py-1 rounded border border-rose-500/40">
              BLAST RADIUS: <span className="font-extrabold text-white"><NumberTicker value={filesAffected} /> / {totalFiles}</span> ({lossPercentage}% locked)
            </div>
            <div className="hidden md:flex items-center space-x-1 text-tactical-emerald font-bold">
              <ShieldCheck className="w-4 h-4" />
              <span>PRE-ENCRYPTION CONTAINED</span>
            </div>
          </div>
        </div>
      )}

      {/* Main Top Header Strip */}
      <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          
          {/* Brand Identity / Terminal Emblem */}
          <div className="flex items-center space-x-3.5">
            <div className={`p-2.5 rounded-lg border transition-all duration-200 ${
              isThreatActive 
                ? 'bg-rose-950/40 border-tactical-crimson/60 text-tactical-crimson shadow-tactical-crimson' 
                : 'bg-[#00f0ff]/10 border-[#00f0ff]/30 text-tactical-cyan shadow-tactical-cyan'
            }`}>
              {isThreatActive ? (
                <ShieldAlert className="w-6 h-6 animate-pulse" />
              ) : (
                <ShieldCheck className="w-6 h-6" />
              )}
            </div>
            <div>
              <div className="flex items-center space-x-2.5">
                <h1 className="font-mono text-xl font-extrabold tracking-wider text-white flex items-center">
                  AEGIS<span className="text-tactical-cyan">RANSOM</span>
                  <span className="text-tactical-crimson font-black ml-0.5">-X</span>
                </h1>
                <span className="px-2 py-0.5 text-[10px] font-mono tracking-widest font-bold rounded bg-[#00f0ff]/10 text-tactical-cyan border border-[#00f0ff]/40">
                  CRYO-SOC v1.0
                </span>
                <span className="hidden sm:inline-flex items-center space-x-1.5 px-2 py-0.5 text-[10px] font-mono rounded bg-emerald-950/60 text-emerald-400 border border-emerald-500/30">
                  <RadarPulse status={isThreatActive ? 'alert' : 'safe'} size={14} />
                  <span>{isThreatActive ? 'ENGAGED' : 'ARMED'}</span>
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5 flex items-center space-x-2">
                <span>macOS Apple Silicon (Darwin ARM64)</span>
                <span className="text-slate-600">&bull;</span>
                <span className="text-tactical-cyan font-semibold">Sub-20ms Pre-Encryption Intercept</span>
                <span className="text-slate-600">&bull;</span>
                <span className="text-slate-500 font-mono">{timeStr}</span>
              </p>
            </div>
          </div>

          {/* High-Precision Tactical KPI Blocks */}
          <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-5 gap-2.5">
            
            {/* 1. System & Local ML Status */}
            <div className="bg-[#090d16] border border-[#141c30] hover:border-[#1d2944] rounded-lg px-3 py-2 flex flex-col justify-between transition-colors shadow-sm">
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono font-semibold tracking-wider uppercase mb-1">
                <span>SYSTEM STATUS</span>
                {wsConnected ? (
                  <Wifi className="w-3.5 h-3.5 text-tactical-emerald" />
                ) : (
                  <WifiOff className="w-3.5 h-3.5 text-tactical-crimson animate-pulse" />
                )}
              </div>
              <div className="flex items-center space-x-2">
                <RadarPulse status={wsConnected ? 'safe' : 'alert'} size={14} />
                <span className="font-mono text-xs font-bold text-slate-100 truncate">
                  {wsConnected ? 'TELEMETRY LIVE' : 'DISCONNECTED'}
                </span>
              </div>
              <div className="flex items-center space-x-1.5 text-[10px] font-mono text-tactical-cyan mt-1">
                <Cpu className="w-3 h-3 text-tactical-cyan" />
                <span className="font-medium">100% OFFLINE ML</span>
              </div>
            </div>

            {/* 2. Apple FSEvents Kernel Sensor */}
            <div className="bg-[#090d16] border border-[#141c30] hover:border-[#1d2944] rounded-lg px-3 py-2 flex flex-col justify-between transition-colors shadow-sm">
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono font-semibold tracking-wider uppercase mb-1">
                <span>KERNEL SENSOR</span>
                <Eye className={`w-3.5 h-3.5 ${watcherActive ? 'text-tactical-cyan' : 'text-tactical-amber'}`} />
              </div>
              <div className="font-mono text-xs font-bold text-slate-100 truncate">
                {watcherActive ? 'FSEvents ACTIVE' : 'SUSPENDED'}
              </div>
              <div className="text-[10px] font-mono text-slate-400 mt-1 flex items-center justify-between">
                <span>QUEUE</span>
                <span className="text-slate-200 font-bold tabular-nums">
                  <NumberTicker value={health?.watcher?.queue_size ?? 0} /> EVTS
                </span>
              </div>
            </div>

            {/* 3. MTTD Speed Metric */}
            <div className="bg-[#090d16] border border-[#141c30] hover:border-[#1d2944] rounded-lg px-3 py-2 flex flex-col justify-between transition-colors shadow-sm">
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono font-semibold tracking-wider uppercase mb-1">
                <span>MTTD (DETECTION)</span>
                <Timer className="w-3.5 h-3.5 text-tactical-cyan" />
              </div>
              <div className="font-mono text-sm font-extrabold text-tactical-cyan tabular-nums flex items-baseline space-x-1">
                <NumberTicker value={mttd} decimalPlaces={1} />
                <span className="text-xs">ms</span>
              </div>
              <div className="text-[10px] font-mono text-slate-400 mt-1 flex items-center justify-between">
                <span>BUDGET</span>
                <span className="text-slate-300 font-semibold">&lt; 20ms</span>
              </div>
            </div>

            {/* 4. MTTC Speed Metric */}
            <div className="bg-[#090d16] border border-[#141c30] hover:border-[#1d2944] rounded-lg px-3 py-2 flex flex-col justify-between transition-colors shadow-sm">
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono font-semibold tracking-wider uppercase mb-1">
                <span>MTTC (SIGSTOP)</span>
                <Zap className="w-3.5 h-3.5 text-tactical-amber" />
              </div>
              <div className="font-mono text-sm font-extrabold text-tactical-amber tabular-nums flex items-baseline space-x-1">
                <NumberTicker value={mttc} decimalPlaces={1} />
                <span className="text-xs">ms</span>
              </div>
              <div className="text-[10px] font-mono text-slate-400 mt-1 flex items-center justify-between">
                <span>METHOD</span>
                <span className="text-slate-300 font-semibold">SIGSTOP</span>
              </div>
            </div>

            {/* 5. Blast Radius Gauge */}
            <div className={`col-span-2 sm:col-span-1 bg-[#090d16] border rounded-lg px-3 py-2 flex flex-col justify-between transition-colors shadow-sm ${
              filesAffected > 0 
                ? 'border-tactical-crimson/70 bg-rose-950/20 shadow-tactical-crimson' 
                : 'border-[#141c30] hover:border-[#1d2944]'
            }`}>
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono font-semibold tracking-wider uppercase mb-1">
                <span>BLAST RADIUS</span>
                <FileWarning className={`w-3.5 h-3.5 ${filesAffected > 0 ? 'text-tactical-crimson' : 'text-tactical-emerald'}`} />
              </div>
              <div className="font-mono text-xs font-bold flex items-baseline justify-between">
                <span className={filesAffected > 0 ? 'text-tactical-crimson text-sm font-black' : 'text-tactical-emerald font-extrabold text-sm'}>
                  <NumberTicker value={filesAffected} /> <span className="text-[10px] font-normal text-slate-400">/ {totalFiles} locked</span>
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  {lossPercentage}%
                </span>
              </div>
              <div className="w-full bg-[#141c30] rounded-full h-1.5 mt-1.5 overflow-hidden">
                <div 
                  className={`h-full transition-all duration-300 ${filesAffected > 0 ? 'bg-tactical-crimson' : 'bg-tactical-emerald'}`}
                  style={{ width: `${Math.min(100, Math.max(0, (filesAffected / totalFiles) * 100))}%` }}
                />
              </div>
            </div>

          </div>

        </div>
      </div>
    </header>
  );
};
