import React, { useState } from 'react';
import { 
  Terminal, 
  Search, 
  Trash2, 
  AlertTriangle, 
  FileCode, 
  FileText, 
  Lock,
  Pause,
  Play,
  Filter,
  CheckCircle2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { TelemetryEvent } from '../types';
import { SpotlightCard } from './ui/SpotlightCard';
import { NumberTicker } from './ui/NumberTicker';

interface TelemetryFeedProps {
  events: TelemetryEvent[];
  onClear: () => void;
}

export const TelemetryFeed: React.FC<TelemetryFeedProps> = ({ events, onClear }) => {
  const [filter, setFilter] = useState('');
  const [activeQuickFilter, setActiveQuickFilter] = useState<'ALL' | 'CANARY' | 'ENCRYPTED' | 'MODIFIED'>('ALL');

  const filteredEvents = events.filter((e) => {
    // Quick category filters
    if (activeQuickFilter === 'CANARY' && !e.is_canary) return false;
    if (activeQuickFilter === 'ENCRYPTED' && !e.file_path.endsWith('.locked') && e.entropy_after < 7.5) return false;
    if (activeQuickFilter === 'MODIFIED' && e.event_type !== 'FILE_MODIFY') return false;

    // Search query
    if (!filter) return true;
    const q = filter.toLowerCase();
    return (
      e.file_path.toLowerCase().includes(q) ||
      e.event_type.toLowerCase().includes(q) ||
      (e.process_name && e.process_name.toLowerCase().includes(q)) ||
      (e.is_canary && 'canary'.includes(q))
    );
  });

  const getEventBadge = (type: string) => {
    switch (type) {
      case 'FILE_CREATE':
        return 'bg-emerald-950/80 text-tactical-emerald border-emerald-500/50';
      case 'FILE_MODIFY':
        return 'bg-[#00f0ff]/10 text-tactical-cyan border-[#00f0ff]/40';
      case 'FILE_RENAME':
        return 'bg-amber-950/80 text-tactical-amber border-tactical-amber/50';
      case 'FILE_DELETE':
        return 'bg-rose-950/80 text-tactical-crimson border-tactical-crimson/50';
      default:
        return 'bg-[#141c30] text-slate-300 border-[#1d2944]';
    }
  };

  const formatTime = (ts: number) => {
    const d = new Date(ts * 1000);
    return d.toTimeString().split(' ')[0] + '.' + String(d.getMilliseconds()).padStart(3, '0');
  };

  return (
    <SpotlightCard className="p-4 shadow-xl flex flex-col h-[420px] tactical-panel" spotlightColor="rgba(0, 240, 255, 0.08)">
      {/* Feed Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#141c30]">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-tactical-cyan">
            <Terminal className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-mono text-sm font-bold tracking-wider text-slate-100 uppercase">
                REAL-TIME FSEVENTS TELEMETRY STREAM
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#0e1422] text-tactical-cyan border border-[#141c30] font-bold tabular-nums">
                <NumberTicker value={events.length} /> EVENTS
              </span>
            </div>
            <p className="text-[11px] font-mono text-slate-400">
              macOS FSEvents kernel hook &bull; 4KB block Shannon entropy calculations &bull; Micro-canary sensors
            </p>
          </div>
        </div>

        {/* Quick Filter Badges & Search */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Quick Filter Buttons */}
          <div className="inline-flex rounded-lg border border-[#141c30] bg-[#05070b] p-0.5 font-mono text-[10px]">
            <button
              onClick={() => setActiveQuickFilter('ALL')}
              className={`px-2 py-0.5 rounded font-semibold transition ${
                activeQuickFilter === 'ALL'
                  ? 'bg-[#141c30] text-tactical-cyan border border-[#1d2944]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              ALL
            </button>
            <button
              onClick={() => setActiveQuickFilter('CANARY')}
              className={`px-2 py-0.5 rounded font-semibold transition ${
                activeQuickFilter === 'CANARY'
                  ? 'bg-amber-950/80 text-tactical-amber border border-tactical-amber/50'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              CANARY
            </button>
            <button
              onClick={() => setActiveQuickFilter('ENCRYPTED')}
              className={`px-2 py-0.5 rounded font-semibold transition ${
                activeQuickFilter === 'ENCRYPTED'
                  ? 'bg-rose-950/80 text-tactical-crimson border border-tactical-crimson/50'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              HIGH ENTROPY
            </button>
            <button
              onClick={() => setActiveQuickFilter('MODIFIED')}
              className={`px-2 py-0.5 rounded font-semibold transition ${
                activeQuickFilter === 'MODIFIED'
                  ? 'bg-[#00f0ff]/10 text-tactical-cyan border border-[#00f0ff]/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              WRITES
            </button>
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2 text-slate-400" />
            <input
              type="text"
              placeholder="Filter file or process..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-[#05070b] border border-[#141c30] rounded-md pl-8 pr-2.5 py-1 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#00f0ff] w-36 sm:w-44 transition"
            />
          </div>

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={onClear}
            className="p-1.5 rounded-md border border-[#141c30] hover:border-slate-500 bg-[#05070b] hover:bg-[#141c30] text-slate-400 hover:text-slate-100 transition-colors"
            title="Clear Stream"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </motion.button>
        </div>
      </div>

      {/* Stream Table / Rows */}
      <div className="flex-1 overflow-y-auto mt-2 space-y-1 pr-1 font-mono text-xs">
        {filteredEvents.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs">
            <Terminal className="w-6 h-6 text-slate-600 mb-1" />
            <span className="font-semibold text-slate-400">Awaiting filesystem events from watchdog sensor...</span>
            <span className="text-[10px] text-slate-600">Trigger sandbox activity or attacks using the stage controls above</span>
          </div>
        ) : (
          filteredEvents.map((evt) => {
            const isEncrypted = evt.file_path.endsWith('.locked') || evt.entropy_after >= 7.5;
            const deltaPositive = evt.entropy_delta > 0;
            const isCanary = evt.is_canary;

            return (
              <div
                key={evt.event_id}
                className={`p-2 rounded-lg border transition-all flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5 ${
                  isCanary
                    ? 'bg-amber-950/40 border-tactical-amber/60 shadow-tactical-amber'
                    : isEncrypted
                    ? 'bg-rose-950/40 border-tactical-crimson/70 shadow-tactical-crimson'
                    : 'bg-[#060910] border-[#141c30] hover:border-[#1d2944]'
                }`}
              >
                {/* Left: Time + Badge + File Path */}
                <div className="flex items-center space-x-2.5 min-w-0">
                  <span className="text-[10px] text-slate-400 shrink-0 tabular-nums">
                    {formatTime(evt.timestamp)}
                  </span>

                  <span className={`text-[10px] px-1.5 py-0.5 rounded border uppercase font-bold shrink-0 ${getEventBadge(evt.event_type)}`}>
                    {evt.event_type.replace('FILE_', '')}
                  </span>

                  {isCanary && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-950 text-tactical-amber border border-tactical-amber/70 font-black shrink-0 flex items-center space-x-1 animate-pulse">
                      <AlertTriangle className="w-3 h-3" />
                      <span>CANARY TRIP</span>
                    </span>
                  )}

                  <div className="truncate text-slate-200 flex items-center space-x-1.5" title={evt.file_path}>
                    {isEncrypted ? (
                      <Lock className="w-3.5 h-3.5 text-tactical-crimson shrink-0 inline" />
                    ) : (
                      <FileText className="w-3.5 h-3.5 text-slate-400 shrink-0 inline" />
                    )}
                    <span className={`truncate ${isEncrypted ? 'text-rose-200 font-bold' : ''}`}>
                      {evt.file_path}
                    </span>
                  </div>
                </div>

                {/* Right: Entropy Delta & Attribution PID */}
                <div className="flex items-center space-x-3 shrink-0 text-[11px] self-end sm:self-auto">
                  <div className="text-slate-400 flex items-center space-x-1 font-mono">
                    <span className="text-[10px] text-slate-400">H(X):</span>
                    <span className="text-slate-300 tabular-nums">{evt.entropy_before.toFixed(2)}</span>
                    <span className="text-slate-500">&rarr;</span>
                    <span className={`font-black tabular-nums ${evt.entropy_after >= 7.5 ? 'text-tactical-crimson' : 'text-tactical-cyan'}`}>
                      {evt.entropy_after.toFixed(2)}
                    </span>
                    <span className={`text-[10px] ml-1 tabular-nums font-bold ${deltaPositive ? 'text-tactical-crimson' : 'text-slate-500'}`}>
                      ({deltaPositive ? '+' : ''}{evt.entropy_delta.toFixed(2)})
                    </span>
                  </div>

                  {evt.pid && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#0e1422] text-slate-300 border border-[#141c30] font-bold">
                      PID:{evt.pid}
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </SpotlightCard>
  );
};
