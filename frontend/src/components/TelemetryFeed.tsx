import React, { useState } from 'react';
import { 
  Terminal, 
  Search, 
  Trash2, 
  AlertTriangle, 
  FileCode, 
  FileText, 
  Lock 
} from 'lucide-react';
import { TelemetryEvent } from '../types';

interface TelemetryFeedProps {
  events: TelemetryEvent[];
  onClear: () => void;
}

export const TelemetryFeed: React.FC<TelemetryFeedProps> = ({ events, onClear }) => {
  const [filter, setFilter] = useState('');

  const filteredEvents = events.filter((e) => {
    if (!filter) return true;
    const q = filter.toLowerCase();
    return (
      e.file_path.toLowerCase().includes(q) ||
      e.event_type.toLowerCase().includes(q) ||
      (e.is_canary && 'canary'.includes(q))
    );
  });

  const getEventBadge = (type: string) => {
    switch (type) {
      case 'FILE_CREATE':
        return 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40';
      case 'FILE_MODIFY':
        return 'bg-cyan-950/80 text-cyan-400 border-cyan-500/40';
      case 'FILE_RENAME':
        return 'bg-purple-950/80 text-purple-400 border-purple-500/40';
      case 'FILE_DELETE':
        return 'bg-rose-950/80 text-rose-400 border-rose-500/40';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-600';
    }
  };

  const formatTime = (ts: number) => {
    const d = new Date(ts * 1000);
    return d.toTimeString().split(' ')[0] + '.' + String(d.getMilliseconds()).padStart(3, '0');
  };

  return (
    <div className="bg-cyber-900 border border-cyber-800 rounded-xl p-4 shadow-xl flex flex-col h-[400px]">
      {/* Feed Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-cyber-800/80">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <h3 className="font-mono text-sm font-bold tracking-wider text-slate-200 uppercase">
            Live FSEvents Telemetry Stream
          </h3>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyber-800 text-cyan-400 border border-cyber-700">
            {events.length} Events
          </span>
        </div>

        {/* Filter & Controls */}
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2 text-slate-400" />
            <input
              type="text"
              placeholder="Filter path / type..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-cyber-850 border border-cyber-700/80 rounded-md pl-8 pr-2.5 py-1 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-36 sm:w-44"
            />
          </div>

          <button
            onClick={onClear}
            className="p-1.5 rounded-md border border-slate-700 hover:border-slate-500 bg-cyber-850 hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
            title="Clear Stream"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Stream Table / Rows */}
      <div className="flex-1 overflow-y-auto mt-2 space-y-1.5 pr-1 font-mono text-xs">
        {filteredEvents.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs">
            <Terminal className="w-6 h-6 text-slate-600 mb-1" />
            <span>Awaiting filesystem events from watchdog sensor...</span>
          </div>
        ) : (
          filteredEvents.map((evt) => {
            const isEncrypted = evt.file_path.endsWith('.locked') || evt.entropy_after > 7.5;
            const deltaPositive = evt.entropy_delta > 0;
            const isCanary = evt.is_canary;

            return (
              <div
                key={evt.event_id}
                className={`p-2 rounded-lg border transition-all flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5 ${
                  isCanary
                    ? 'bg-amber-950/30 border-amber-500/50 glow-amber'
                    : isEncrypted
                    ? 'bg-red-950/30 border-red-500/40 glow-crimson'
                    : 'bg-cyber-850/50 border-cyber-800 hover:border-cyber-700'
                }`}
              >
                {/* Left: Time + Badge + File Path */}
                <div className="flex items-center space-x-2.5 min-w-0">
                  <span className="text-[10px] text-slate-500 shrink-0">
                    {formatTime(evt.timestamp)}
                  </span>

                  <span className={`text-[10px] px-1.5 py-0.5 rounded border uppercase font-bold shrink-0 ${getEventBadge(evt.event_type)}`}>
                    {evt.event_type.replace('FILE_', '')}
                  </span>

                  {isCanary && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-500/60 font-bold shrink-0 flex items-center space-x-1 animate-pulse">
                      <AlertTriangle className="w-3 h-3" />
                      <span>CANARY</span>
                    </span>
                  )}

                  <div className="truncate text-slate-300 flex items-center space-x-1" title={evt.file_path}>
                    {isEncrypted ? (
                      <Lock className="w-3.5 h-3.5 text-red-400 shrink-0 inline" />
                    ) : (
                      <FileText className="w-3.5 h-3.5 text-slate-400 shrink-0 inline" />
                    )}
                    <span className={isEncrypted ? 'text-red-300 font-semibold' : ''}>
                      {evt.file_path}
                    </span>
                  </div>
                </div>

                {/* Right: Entropy Delta & Attribution PID */}
                <div className="flex items-center space-x-3 shrink-0 text-[11px] self-end sm:self-auto">
                  <div className="text-slate-400 flex items-center space-x-1">
                    <span>H(X):</span>
                    <span className="text-slate-300">{evt.entropy_before.toFixed(2)}</span>
                    <span className="text-slate-500">→</span>
                    <span className={`font-bold ${evt.entropy_after >= 7.5 ? 'text-red-400' : 'text-cyan-300'}`}>
                      {evt.entropy_after.toFixed(2)}
                    </span>
                    <span className={`text-[10px] ml-1 ${deltaPositive ? 'text-rose-400' : 'text-slate-500'}`}>
                      ({deltaPositive ? '+' : ''}{evt.entropy_delta.toFixed(2)})
                    </span>
                  </div>

                  {evt.pid && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyber-950 text-slate-400 border border-cyber-800">
                      PID:{evt.pid}
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
