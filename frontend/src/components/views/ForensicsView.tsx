import React from 'react';
import { 
  ShieldAlert, 
  RotateCcw, 
  Skull, 
  Play, 
  FileSearch, 
  CheckCircle2, 
  Cpu, 
  Sparkles, 
  Terminal,
  Activity,
  Layers,
  Lock
} from 'lucide-react';
import { AnalystAction, CopilotMessage, IncidentAlert } from '../../types';
import { IncidentPanel } from '../IncidentPanel';
import { AICopilotCard } from '../AICopilotCard';

interface ForensicsViewProps {
  incident: IncidentAlert | null;
  copilot: CopilotMessage | null;
  onActionComplete: (action: AnalystAction, result: string) => void;
  onRefreshCopilot: () => void;
}

export const ForensicsView: React.FC<ForensicsViewProps> = ({
  incident,
  copilot,
  onActionComplete,
  onRefreshCopilot,
}) => {
  return (
    <div className="space-y-6">
      
      {/* Top Forensics Dispatch Header */}
      <div className="bg-[#11141D] border border-[#1F2433] rounded-2xl p-5 shadow-xl backdrop-blur-xl">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-sans text-base font-semibold text-white tracking-tight">
                  Incident Forensics &amp; Cryo-Remediation Vault
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-950 text-rose-300 border border-rose-800">
                  {incident ? `INCIDENT #${incident.incident_id?.slice(-6) || 'ACTIVE'}` : 'MONITORING'}
                </span>
              </div>
              <p className="text-xs text-zinc-400 font-sans mt-0.5">
                Investigate hardware-frozen processes, inspect XAI attribution factors, and execute instant shadow rollbacks
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2 text-xs font-mono">
            <span className="px-3 py-1.5 rounded-lg bg-zinc-900 border border-white/[0.08] text-zinc-300">
              MITRE: <strong className="text-cyan-400">T1486</strong>
            </span>
            <span className="px-3 py-1.5 rounded-lg bg-zinc-900 border border-white/[0.08] text-zinc-300">
              Signal: <strong className="text-rose-400">SIGSTOP</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Primary Split Investigation Workbench */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left: Cryo-Quarantine Dossier & XAI Attribution (6 cols) */}
        <div className="lg:col-span-6">
          <IncidentPanel
            incident={incident}
            onActionComplete={onActionComplete}
          />
        </div>

        {/* Right: Tier-2 Local Gemma 2B Threat Intelligence Dispatch (6 cols) */}
        <div className="lg:col-span-6">
          <AICopilotCard
            incident={incident}
            copilot={copilot}
            onRefresh={onRefreshCopilot}
          />
        </div>

      </div>

    </div>
  );
};
