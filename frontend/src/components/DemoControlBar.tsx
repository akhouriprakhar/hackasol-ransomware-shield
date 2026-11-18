import React, { useState } from 'react';
import { 
  RotateCcw, 
  Flame, 
  Footprints, 
  CheckCircle2, 
  Loader2, 
  AlertCircle,
  Play,
  Terminal,
  ShieldCheck,
  Zap,
  SlidersHorizontal
} from 'lucide-react';
import { motion } from 'framer-motion';
import { resetSimulator, startSimulator } from '../api';
import { BorderBeam } from './ui/BorderBeam';

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
      showFeedback(`Sandbox Restored: ${res.files_count ?? 50} files + ${res.canaries_count ?? 4} micro-canaries primed`, 'success');
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
    <div className="relative overflow-hidden bg-[#090d16] border border-[#141c30] rounded-xl p-4 shadow-xl tactical-panel">
      {/* MagicUI Border Beam along card edges */}
      <BorderBeam size={220} duration={8} colorFrom="#00f0ff" colorTo="#10b981" />

      {/* Control Strip Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 pb-3 border-b border-[#141c30]">
        <div className="flex items-center space-x-3">
          <div className="p-1.5 rounded bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-tactical-cyan">
            <SlidersHorizontal className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="font-mono text-sm font-bold tracking-wider text-slate-100 uppercase">
                JURY STAGE CONTROLS // ATTACK INJECTION &amp; BENCHMARK SUITE
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#0e1422] text-tactical-cyan border border-[#141c30] font-semibold">
                ISOLATED SANDBOX
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Inject real-time encrypted bursts or stealth attacks to trigger instantaneous POSIX SIGSTOP cryo-containment
            </p>
          </div>
        </div>

        {feedback && (
          <div className={`px-3 py-1.5 rounded-lg text-xs font-mono flex items-center space-x-2 border transition-all ${
            feedback.type === 'success' 
              ? 'bg-emerald-950/80 border-emerald-500/60 text-emerald-200' 
              : feedback.type === 'error'
              ? 'bg-rose-950/80 border-tactical-crimson/70 text-rose-200'
              : 'bg-[#00f0ff]/10 border-[#00f0ff]/40 text-cyan-200'
          }`}>
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-tactical-emerald shrink-0" />
            ) : feedback.type === 'error' ? (
              <AlertCircle className="w-4 h-4 text-tactical-crimson shrink-0" />
            ) : (
              <Loader2 className="w-4 h-4 text-tactical-cyan animate-spin shrink-0" />
            )}
            <span className="truncate max-w-xs md:max-w-md font-semibold">{feedback.message}</span>
          </div>
        )}
      </div>

      {/* Action Buttons Grid with Framer Motion spring feedback */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-3">
        
        {/* 1. Reset Sandbox */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleReset}
          disabled={loadingAction !== null}
          className="group relative flex items-center justify-between px-4 py-3 rounded-lg border border-[#1d2944] bg-[#0c121e] hover:bg-[#141c30] hover:border-[#2b3b60] text-slate-100 transition-all font-mono text-xs font-bold shadow-md disabled:opacity-50"
        >
          <div className="flex items-center space-x-2.5">
            {loadingAction === 'reset' ? (
              <Loader2 className="w-4 h-4 animate-spin text-tactical-cyan" />
            ) : (
              <RotateCcw className="w-4 h-4 text-slate-400 group-hover:text-tactical-cyan transition-colors" />
            )}
            <span>Reset Sandbox</span>
          </div>
          <span className="text-[10px] text-slate-300 border border-[#141c30] px-2 py-0.5 rounded bg-[#05070b]">
            54 Targets
          </span>
        </motion.button>

        {/* 2. Launch Attack (Burst) */}
        <motion.button
          whileHover={!isThreatContained ? { scale: 1.02 } : {}}
          whileTap={!isThreatContained ? { scale: 0.98 } : {}}
          onClick={() => handleStartSim('burst')}
          disabled={loadingAction !== null || isThreatContained}
          className={`group relative overflow-hidden flex items-center justify-between px-4 py-3 rounded-lg border font-mono text-xs font-bold transition-all shadow-md disabled:opacity-50 ${
            isThreatContained
              ? 'border-rose-950/40 bg-rose-950/10 text-rose-500/40 cursor-not-allowed'
              : 'border-tactical-crimson/80 bg-gradient-to-r from-[#2c0911] via-[#480d1a] to-[#2c0911] hover:from-[#400d18] hover:to-[#5c1322] text-rose-100 shadow-tactical-crimson animate-shimmer'
          }`}
        >
          <div className="flex items-center space-x-2.5 relative z-10">
            {loadingAction === 'burst' ? (
              <Loader2 className="w-4 h-4 animate-spin text-tactical-crimson" />
            ) : (
              <Flame className="w-4 h-4 text-tactical-crimson animate-pulse" />
            )}
            <span className="text-white font-extrabold">Attack (Burst)</span>
          </div>
          <span className="relative z-10 text-[10px] bg-black/60 text-tactical-crimson border border-tactical-crimson/60 px-2 py-0.5 rounded font-black">
            0ms Delay
          </span>
        </motion.button>

        {/* 3. Launch Attack (Stealth) */}
        <motion.button
          whileHover={!isThreatContained ? { scale: 1.02 } : {}}
          whileTap={!isThreatContained ? { scale: 0.98 } : {}}
          onClick={() => handleStartSim('stealth')}
          disabled={loadingAction !== null || isThreatContained}
          className={`group relative flex items-center justify-between px-4 py-3 rounded-lg border font-mono text-xs font-bold transition-all shadow-md disabled:opacity-50 ${
            isThreatContained
              ? 'border-amber-950/40 bg-amber-950/10 text-amber-500/40 cursor-not-allowed'
              : 'border-tactical-amber/70 bg-gradient-to-r from-[#2d1b02] via-[#462a04] to-[#2d1b02] hover:from-[#412703] hover:to-[#573505] text-amber-100 shadow-tactical-amber'
          }`}
        >
          <div className="flex items-center space-x-2.5">
            {loadingAction === 'stealth' ? (
              <Loader2 className="w-4 h-4 animate-spin text-tactical-amber" />
            ) : (
              <Footprints className="w-4 h-4 text-tactical-amber" />
            )}
            <span className="text-white font-extrabold">Attack (Stealth)</span>
          </div>
          <span className="text-[10px] bg-black/60 text-tactical-amber border border-tactical-amber/60 px-2 py-0.5 rounded font-black">
            200ms Evasion
          </span>
        </motion.button>

        {/* 4. Benign Activity */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => handleStartSim('benign')}
          disabled={loadingAction !== null}
          className="group relative flex items-center justify-between px-4 py-3 rounded-lg border border-emerald-500/50 bg-[#071810] hover:bg-[#0c2419] hover:border-emerald-400 text-emerald-100 transition-all font-mono text-xs font-bold shadow-md disabled:opacity-50"
        >
          <div className="flex items-center space-x-2.5">
            {loadingAction === 'benign' ? (
              <Loader2 className="w-4 h-4 animate-spin text-tactical-emerald" />
            ) : (
              <Play className="w-4 h-4 text-tactical-emerald" />
            )}
            <span className="text-white font-bold">Benign Dev Load</span>
          </div>
          <span className="text-[10px] bg-black/60 text-tactical-emerald border border-emerald-500/60 px-2 py-0.5 rounded font-black">
            Zero Threat
          </span>
        </motion.button>

      </div>
    </div>
  );
};
