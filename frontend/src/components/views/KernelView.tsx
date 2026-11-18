import React from 'react';
import { Terminal, ShieldCheck, Eye, Cpu, Filter } from 'lucide-react';
import { TelemetryEvent } from '../../types';
import { TelemetryFeed } from '../TelemetryFeed';

interface KernelViewProps {
  events: TelemetryEvent[];
  onClear: () => void;
}

export const KernelView: React.FC<KernelViewProps> = ({ events, onClear }) => {
  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="bg-[#11141D] border border-[#1F2433] rounded-2xl p-5 shadow-xl backdrop-blur-xl">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-sans text-base font-semibold text-white tracking-tight">
                  Apple Silicon FSEvents Kernel Stream &amp; Audit Trail
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800">
                  Ring Buffer
                </span>
              </div>
              <p className="text-xs text-zinc-400 font-sans mt-0.5">
                Low-latency filesystem telemetry hooks capturing Shannon entropy deltas, file writes, and canary hits
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 text-xs font-mono">
            <div className="px-3 py-1.5 rounded-lg bg-zinc-900 border border-white/[0.08] text-zinc-300 flex items-center space-x-1.5">
              <Eye className="w-3.5 h-3.5 text-cyan-400" />
              <span>Watchdog FSEvents Active</span>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-zinc-900 border border-white/[0.08] text-zinc-300 flex items-center space-x-1.5">
              <Cpu className="w-3.5 h-3.5 text-emerald-400" />
              <span>Sub-2ms Evaluation</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Telemetry Feed */}
      <div className="w-full">
        <TelemetryFeed
          events={events}
          onClear={onClear}
        />
      </div>

    </div>
  );
};
