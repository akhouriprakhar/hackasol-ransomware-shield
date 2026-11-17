import React from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Wifi, 
  WifiOff, 
  Cpu, 
  Eye, 
  Timer, 
  Zap, 
  FileWarning 
} from 'lucide-react';
import { HealthStatus, IncidentAlert } from '../types';

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
  const isThreatActive = activeIncident && activeIncident.status === 'CONTAINED';
  const watcherActive = health?.watcher?.active ?? true;
  const mttd = activeIncident?.detection_latency_ms 
    ? `${activeIncident.detection_latency_ms.toFixed(1)}ms` 
    : '< 20ms';
  const mttc = '< 5ms';

  return (
    <header className="border-b border-cyber-800 bg-cyber-900/90 backdrop-blur-md sticky top-0 z-50">
      {/* Top Banner Alert Bar if Frozen/Contained */}
      {isThreatActive && (
        <div className="bg-gradient-to-r from-red-950 via-rose-900 to-red-950 border-b border-red-500/50 px-4 py-2 flex items-center justify-between animate-pulse">
          <div className="flex items-center space-x-3">
            <span className="flex h-3 w-3 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
            </span>
            <span className="font-mono text-xs md:text-sm font-bold tracking-wider text-red-200 uppercase">
              CRITICAL THREAT FROZEN: PID {activeIncident.offending_pid} ({activeIncident.process_name}) HALTED VIA POSIX SIGSTOP
            </span>
          </div>
          <div className="font-mono text-xs text-red-300 hidden md:block">
            Risk: <span className="font-bold text-white">{activeIncident.risk_score.toFixed(1)}/100</span> | Blast Radius: <span className="font-bold text-white">{filesAffected} files</span>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          
          {/* Logo & Platform Info */}
          <div className="flex items-center space-x-3">
            <div className={`p-2.5 rounded-lg border ${isThreatActive ? 'bg-red-500/10 border-red-500/40 text-red-400 glow-crimson' : 'bg-cyan-500/10 border-cyan-500/40 text-cyan-400 glow-cyan'}`}>
              {isThreatActive ? <ShieldAlert className="w-6 h-6 animate-pulse" /> : <ShieldCheck className="w-6 h-6" />}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="font-mono text-lg font-bold tracking-wider text-white">
                  AEGIS<span className="text-cyan-400">RANSOM</span>-X
                </h1>
                <span className="px-2 py-0.5 text-[10px] font-mono tracking-widest font-semibold rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800">
                  v1.0-SOC
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                macOS Pre-Encryption Cryo-Containment & Offline Local ML
              </p>
            </div>
          </div>

          {/* KPI Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-5 gap-2 sm:gap-3">
            
            {/* 1. Connection & Local ML Status */}
            <div className="bg-cyber-850/80 border border-cyber-700/60 rounded-md px-3 py-2 flex flex-col justify-center">
              <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-1">
                <span>SYSTEM STATUS</span>
                {wsConnected ? (
                  <Wifi className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <WifiOff className="w-3.5 h-3.5 text-rose-500 animate-pulse" />
                )}
              </div>
              <div className="flex items-center space-x-1.5">
                <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
                <span className="font-mono text-xs font-semibold text-slate-200 truncate">
                  {wsConnected ? 'WS CONNECTED' : 'OFFLINE RECONNECT'}
                </span>
              </div>
              <div className="flex items-center space-x-1 text-[10px] font-mono text-emerald-400/90 mt-0.5">
                <Cpu className="w-3 h-3 text-cyan-400" />
                <span>100% LOCAL ML</span>
              </div>
            </div>

            {/* 2. Active Watcher Indicator */}
            <div className="bg-cyber-850/80 border border-cyber-700/60 rounded-md px-3 py-2 flex flex-col justify-center">
              <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-1">
                <span>FS SENSOR</span>
                <Eye className={`w-3.5 h-3.5 ${watcherActive ? 'text-cyan-400' : 'text-amber-400'}`} />
              </div>
              <div className="font-mono text-xs font-semibold text-slate-200 truncate">
                {watcherActive ? 'FSEvents ACTIVE' : 'STANDBY'}
              </div>
              <div className="text-[10px] font-mono text-slate-400 mt-0.5">
                Queue: {health?.watcher?.queue_size ?? 0} events
              </div>
            </div>

            {/* 3. MTTD Indicator */}
            <div className="bg-cyber-850/80 border border-cyber-700/60 rounded-md px-3 py-2 flex flex-col justify-center">
              <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-1">
                <span>MTTD (DETECTION)</span>
                <Timer className="w-3.5 h-3.5 text-cyan-400" />
              </div>
              <div className="font-mono text-xs font-bold text-cyan-300">
                {mttd}
              </div>
              <div className="text-[10px] font-mono text-slate-400 mt-0.5">
                Threshold: &lt; 20ms
              </div>
            </div>

            {/* 4. MTTC Indicator */}
            <div className="bg-cyber-850/80 border border-cyber-700/60 rounded-md px-3 py-2 flex flex-col justify-center">
              <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-1">
                <span>MTTC (CRYO-FREEZE)</span>
                <Zap className="w-3.5 h-3.5 text-amber-400" />
              </div>
              <div className="font-mono text-xs font-bold text-amber-300">
                {mttc}
              </div>
              <div className="text-[10px] font-mono text-slate-400 mt-0.5">
                POSIX SIGSTOP
              </div>
            </div>

            {/* 5. Blast Radius Counter */}
            <div className={`col-span-2 sm:col-span-1 bg-cyber-850/80 border rounded-md px-3 py-2 flex flex-col justify-center ${
              filesAffected > 0 ? 'border-red-500/50 bg-red-950/20 glow-crimson' : 'border-cyber-700/60'
            }`}>
              <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-1">
                <span>BLAST RADIUS</span>
                <FileWarning className={`w-3.5 h-3.5 ${filesAffected > 0 ? 'text-red-400' : 'text-slate-400'}`} />
              </div>
              <div className="font-mono text-xs font-bold">
                <span className={filesAffected > 0 ? 'text-red-400 text-sm' : 'text-emerald-400'}>
                  {filesAffected}
                </span>
                <span className="text-slate-400 text-xs"> / {totalFiles} files affected</span>
              </div>
              <div className="text-[10px] font-mono text-slate-400 mt-0.5 truncate">
                {filesAffected === 0 ? 'Zero Data Loss' : 'Containment Sealed'}
              </div>
            </div>

          </div>

        </div>
      </div>
    </header>
  );
};
