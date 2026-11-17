import React, { useState } from 'react';
import { 
  RotateCcw, 
  Flame, 
  Footprints, 
  CheckCircle2, 
  Loader2, 
  AlertCircle,
  Play
} from 'lucide-react';
import { resetSimulator, startSimulator } from '../api';

interface DemoControlBarProps {
  onSandboxReset: () => void;
  onAttackTriggered: (mode: string) => void;
  isThreatContained: boolean;
}

export const DemoControlBar: React.FC<DemoControlBarProps> = ({
  onSandboxReset,
  onAttackTriggered,
  isThreatContained,
}) => {
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ message: string; type: 'success' | 'info' | 'error' } | null>(null);

  const showFeedback = (message: string, type: 'success' | 'info' | 'error' = 'info') => {
    setFeedback({ message, type });
    setTimeout(() => {
      setFeedback((prev) => (prev?.message === message ? null : prev));
    }, 4500);
  };

  const handleReset = async () => {
    setLoadingAction('reset');
    try {
      const res = await resetSimulator();
      onSandboxReset();
      showFeedback(`Sandbox Restored: ${res.files_count ?? 50} benign files + ${res.canaries_count ?? 4} micro-canaries primed`, 'success');
    } catch (err: any) {
      showFeedback(`Reset failed: ${err.message}`, 'error');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleStartSim = async (mode: 'burst' | 'stealth' | 'benign') => {
    setLoadingAction(mode);
    try {
      const res = await startSimulator(mode);
      onAttackTriggered(mode);
      if (mode === 'burst') {
        showFeedback(`High-Velocity Burst Ransomware injected (PID: ${res.pid})`, 'info');
      } else if (mode === 'stealth') {
        showFeedback(`Low & Slow Stealth Ransomware injected (PID: ${res.pid})`, 'info');
      } else {
        showFeedback(`Benign developer activity simulated across sandbox files`, 'success');
      }
    } catch (err: any) {
      showFeedback(`Failed to launch ${mode}: ${err.message}`, 'error');
    } finally {
      setLoadingAction(null);
    }
  };

  return (
    <div className="bg-cyber-900 border border-cyber-800 rounded-xl p-4 shadow-xl">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 pb-3 border-b border-cyber-800/80">
        <div>
          <div className="flex items-center space-x-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <h2 className="font-mono text-sm font-bold tracking-wider text-slate-200 uppercase">
              Judge Stage Controls // Live 3-Minute Demo Suite
            </h2>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Trigger deterministic local attacks and verify instantaneous cryo-freeze containment
          </p>
        </div>

        {feedback && (
          <div className={`px-3 py-1.5 rounded-md text-xs font-mono flex items-center space-x-2 border transition-all ${
            feedback.type === 'success' 
              ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300' 
              : feedback.type === 'error'
              ? 'bg-rose-950/80 border-rose-500/40 text-rose-300'
              : 'bg-cyan-950/80 border-cyan-500/40 text-cyan-300'
          }`}>
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : feedback.type === 'error' ? (
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            ) : (
              <Loader2 className="w-4 h-4 text-cyan-400 animate-spin shrink-0" />
            )}
            <span className="truncate max-w-xs md:max-w-md">{feedback.message}</span>
          </div>
        )}
      </div>

      {/* Action Buttons Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-3">
        
        {/* 1. Reset Sandbox */}
        <button
          onClick={handleReset}
          disabled={loadingAction !== null}
          className="group relative flex items-center justify-center space-x-2.5 px-4 py-3 rounded-lg border border-slate-700 bg-cyber-850 hover:bg-slate-800 hover:border-slate-500 text-slate-200 transition-all font-mono text-xs font-semibold shadow-md active:scale-95 disabled:opacity-50"
        >
          {loadingAction === 'reset' ? (
            <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
          ) : (
            <RotateCcw className="w-4 h-4 text-slate-400 group-hover:text-cyan-400 transition-colors" />
          )}
          <span>Reset Sandbox</span>
          <span className="text-[10px] text-slate-500 border border-slate-700 px-1.5 py-0.5 rounded bg-cyber-950">
            54 Files
          </span>
        </button>

        {/* 2. Launch Attack (Burst) */}
        <button
          onClick={() => handleStartSim('burst')}
          disabled={loadingAction !== null || isThreatContained}
          className={`group relative flex items-center justify-center space-x-2.5 px-4 py-3 rounded-lg border font-mono text-xs font-bold transition-all shadow-md active:scale-95 disabled:opacity-50 ${
            isThreatContained
              ? 'border-red-900/50 bg-red-950/20 text-red-500/60 cursor-not-allowed'
              : 'border-red-500/60 bg-gradient-to-r from-red-950/70 via-rose-900/50 to-red-950/70 hover:from-red-900/80 hover:to-rose-800/80 text-red-200 glow-crimson'
          }`}
        >
          {loadingAction === 'burst' ? (
            <Loader2 className="w-4 h-4 animate-spin text-red-400" />
          ) : (
            <Flame className="w-4 h-4 text-red-400 animate-pulse" />
          )}
          <span>Attack (Burst)</span>
          <span className="text-[10px] bg-red-950/90 text-red-300 border border-red-700/60 px-1.5 py-0.5 rounded">
            0ms Delay
          </span>
        </button>

        {/* 3. Launch Attack (Stealth) */}
        <button
          onClick={() => handleStartSim('stealth')}
          disabled={loadingAction !== null || isThreatContained}
          className={`group relative flex items-center justify-center space-x-2.5 px-4 py-3 rounded-lg border font-mono text-xs font-bold transition-all shadow-md active:scale-95 disabled:opacity-50 ${
            isThreatContained
              ? 'border-amber-900/50 bg-amber-950/20 text-amber-500/60 cursor-not-allowed'
              : 'border-amber-500/60 bg-gradient-to-r from-amber-950/70 via-amber-900/40 to-amber-950/70 hover:from-amber-900/80 hover:to-amber-800/80 text-amber-200 glow-amber'
          }`}
        >
          {loadingAction === 'stealth' ? (
            <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
          ) : (
            <Footprints className="w-4 h-4 text-amber-400" />
          )}
          <span>Attack (Stealth)</span>
          <span className="text-[10px] bg-amber-950/90 text-amber-300 border border-amber-700/60 px-1.5 py-0.5 rounded">
            200ms
          </span>
        </button>

        {/* 4. Benign Activity */}
        <button
          onClick={() => handleStartSim('benign')}
          disabled={loadingAction !== null}
          className="group relative flex items-center justify-center space-x-2.5 px-4 py-3 rounded-lg border border-emerald-500/50 bg-emerald-950/40 hover:bg-emerald-900/50 hover:border-emerald-400 text-emerald-200 transition-all font-mono text-xs font-semibold shadow-md active:scale-95 disabled:opacity-50"
        >
          {loadingAction === 'benign' ? (
            <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
          ) : (
            <Play className="w-4 h-4 text-emerald-400" />
          )}
          <span>Benign Activity</span>
          <span className="text-[10px] bg-emerald-950/90 text-emerald-300 border border-emerald-700/60 px-1.5 py-0.5 rounded">
            Zero Threat
          </span>
        </button>

      </div>
    </div>
  );
};
