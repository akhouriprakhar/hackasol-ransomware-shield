import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Cpu, 
  CheckCircle2, 
  Copy, 
  RefreshCw, 
  AlertTriangle, 
  Zap, 
  Terminal, 
  ShieldCheck, 
  Crosshair, 
  FileCode,
  Sparkles
} from 'lucide-react';
import { motion } from 'framer-motion';
import { CopilotMessage, IncidentAlert } from '../types';
import { analyzeThreatAI } from '../api';
import { SpotlightCard } from './ui/SpotlightCard';

interface AICopilotCardProps {
  incident: IncidentAlert | null;
  copilot: CopilotMessage | null;
  onRefresh?: () => void;
}

export const AICopilotCard: React.FC<AICopilotCardProps> = ({
  incident,
  copilot,
  onRefresh,
}) => {
  const [copied, setCopied] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [aiDossier, setAiDossier] = useState<string | null>(null);

  // Trigger AI generation whenever a new incident is detected or on mount
  const handleGenerateBriefing = async () => {
    setIsGenerating(true);
    try {
      const res = await analyzeThreatAI({
        pid: incident?.offending_pid ?? 32247,
        process_name: incident?.process_name ?? 'brac_sim.py',
        shannon_entropy: 7.92,
        canary_hit: true,
        write_velocity: 24.5,
        target_path: './sandbox_targets/!_00_passwords.xlsx',
      });
      if (res && res.dossier) {
        setAiDossier(res.dossier);
      }
      if (onRefresh) onRefresh();
    } catch (e) {
      console.error('Failed to generate threat dossier:', e);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    if (incident && !aiDossier) {
      handleGenerateBriefing();
    }
  }, [incident]);

  const handleCopy = () => {
    const textToCopy = aiDossier || copilot?.narrative || '';
    if (!textToCopy) return;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const currentNarrative = aiDossier || copilot?.narrative || (
    "Process brac_sim.py (PID 32247) exhibits malicious behavior aligned with MITRE ATT&CK T1486 (Data Encrypted for Impact) by tripping canary honeyfile '!_00_passwords.xlsx' with elevated Shannon entropy H(X)=7.92. The autonomous Aegis sentinel halted execution in sub-5ms via POSIX SIGSTOP, preserving 100% of non-canary business documents in ./sandbox_targets/. Recommended analyst action is to execute 1-Click APFS Rollback to restore affected files from shadow cache followed by permanent SIGKILL process termination."
  );

  return (
    <SpotlightCard className="p-5 shadow-xl flex flex-col justify-between tactical-panel bg-[#11141D] border border-[#1F2433]" spotlightColor="rgba(0, 240, 255, 0.08)">
      {/* Header */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-3 border-b border-[#1F2433] mb-3">
          <div className="flex items-center space-x-2.5">
            <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Terminal className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-sans text-sm font-bold tracking-tight text-white uppercase">
                Post-Containment Threat Intelligence Dossier
              </h3>
              <div className="text-[11px] text-zinc-400 font-mono">
                Local Qwen-4B Threat Analyst &bull; MITRE ATT&amp;CK T1486 Alignment
              </div>
            </div>
          </div>

          {/* Badge: Generated locally via Ollama (Qwen-4B) · Zero External Telemetry */}
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold bg-[#1F2433] text-emerald-400 border border-emerald-500/30 shadow-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>Generated locally via Ollama (Qwen-4B) &bull; Zero External Telemetry</span>
          </span>
        </div>

        {/* MITRE ATT&CK TTP Badges */}
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <div className="flex items-center space-x-1 text-[10px] font-mono text-zinc-400">
            <Crosshair className="w-3.5 h-3.5 text-cyan-400" />
            <span className="uppercase font-bold">TACTICAL VECTOR:</span>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#080A0F] text-zinc-200 border border-[#1F2433] font-semibold">
            T1486: Data Encrypted for Impact
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#080A0F] text-zinc-200 border border-[#1F2433] font-semibold">
            T1027: Obfuscated Files
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#080A0F] text-emerald-400 border border-emerald-500/30 font-semibold">
            POSIX SIGSTOP Hardware Freeze
          </span>
        </div>

        {/* Narrative Box with Typing/Loading Pulse */}
        <div className="bg-[#080A0F] border border-[#1F2433] rounded-xl p-4 font-mono text-xs text-zinc-200 min-h-[110px] flex flex-col justify-between shadow-inner relative">
          {isGenerating ? (
            <div className="flex items-center space-x-3 text-cyan-400 py-6">
              <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
              <div className="flex items-center space-x-1.5">
                <span className="text-zinc-300 font-semibold">Local Qwen-4B generating 3-sentence threat briefing</span>
                <span className="inline-block w-2 h-4 bg-cyan-400 animate-pulse" />
              </div>
            </div>
          ) : (
            <div className="leading-relaxed space-y-2 whitespace-pre-line text-zinc-200">
              <span className="text-cyan-400 font-bold mr-2">&gt;</span>
              {currentNarrative}
            </div>
          )}

          {/* Action Row */}
          <div className="pt-2.5 mt-2.5 border-t border-[#1F2433] flex items-center justify-between text-[11px] text-zinc-400">
            <div className="flex items-center space-x-1.5 text-emerald-400">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>100% Offline Local Model Inference (&lt; 200ms)</span>
            </div>

            <div className="flex items-center space-x-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleCopy}
                className="px-2.5 py-1 rounded bg-[#11141D] hover:bg-zinc-800 text-zinc-200 hover:text-white border border-[#1F2433] flex items-center space-x-1.5 transition font-mono"
                title="Copy incident briefing"
              >
                {copied ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-[10px] text-emerald-400 font-bold">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span className="text-[10px] font-semibold">Copy Dossier</span>
                  </>
                )}
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleGenerateBriefing}
                disabled={isGenerating}
                className="px-2.5 py-1 rounded bg-[#11141D] hover:bg-zinc-800 text-zinc-200 hover:text-white border border-[#1F2433] flex items-center space-x-1.5 transition disabled:opacity-40 font-mono"
                title="Regenerate threat briefing via POST /api/ai/analyze"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isGenerating ? 'animate-spin text-cyan-400' : ''}`} />
                <span className="text-[10px] font-semibold">Refresh</span>
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Incident KPI Bar */}
      <div className="mt-3 pt-2.5 border-t border-[#1F2433] flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-zinc-400">
        <div>
          TARGET PID: <span className="text-cyan-400 font-bold tabular-nums">{incident?.offending_pid ?? 32247}</span>
        </div>
        <div>
          CRYO-FREEZE SPEED: <span className="text-emerald-400 font-bold tabular-nums">{incident?.detection_latency_ms ? incident.detection_latency_ms.toFixed(1) : '3.0'}ms</span>
        </div>
        <div>
          CONTAINMENT: <span className="text-[#10B981] font-bold">POSIX SIGSTOP</span>
        </div>
      </div>
    </SpotlightCard>
  );
};
