import React, { useState } from 'react';
import { 
  ShieldAlert, 
  RotateCcw, 
  Skull, 
  Play, 
  Loader2, 
  AlertOctagon, 
  CheckCircle, 
  Activity, 
  Sparkles,
  Lock,
  Cpu
} from 'lucide-react';
import { AnalystAction, IncidentAlert } from '../types';
import { executeIncidentAction } from '../api';

interface IncidentPanelProps {
  incident: IncidentAlert | null;
  onActionComplete: (action: AnalystAction, result: string) => void;
}

export const IncidentPanel: React.FC<IncidentPanelProps> = ({
  incident,
  onActionComplete,
}) => {
  const [loadingAction, setLoadingAction] = useState<AnalystAction | null>(null);
  const [actionFeedback, setActionFeedback] = useState<{ message: string; success: boolean } | null>(null);

  const handleAction = async (action: AnalystAction) => {
    if (!incident) return;
    setLoadingAction(action);
    setActionFeedback(null);
    try {
      const res = await executeIncidentAction(incident.incident_id || 'latest', action);
      const isSuccess = res.status === 'success';
      setActionFeedback({
        message: res.result || `Action ${action} completed successfully`,
        success: isSuccess,
      });
      onActionComplete(action, res.result);
    } catch (err: any) {
      setActionFeedback({
        message: err.message || `Action ${action} failed`,
        success: false,
      });
    } finally {
      setLoadingAction(null);
    }
  };

  const isFrozen = incident && incident.status === 'CONTAINED';
  const hasCanaryHit = incident?.xai_breakdown.some(
    (x) => x.factor.toUpperCase().includes('CANARY') && x.weight > 0
  );

  return (
    <div className={`bg-cyber-900 border rounded-xl p-4 shadow-xl flex flex-col justify-between transition-all duration-300 ${
      isFrozen ? 'border-red-500/70 glow-crimson' : 'border-cyber-800'
    }`}>
      {/* Panel Header */}
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-cyber-800/80 mb-3">
          <div className="flex items-center space-x-2">
            <ShieldAlert className={`w-4 h-4 ${isFrozen ? 'text-red-400 animate-pulse' : 'text-slate-400'}`} />
            <h3 className="font-mono text-sm font-bold tracking-wider text-slate-200 uppercase">
              Cryo-Quarantine &amp; Explainable AI (XAI)
            </h3>
          </div>
          {incident ? (
            <span className={`px-2.5 py-0.5 rounded text-[11px] font-mono font-bold tracking-wider uppercase border ${
              isFrozen
                ? 'bg-red-950 text-red-300 border-red-500/60 animate-pulse'
                : incident.status === 'RESTORED'
                ? 'bg-emerald-950 text-emerald-300 border-emerald-500/50'
                : incident.status === 'TERMINATED'
                ? 'bg-slate-800 text-slate-300 border-slate-600'
                : 'bg-cyan-950 text-cyan-300 border-cyan-500/50'
            }`}>
              {isFrozen ? 'STATUS: FROZEN / SIGSTOP' : `STATUS: ${incident.status}`}
            </span>
          ) : (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyber-850 text-emerald-400 border border-cyber-700">
              STANDBY // NO THREATS
            </span>
          )}
        </div>

        {/* Incident Details Card */}
        {incident ? (
          <div className="space-y-4">
            {/* Culprit metadata grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 font-mono text-xs">
              <div className="bg-cyber-850/80 border border-cyber-800 p-2.5 rounded-lg">
                <div className="text-[10px] text-slate-400">CULPRIT PID</div>
                <div className="font-bold text-slate-100 flex items-center space-x-1 mt-0.5">
                  <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{incident.offending_pid}</span>
                </div>
              </div>

              <div className="bg-cyber-850/80 border border-cyber-800 p-2.5 rounded-lg">
                <div className="text-[10px] text-slate-400">PROCESS NAME</div>
                <div className="font-bold text-cyan-300 truncate mt-0.5" title={incident.process_name}>
                  {incident.process_name}
                </div>
              </div>

              <div className="bg-cyber-850/80 border border-cyber-800 p-2.5 rounded-lg">
                <div className="text-[10px] text-slate-400">CONTAINMENT LATENCY</div>
                <div className="font-bold text-amber-300 mt-0.5">
                  {incident.detection_latency_ms ? `${incident.detection_latency_ms.toFixed(1)} ms` : '< 20 ms'}
                </div>
              </div>

              <div className="bg-cyber-850/80 border border-cyber-800 p-2.5 rounded-lg">
                <div className="text-[10px] text-slate-400">CANARY INTEGRITY</div>
                <div className="mt-0.5">
                  {hasCanaryHit ? (
                    <span className="text-red-400 font-bold flex items-center space-x-1 animate-pulse">
                      <AlertOctagon className="w-3.5 h-3.5" />
                      <span>TRIPPED</span>
                    </span>
                  ) : (
                    <span className="text-emerald-400 font-semibold flex items-center space-x-1">
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>INTACT</span>
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Explainable AI (XAI) Attribution Breakdown */}
            <div className="bg-cyber-850/70 border border-cyber-800/90 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-1.5 text-xs font-mono font-semibold text-slate-200">
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Local Deterministic Feature Attribution (XAI)</span>
                </div>
                <span className="text-[10px] font-mono text-slate-400">
                  Risk Score: <strong className="text-red-400">{incident.risk_score.toFixed(1)}/100</strong>
                </span>
              </div>

              {/* Factor Bars */}
              <div className="space-y-2 mt-2">
                {incident.xai_breakdown && incident.xai_breakdown.length > 0 ? (
                  incident.xai_breakdown.map((item, idx) => {
                    const percentage = Math.min(100, Math.round(item.weight * 100));
                    const isCanary = item.factor.includes('CANARY');
                    const isEntropy = item.factor.includes('ENTROPY');
                    return (
                      <div key={idx} className="space-y-1">
                        <div className="flex justify-between text-[11px] font-mono text-slate-300">
                          <span className="truncate flex items-center space-x-1">
                            <span className={`w-1.5 h-1.5 rounded-full ${isCanary ? 'bg-amber-400' : isEntropy ? 'bg-rose-400' : 'bg-cyan-400'}`} />
                            <span>{item.factor}</span>
                          </span>
                          <span className="font-bold text-slate-200">{percentage}%</span>
                        </div>
                        <div className="w-full bg-cyber-950 rounded-full h-2 overflow-hidden border border-cyber-700/60">
                          <div
                            className={`h-full rounded-full transition-all duration-700 ${
                              isCanary
                                ? 'bg-gradient-to-r from-amber-500 to-amber-300'
                                : isEntropy
                                ? 'bg-gradient-to-r from-red-600 via-rose-500 to-red-400'
                                : 'bg-gradient-to-r from-cyan-600 to-cyan-400'
                            }`}
                            style={{ width: `${Math.max(percentage, 5)}%` }}
                          />
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-xs font-mono text-slate-400 italic py-1">
                    Isolation Forest Anomaly Vector &gt; 0.85
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="py-8 text-center flex flex-col items-center justify-center space-y-2 text-slate-500 font-mono text-xs">
            <Lock className="w-8 h-8 text-slate-600" />
            <p className="text-slate-400 font-semibold">Zero Active Threat Incidents</p>
            <p className="max-w-xs text-[11px]">
              Offline Isolation Forest and Canary Honeyfile tripwires are primed. Launch an attack above to observe real-time containment.
            </p>
          </div>
        )}
      </div>

      {/* Action Execution Feedback */}
      {actionFeedback && (
        <div className={`mt-3 p-2.5 rounded-lg border font-mono text-xs flex items-center space-x-2 ${
          actionFeedback.success 
            ? 'bg-emerald-950/70 border-emerald-500/40 text-emerald-300' 
            : 'bg-rose-950/70 border-rose-500/40 text-rose-300'
        }`}>
          {actionFeedback.success ? (
            <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : (
            <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0" />
          )}
          <span className="truncate">{actionFeedback.message}</span>
        </div>
      )}

      {/* Three Prominent Analyst Action Buttons */}
      <div className="pt-4 border-t border-cyber-800/80 mt-4">
        <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-2 font-semibold">
          Analyst Cryo-Remediation Controls:
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          
          {/* Button 1: 1-Click Shadow Rollback */}
          <button
            onClick={() => handleAction('ROLLBACK_RESTORE')}
            disabled={!incident || loadingAction !== null}
            className="group relative flex items-center justify-center space-x-2 px-3 py-2.5 rounded-lg border border-emerald-500/50 bg-emerald-950/60 hover:bg-emerald-900/70 text-emerald-200 transition-all font-mono text-xs font-bold shadow-lg disabled:opacity-40 disabled:cursor-not-allowed glow-green active:scale-95"
            title="Restore encrypted files from shadow cache and delete .locked artifacts"
          >
            {loadingAction === 'ROLLBACK_RESTORE' ? (
              <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
            ) : (
              <RotateCcw className="w-4 h-4 text-emerald-400 group-hover:-rotate-45 transition-transform" />
            )}
            <span>1-Click Rollback</span>
          </button>

          {/* Button 2: Terminate Process (SIGKILL) */}
          <button
            onClick={() => handleAction('TERMINATE_SIGKILL')}
            disabled={!incident || loadingAction !== null || incident.status === 'TERMINATED'}
            className="group relative flex items-center justify-center space-x-2 px-3 py-2.5 rounded-lg border border-rose-500/50 bg-rose-950/60 hover:bg-rose-900/70 text-rose-200 transition-all font-mono text-xs font-bold shadow-lg disabled:opacity-40 disabled:cursor-not-allowed glow-crimson active:scale-95"
            title="Permanently kill the frozen process using SIGKILL"
          >
            {loadingAction === 'TERMINATE_SIGKILL' ? (
              <Loader2 className="w-4 h-4 animate-spin text-rose-400" />
            ) : (
              <Skull className="w-4 h-4 text-rose-400" />
            )}
            <span>Terminate (SIGKILL)</span>
          </button>

          {/* Button 3: Resume Process (SIGCONT) */}
          <button
            onClick={() => handleAction('RESUME_SIGCONT')}
            disabled={!incident || loadingAction !== null || incident.status === 'RELEASED'}
            className="group relative flex items-center justify-center space-x-2 px-3 py-2.5 rounded-lg border border-cyan-500/50 bg-cyan-950/60 hover:bg-cyan-900/70 text-cyan-200 transition-all font-mono text-xs font-bold shadow-lg disabled:opacity-40 disabled:cursor-not-allowed glow-cyan active:scale-95"
            title="Resume frozen process (SIGCONT) in case of false positive"
          >
            {loadingAction === 'RESUME_SIGCONT' ? (
              <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
            ) : (
              <Play className="w-4 h-4 text-cyan-400" />
            )}
            <span>Resume (SIGCONT)</span>
          </button>

        </div>
      </div>
    </div>
  );
};
