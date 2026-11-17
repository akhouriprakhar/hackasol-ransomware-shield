import React, { useState } from 'react';
import { 
  Bot, 
  Sparkles, 
  Cpu, 
  CheckCircle2, 
  Copy, 
  RefreshCw, 
  AlertTriangle,
  Zap,
  Terminal,
  ShieldCheck
} from 'lucide-react';
import { CopilotMessage, IncidentAlert } from '../types';
import { fetchCopilotBriefing } from '../api';

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
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [manualNarrative, setManualNarrative] = useState<string | null>(null);

  const isStreaming = copilot?.status === 'streaming';
  const isAnalyzing = copilot?.status === 'analyzing';
  const isFallback = copilot?.fallback ?? false;
  const currentNarrative = manualNarrative || copilot?.narrative || '';

  const handleCopy = () => {
    if (!currentNarrative) return;
    navigator.clipboard.writeText(currentNarrative);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleManualRefresh = async () => {
    if (!incident) return;
    setIsRefreshing(true);
    try {
      const res = await fetchCopilotBriefing(incident.incident_id || 'latest');
      if (res && res.narrative) {
        setManualNarrative(res.narrative);
      }
      if (onRefresh) onRefresh();
    } catch (e) {
      console.error('Failed to refresh briefing:', e);
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className="bg-cyber-900 border border-cyber-800 rounded-xl p-4 shadow-xl flex flex-col justify-between transition-all duration-300 relative overflow-hidden">
      {/* Decorative cyber grid highlight */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 rounded-bl-full pointer-events-none" />

      {/* Card Header */}
      <div className="flex items-center justify-between pb-3 border-b border-cyber-800/80 mb-3">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Bot className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-mono text-sm font-bold tracking-wider text-slate-200 uppercase">
                AI Incident Briefing
              </h3>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/60 font-semibold">
                TIER-2 POST-FREEZE
              </span>
            </div>
            <div className="text-[10px] text-slate-400 font-mono">
              Local Ollama (Gemma:2b) &bull; Zero Freeze Latency Impact
            </div>
          </div>
        </div>

        {/* Model Engine Badge */}
        <div className="flex items-center space-x-2">
          {isStreaming ? (
            <span className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded text-[11px] font-mono font-bold tracking-wider bg-amber-950 text-amber-300 border border-amber-500/60 animate-pulse">
              <Sparkles className="w-3 h-3 animate-spin" />
              <span>STREAMING...</span>
            </span>
          ) : isAnalyzing ? (
            <span className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded text-[11px] font-mono font-bold tracking-wider bg-blue-950 text-blue-300 border border-blue-500/60 animate-pulse">
              <RefreshCw className="w-3 h-3 animate-spin" />
              <span>ANALYZING...</span>
            </span>
          ) : copilot?.done ? (
            <span className={`flex items-center space-x-1.5 px-2.5 py-0.5 rounded text-[11px] font-mono font-bold tracking-wider border ${
              isFallback
                ? 'bg-amber-950/70 text-amber-300 border-amber-600/60'
                : 'bg-emerald-950 text-emerald-300 border-emerald-500/60'
            }`}>
              {isFallback ? (
                <>
                  <AlertTriangle className="w-3 h-3 text-amber-400" />
                  <span>DETERMINISTIC XAI</span>
                </>
              ) : (
                <>
                  <Cpu className="w-3 h-3 text-emerald-400" />
                  <span>GEMMA:2B // OLLAMA</span>
                </>
              )}
            </span>
          ) : (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyber-850 text-slate-400 border border-cyber-700">
              STANDBY
            </span>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="space-y-4">
        {/* Streamed / Natural Language Briefing Box */}
        <div className="bg-cyber-950/90 border border-cyber-800/80 rounded-lg p-3.5 relative font-mono text-xs text-slate-200 min-h-[96px] flex flex-col justify-between">
          {currentNarrative ? (
            <div className="leading-relaxed space-y-2">
              <div className="text-slate-100 selection:bg-cyan-500/30">
                {currentNarrative}
                {isStreaming && (
                  <span className="inline-block w-2 h-4 ml-1 bg-cyan-400 animate-pulse align-middle" />
                )}
              </div>
            </div>
          ) : incident ? (
            <div className="flex items-center space-x-3 text-slate-400 py-3">
              <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
              <span>Generating Tier-2 natural language briefing from Gemma 2B...</span>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-4 text-center text-slate-500 space-y-1">
              <Terminal className="w-5 h-5 text-slate-600 mb-1" />
              <div className="text-xs font-mono">No active containment briefing.</div>
              <div className="text-[11px] text-slate-600 max-w-sm">
                When a threat breaches the &ge;80.0 risk threshold and is frozen via POSIX SIGSTOP, Gemma 2B synthesizes telemetry &amp; XAI factors here.
              </div>
            </div>
          )}

          {/* Action Row inside narrative box */}
          {currentNarrative && (
            <div className="pt-2 mt-2 border-t border-cyber-850 flex items-center justify-between text-[11px] text-slate-400">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>
                  {isFallback
                    ? '100% Deterministic Offline Rule Synthesis'
                    : 'Generated locally via Ollama gemma:2b'}
                </span>
              </div>
              <div className="flex items-center space-x-1">
                <button
                  onClick={handleCopy}
                  className="px-2 py-0.5 rounded bg-cyber-850 hover:bg-cyber-800 text-slate-300 hover:text-white border border-cyber-700/60 flex items-center space-x-1 transition"
                  title="Copy incident briefing"
                >
                  {copied ? (
                    <>
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      <span className="text-[10px] text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3" />
                      <span className="text-[10px]">Copy</span>
                    </>
                  )}
                </button>
                <button
                  onClick={handleManualRefresh}
                  disabled={isRefreshing || !incident}
                  className="px-2 py-0.5 rounded bg-cyber-850 hover:bg-cyber-800 text-slate-300 hover:text-white border border-cyber-700/60 flex items-center space-x-1 transition disabled:opacity-40"
                  title="Regenerate briefing"
                >
                  <RefreshCw className={`w-3 h-3 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
                  <span className="text-[10px]">Refresh</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Deterministic XAI Attribution Breakdown Bars */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
            <span className="flex items-center space-x-1">
              <Zap className="w-3 h-3 text-cyan-400" />
              <span className="font-semibold uppercase tracking-wider">Deterministic XAI Factors</span>
            </span>
            <span className="text-[10px] text-slate-500">Inference Latency: &lt; 50ms</span>
          </div>

          {incident && incident.xai_breakdown && incident.xai_breakdown.length > 0 ? (
            <div className="space-y-2">
              {incident.xai_breakdown.map((item, idx) => {
                const pct = Math.round(item.weight * 100);
                const isCanary = item.factor.toUpperCase().includes('CANARY');
                const isEntropy = item.factor.toUpperCase().includes('ENTROPY');
                
                const barColor = isCanary
                  ? 'bg-rose-500'
                  : isEntropy
                  ? 'bg-amber-500'
                  : 'bg-cyan-500';

                return (
                  <div key={idx} className="bg-cyber-850/60 border border-cyber-800 rounded p-2 text-xs font-mono">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`font-semibold ${
                        isCanary ? 'text-rose-300' : isEntropy ? 'text-amber-300' : 'text-cyan-300'
                      }`}>
                        {item.factor}
                      </span>
                      <span className="text-slate-400 font-bold">{pct}%</span>
                    </div>
                    <div className="w-full bg-cyber-950 h-1.5 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${barColor} transition-all duration-500`}
                        style={{ width: `${Math.max(5, pct)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
              <div className="bg-cyber-850/40 border border-cyber-800/60 p-2 rounded text-slate-500">
                <div className="text-[10px] text-slate-400 uppercase">Micro-Canary Honeyfiles</div>
                <div>Monitoring !_passwords, _aa_financials</div>
              </div>
              <div className="bg-cyber-850/40 border border-cyber-800/60 p-2 rounded text-slate-500">
                <div className="text-[10px] text-slate-400 uppercase">Shannon Entropy Engine</div>
                <div>4KB Chunk Fast H &gt; 7.5 Threshold</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer KPI Tag */}
      {incident && (
        <div className="mt-3 pt-2 border-t border-cyber-800 flex items-center justify-between text-[11px] font-mono text-slate-400">
          <div>
            Target PID: <span className="text-cyan-400 font-bold">{incident.offending_pid}</span>
          </div>
          <div>
            Freeze Latency: <span className="text-emerald-400 font-bold">{incident.detection_latency_ms.toFixed(1)}ms</span>
          </div>
          <div>
            Files Preserved: <span className="text-slate-200 font-bold">{Math.max(0, 54 - incident.files_affected_count)}</span> / 54
          </div>
        </div>
      )}
    </div>
  );
};
