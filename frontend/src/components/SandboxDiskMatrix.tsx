import React, { useState } from 'react';
import { 
  FileText, 
  FileCode, 
  FileSpreadsheet, 
  Lock, 
  ShieldCheck, 
  AlertTriangle, 
  HardDrive,
  RefreshCw,
  Eye,
  CheckCircle2,
  FileWarning
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { SandboxFile } from '../types';

interface SandboxDiskMatrixProps {
  files: SandboxFile[];
  onRefresh: () => void;
  isThreatContained: boolean;
}

export const SandboxDiskMatrix: React.FC<SandboxDiskMatrixProps> = ({
  files,
  onRefresh,
  isThreatContained,
}) => {
  const [selectedFile, setSelectedFile] = useState<SandboxFile | null>(null);

  const canaries = files.filter((f) => f.is_canary);
  const regulars = files.filter((f) => !f.is_canary);
  const lockedCount = files.filter((f) => f.is_locked).length;
  const intactCount = files.length - lockedCount;

  const getFileIcon = (file: SandboxFile) => {
    if (file.is_locked) {
      return <Lock className="w-3.5 h-3.5 text-rose-400 shrink-0" />;
    }
    if (file.is_canary) {
      return <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />;
    }
    if (file.name.endsWith('.json')) {
      return <FileCode className="w-3.5 h-3.5 text-cyan-400 shrink-0" />;
    }
    if (file.name.endsWith('.csv') || file.name.endsWith('.xlsx')) {
      return <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400 shrink-0" />;
    }
    return <FileText className="w-3.5 h-3.5 text-slate-400 shrink-0" />;
  };

  return (
    <div className="bg-[#11141D] border border-[#1F2433] rounded-2xl p-5 shadow-2xl backdrop-blur-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-white/[0.06]">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <HardDrive className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-sans text-sm font-semibold tracking-tight text-white">
                Sandbox Target Directory Disk Matrix
              </h3>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 font-semibold">
                APFS Volume
              </span>
            </div>
            <p className="text-xs text-zinc-400 font-sans mt-0.5">
              Live visual state of all 54 files monitored by Apple Silicon FSEvents kernel sensor
            </p>
          </div>
        </div>

        {/* Status Counters */}
        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-zinc-900/80 border border-white/[0.06]">
            <span className="text-zinc-400">Intact:</span>
            <span className="font-bold text-emerald-400 tabular-nums">{intactCount}</span>
            <span className="text-zinc-500">/ {files.length}</span>
          </div>

          <div className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border transition-colors ${
            lockedCount > 0 
              ? 'bg-rose-950/50 border-rose-500/60 text-rose-300 animate-pulse' 
              : 'bg-zinc-900/80 border-white/[0.06] text-zinc-300'
          }`}>
            <span className="text-zinc-400">Locked:</span>
            <span className={`font-bold tabular-nums ${lockedCount > 0 ? 'text-rose-400' : 'text-zinc-200'}`}>
              {lockedCount}
            </span>
          </div>

          <button
            onClick={onRefresh}
            className="p-1.5 rounded-lg bg-zinc-900/80 hover:bg-zinc-800 border border-white/[0.08] text-zinc-400 hover:text-white transition"
            title="Refresh Disk State"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 1. Canary Honeyfiles Strip */}
      <div className="pt-4 pb-3">
        <div className="flex items-center space-x-2 mb-2.5">
          <span className="inline-block w-2 h-2 rounded-full bg-amber-400 shadow-[0_0_8px_#f59e0b]"></span>
          <span className="text-xs font-semibold uppercase tracking-wider text-amber-300/90 font-mono">
            Micro-Canary Honeyfiles (Strategic First-Target Traps)
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
          {canaries.map((canary) => (
            <motion.div
              key={canary.name}
              whileHover={{ scale: 1.02 }}
              onClick={() => setSelectedFile(canary)}
              className={`p-2.5 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                canary.is_locked
                  ? 'bg-rose-950/40 border-rose-500/80 shadow-[0_0_15px_rgba(244,63,94,0.3)] animate-pulse'
                  : 'bg-amber-950/20 border-amber-500/40 hover:border-amber-400 shadow-[0_0_12px_rgba(245,158,11,0.15)]'
              }`}
            >
              <div className="flex items-center space-x-2 min-w-0">
                {getFileIcon(canary)}
                <span className="font-mono text-xs font-bold text-zinc-100 truncate">
                  {canary.name}
                </span>
              </div>
              <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${
                canary.is_locked ? 'bg-rose-900 text-rose-200' : 'bg-amber-900/60 text-amber-300'
              }`}>
                {canary.is_locked ? 'TRIPPED' : 'ARMED'}
              </span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* 2. Standard Business Files Matrix Grid */}
      <div className="pt-3">
        <div className="flex items-center justify-between mb-2.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono">
            Monitored Corporate Documents (50 Files)
          </span>
          <span className="text-[11px] text-zinc-500 font-mono">
            Click any block to view telemetry metadata
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-10 gap-1.5">
          {regulars.map((file) => (
            <motion.div
              key={file.name}
              whileHover={{ scale: 1.05 }}
              onClick={() => setSelectedFile(file)}
              className={`p-2 rounded-lg border text-center flex flex-col items-center justify-center cursor-pointer transition-all ${
                file.is_locked
                  ? 'bg-rose-950/60 border-rose-500 text-rose-200 shadow-[0_0_12px_rgba(244,63,94,0.4)] animate-pulse'
                  : selectedFile?.name === file.name
                  ? 'bg-cyan-950/40 border-cyan-400 text-white'
                  : 'bg-zinc-900/60 border-white/[0.04] hover:border-white/[0.2] text-zinc-300'
              }`}
            >
              <div className="mb-1">{getFileIcon(file)}</div>
              <span className="font-mono text-[10px] font-medium truncate w-full" title={file.name}>
                {file.name.replace('sample_doc_', '')}
              </span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* 3. Selected File Inspector Drawer / Banner */}
      <AnimatePresence>
        {selectedFile && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="mt-4 p-3.5 rounded-xl bg-zinc-900/90 border border-white/[0.08] flex flex-col sm:flex-row sm:items-center justify-between gap-3 font-mono text-xs"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-zinc-800 border border-white/[0.08]">
                {getFileIcon(selectedFile)}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-white text-sm">{selectedFile.name}</span>
                  {selectedFile.is_canary && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-amber-950 text-amber-300 border border-amber-600/50">
                      Canary Trap
                    </span>
                  )}
                  {selectedFile.is_locked ? (
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-rose-950 text-rose-300 border border-rose-600/50 font-bold">
                      Encrypted (.locked)
                    </span>
                  ) : (
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-600/50">
                      Intact / Protected
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-zinc-400 mt-0.5 truncate max-w-md">
                  Path: {selectedFile.path}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4 self-end sm:self-auto text-zinc-400">
              <div>
                Size: <strong className="text-zinc-200">{(selectedFile.size_bytes / 1024).toFixed(1)} KB</strong>
              </div>
              <div>
                Format: <strong className="text-cyan-400">{selectedFile.ext.toUpperCase()}</strong>
              </div>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-zinc-500 hover:text-white px-2 py-1 rounded bg-zinc-800 hover:bg-zinc-700 transition"
              >
                Dismiss
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
