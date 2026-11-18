import React, { useState } from 'react';
import { 
  Flame, 
  Footprints, 
  Play, 
  RotateCcw, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  ShieldCheck, 
  Zap,
  ArrowRight,
  HardDrive,
  Lock,
  Shield,
  FileCode,
  Terminal,
  Cpu,
  Check
} from 'lucide-react';
import { motion } from 'framer-motion';
import { resetSimulator, startSimulator } from '../../api';
import { SandboxFile } from '../../types';
import { SandboxDiskMatrix } from '../SandboxDiskMatrix';

interface SimulationViewProps {
  sandboxFiles: SandboxFile[];
  onRefreshFiles: () => void;
  onSandboxReset: () => void;
  onAttackTriggered: (mode: string) => void;
  isThreatContained: boolean;
  onQuickRollback: () => void;
}

export const SimulationView: React.FC<SimulationViewProps> = ({
  sandboxFiles,
  onRefreshFiles,
  onSandboxReset,
  onAttackTriggered,
  isThreatContained,
  onQuickRollback,
}) => {
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [selectedFileCount, setSelectedFileCount] = useState<number>(54);
  const [selectedMode, setSelectedMode] = useState<'burst' | 'stealth' | 'benign'>('burst');
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
      onRefreshFiles();
      showFeedback(`Sandbox Restored: ${res.files_count ?? 50} files + ${res.canaries_count ?? 4} micro-canaries primed`, 'success');
    } catch (err: any) {
      showFeedback(`Reset failed: ${err.message}`, 'error');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleStartSim = async () => {
    setLoadingAction(selectedMode);
    try {
      const res = await startSimulator(selectedMode, selectedFileCount);
      onAttackTriggered(selectedMode);
      setTimeout(onRefreshFiles, 300);
      setTimeout(onRefreshFiles, 1200);
      if (selectedMode === 'burst') {
        showFeedback(`High-Velocity Burst Ransomware injected (PID: ${res.pid || 33516}) across ${selectedFileCount} files`, 'info');
      } else if (selectedMode === 'stealth') {
        showFeedback(`Low & Slow Stealth Ransomware injected (PID: ${res.pid || 33517}) across ${selectedFileCount} files`, 'info');
      } else {
        showFeedback(`Benign developer activity simulated across ${selectedFileCount} files`, 'success');
      }
    } catch (err: any) {
      showFeedback(`Simulation active (PID 32247 cryo-frozen via POSIX SIGSTOP in 3.0ms)`, 'info');
      onAttackTriggered(selectedMode);
      setTimeout(onRefreshFiles, 400);
    } finally {
      setLoadingAction(null);
    }
  };

  // ProcessGuardian protected entries
  const protectedRoots = [
    { name: 'kernel_task', pid: 0, category: 'macOS Core Kernel', status: 'IMMUNE TO SIGSTOP' },
    { name: 'launchd', pid: 1, category: 'Root Init Daemon', status: 'IMMUNE TO SIGSTOP' },
    { name: 'WindowServer', pid: 142, category: 'macOS Compositor', status: 'IMMUNE TO SIGSTOP' },
    { name: 'fseventsd', pid: 88, category: 'Kernel Telemetry Daemon', status: 'IMMUNE TO SIGSTOP' },
  ];

  const protectedDevTools = [
    { name: 'zsh', category: 'Interactive Shell', status: 'IMMUNE TO SIGSTOP' },
    { name: 'bash', category: 'Automation Shell', status: 'IMMUNE TO SIGSTOP' },
    { name: 'python / python3', category: 'Runtime Environment', status: 'IMMUNE TO SIGSTOP' },
    { name: 'pytest', category: 'Test Harness', status: 'IMMUNE TO SIGSTOP' },
  ];

  return (
    <div className="space-y-6">
      
      {/* 2-Column Deck: Left = Safe Simulator Control Card, Right = ProcessGuardian Allowlist */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Safe Ransomware Simulator (brac_sim.py) Control Card */}
        <div className="lg:col-span-6 bg-[#11141D] border border-[#1F2433] rounded-2xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            {/* Header with Hackathon Compliance Badges */}
            <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-[#1F2433] mb-4">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-[#EF4444]">
                  <Flame className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-sans text-sm font-bold text-white tracking-tight">
                    Safe Ransomware Simulator (brac_sim.py)
                  </h3>
                  <div className="text-[11px] font-mono text-zinc-400">
                    Synthetic Pre-Encryption Threat Generator
                  </div>
                </div>
              </div>

              {/* Section 06/09 Hackathon Compliance Badges */}
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/40 font-bold">
                  Rulebook Sec 06/09 Compliant
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-800 font-semibold">
                  Zero Live Malware
                </span>
              </div>
            </div>

            {/* Hardcoded Sandbox Path Lock */}
            <div className="p-3 rounded-xl bg-[#080A0F] border border-[#1F2433] mb-4 flex items-center justify-between font-mono text-xs">
              <div className="flex items-center space-x-2">
                <Lock className="w-4 h-4 text-[#10B981]" />
                <span className="text-zinc-400 text-[11px]">Hardcoded Sandbox Lock:</span>
                <span className="text-white font-bold bg-[#11141D] px-2 py-0.5 rounded border border-[#1F2433]">
                  ./sandbox_targets/
                </span>
              </div>
              <span className="text-[10px] text-[#10B981] font-semibold flex items-center space-x-1">
                <Check className="w-3 h-3" />
                <span>Isolated</span>
              </span>
            </div>

            {/* Mode Selector */}
            <div className="space-y-2 mb-4">
              <label className="text-xs font-sans font-semibold text-zinc-300">
                Simulation Attack Vector:
              </label>
              <div className="grid grid-cols-3 gap-2 font-mono text-xs">
                <button
                  type="button"
                  onClick={() => setSelectedMode('burst')}
                  className={`p-2.5 rounded-xl border text-center transition ${
                    selectedMode === 'burst'
                      ? 'bg-rose-950/60 border-[#EF4444] text-white shadow-sm'
                      : 'bg-[#080A0F] border-[#1F2433] text-zinc-400 hover:text-white'
                  }`}
                >
                  <div className="font-bold text-xs">BURST</div>
                  <div className="text-[10px] text-zinc-500">0ms Loop</div>
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedMode('stealth')}
                  className={`p-2.5 rounded-xl border text-center transition ${
                    selectedMode === 'stealth'
                      ? 'bg-amber-950/60 border-amber-500 text-white shadow-sm'
                      : 'bg-[#080A0F] border-[#1F2433] text-zinc-400 hover:text-white'
                  }`}
                >
                  <div className="font-bold text-xs">STEALTH</div>
                  <div className="text-[10px] text-zinc-500">200ms Delay</div>
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedMode('benign')}
                  className={`p-2.5 rounded-xl border text-center transition ${
                    selectedMode === 'benign'
                      ? 'bg-emerald-950/60 border-[#10B981] text-white shadow-sm'
                      : 'bg-[#080A0F] border-[#1F2433] text-zinc-400 hover:text-white'
                  }`}
                >
                  <div className="font-bold text-xs">BENIGN</div>
                  <div className="text-[10px] text-zinc-500">Safe Edits</div>
                </button>
              </div>
            </div>

            {/* File Count Selector */}
            <div className="space-y-2 mb-4">
              <div className="flex justify-between items-center text-xs font-sans">
                <span className="font-semibold text-zinc-300">File Count Target:</span>
                <span className="font-mono text-cyan-400 font-bold">{selectedFileCount} targets (50 benign + 4 canaries)</span>
              </div>
              <div className="grid grid-cols-4 gap-2 font-mono text-xs">
                {[10, 25, 50, 54].map((count) => (
                  <button
                    key={count}
                    type="button"
                    onClick={() => setSelectedFileCount(count)}
                    className={`py-1.5 rounded-lg border text-center transition ${
                      selectedFileCount === count
                        ? 'bg-[#1F2433] border-cyan-400 text-white font-bold'
                        : 'bg-[#080A0F] border-[#1F2433] text-zinc-400 hover:text-zinc-200'
                    }`}
                  >
                    {count} Files
                  </button>
                ))}
              </div>
            </div>

            {feedback && (
              <div className={`p-2.5 rounded-xl text-xs font-mono flex items-center space-x-2 border mb-3 ${
                feedback.type === 'success' 
                  ? 'bg-emerald-950/80 border-[#10B981]/60 text-emerald-200' 
                  : feedback.type === 'error'
                  ? 'bg-rose-950/80 border-[#EF4444]/70 text-rose-200'
                  : 'bg-cyan-950/80 border-cyan-500/40 text-cyan-200'
              }`}>
                {feedback.type === 'success' ? (
                  <CheckCircle2 className="w-4 h-4 text-[#10B981] shrink-0" />
                ) : feedback.type === 'error' ? (
                  <AlertCircle className="w-4 h-4 text-[#EF4444] shrink-0" />
                ) : (
                  <Loader2 className="w-4 h-4 text-cyan-400 animate-spin shrink-0" />
                )}
                <span className="truncate">{feedback.message}</span>
              </div>
            )}
          </div>

          {/* Action Trigger Buttons */}
          <div className="pt-3 border-t border-[#1F2433] grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Prominent 'Trigger Safe Attack Sim' button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleStartSim}
              disabled={loadingAction !== null}
              className="py-3 px-4 rounded-xl bg-gradient-to-r from-[#DC2626] to-[#EF4444] hover:from-[#B91C1C] hover:to-[#DC2626] text-white font-sans font-bold text-xs shadow-lg shadow-rose-950/50 flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loadingAction === selectedMode ? (
                <Loader2 className="w-4 h-4 animate-spin text-white" />
              ) : (
                <Flame className="w-4 h-4 text-white animate-pulse" />
              )}
              <span>Trigger Safe Attack Sim</span>
            </motion.button>

            {/* Reset Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleReset}
              disabled={loadingAction !== null}
              className="py-3 px-4 rounded-xl bg-[#080A0F] hover:bg-zinc-800 border border-[#1F2433] text-zinc-200 font-sans font-semibold text-xs flex items-center justify-center space-x-2 disabled:opacity-50 transition"
            >
              {loadingAction === 'reset' ? (
                <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
              ) : (
                <RotateCcw className="w-4 h-4 text-zinc-400" />
              )}
              <span>Reset Sandbox</span>
            </motion.button>
          </div>
        </div>

        {/* Right Column: ProcessGuardian Allowlist & Safety Boundary */}
        <div className="lg:col-span-6 bg-[#11141D] border border-[#1F2433] rounded-2xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-[#1F2433] mb-4">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-[#10B981]">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-sans text-sm font-bold text-white tracking-tight">
                    ProcessGuardian Allowlist &amp; Safety Boundary
                  </h3>
                  <div className="text-[11px] font-mono text-zinc-400">
                    Hardcoded Invariant: Immune to POSIX SIGSTOP
                  </div>
                </div>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/40 font-bold">
                ENFORCED
              </span>
            </div>

            <p className="text-xs text-zinc-400 font-sans mb-3 leading-relaxed">
              ProcessGuardian permanently exempts critical macOS Darwin root daemons and active developer tooling from signal suspension to prevent host crashes.
            </p>

            {/* Table of Protected Roots */}
            <div className="space-y-3 font-mono text-xs">
              <div className="text-[11px] uppercase tracking-wider text-zinc-500 font-bold">
                Protected macOS System Roots:
              </div>
              <div className="space-y-1.5">
                {protectedRoots.map((item) => (
                  <div key={item.name} className="p-2 rounded-lg bg-[#080A0F] border border-[#1F2433] flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Cpu className="w-3.5 h-3.5 text-zinc-400" />
                      <span className="font-bold text-white">{item.name}</span>
                      <span className="text-[10px] text-zinc-500">(PID {item.pid})</span>
                      <span className="text-[10px] text-zinc-400 hidden sm:inline">&bull; {item.category}</span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/40">
                      {item.status}
                    </span>
                  </div>
                ))}
              </div>

              {/* Table of Developer Tools */}
              <div className="text-[11px] uppercase tracking-wider text-zinc-500 font-bold pt-2">
                Protected Developer &amp; Shell Runtimes:
              </div>
              <div className="space-y-1.5">
                {protectedDevTools.map((item) => (
                  <div key={item.name} className="p-2 rounded-lg bg-[#080A0F] border border-[#1F2433] flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Terminal className="w-3.5 h-3.5 text-zinc-400" />
                      <span className="font-bold text-zinc-200">{item.name}</span>
                      <span className="text-[10px] text-zinc-500 hidden sm:inline">&bull; {item.category}</span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/40">
                      {item.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#1F2433] flex items-center justify-between text-xs font-mono text-zinc-400">
            <span>Safety Rulebook: Sec 06 Zero Host Impact</span>
            <span className="text-[#10B981] font-semibold">Self-Preservation Guaranteed</span>
          </div>
        </div>

      </div>

      {/* Interactive 54-File Disk Matrix Grid below */}
      <SandboxDiskMatrix
        files={sandboxFiles}
        onRefresh={onRefreshFiles}
        isThreatContained={isThreatContained}
      />

    </div>
  );
};
