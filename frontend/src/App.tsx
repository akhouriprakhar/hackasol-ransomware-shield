import React, { useEffect, useState, useRef } from 'react';
import { 
  AegisWebSocketClient, 
  fetchCopilotBriefing,
  fetchHealth, 
  fetchIncidents, 
  fetchTelemetry 
} from './api';
import { 
  AnalystAction, 
  ChartDataPoint, 
  CopilotMessage,
  HealthStatus, 
  IncidentAlert, 
  TelemetryEvent 
} from './types';
import { Header } from './components/Header';
import { DemoControlBar } from './components/DemoControlBar';
import { EntropyRadar } from './components/EntropyRadar';
import { IncidentPanel } from './components/IncidentPanel';
import { AICopilotCard } from './components/AICopilotCard';
import { TelemetryFeed } from './components/TelemetryFeed';

import { Shield, Terminal, Cpu, Info } from 'lucide-react';

export const App: React.FC = () => {
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [events, setEvents] = useState<TelemetryEvent[]>([]);
  const [activeIncident, setActiveIncident] = useState<IncidentAlert | null>(null);
  const [copilot, setCopilot] = useState<CopilotMessage | null>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);

  const [currentEntropy, setCurrentEntropy] = useState<number>(3.45);
  const [currentRisk, setCurrentRisk] = useState<number>(10.0);
  const [filesAffected, setFilesAffected] = useState<number>(0);
  const [totalFiles, setTotalFiles] = useState<number>(54);

  const chartIndexRef = useRef<number>(0);

  // Initialize baseline chart data points
  useEffect(() => {
    const initialPoints: ChartDataPoint[] = [];
    const now = Date.now();
    for (let i = 10; i >= 0; i--) {
      const ts = new Date(now - i * 1000);
      initialPoints.push({
        index: chartIndexRef.current++,
        timeStr: ts.toTimeString().split(' ')[0],
        fileName: 'baseline_idle.txt',
        entropy: 3.4 + (Math.random() * 0.3 - 0.15),
        riskScore: 8.0 + (Math.random() * 4.0 - 2.0),
        isCanary: false,
      });
    }
    setChartData(initialPoints);
  }, []);

  // Fetch initial system state & polling health
  useEffect(() => {
    const loadInitialState = async () => {
      try {
        const [healthData, telemetryData, incidentData] = await Promise.all([
          fetchHealth().catch(() => null),
          fetchTelemetry(40).catch(() => []),
          fetchIncidents(5).catch(() => []),
        ]);

        if (healthData) {
          setHealth(healthData);
          if (healthData.sandbox) {
            setTotalFiles(healthData.sandbox.total_files || 54);
            setFilesAffected(healthData.sandbox.locked_files || 0);
          }
          if (healthData.latest_incident) {
            setActiveIncident(healthData.latest_incident);
          }
        }

        if (telemetryData.length > 0) {
          setEvents(telemetryData);
          const latest = telemetryData[0];
          setCurrentEntropy(latest.entropy_after || 3.45);
        }

        if (incidentData.length > 0) {
          setActiveIncident(incidentData[0]);
          setCurrentRisk(incidentData[0].risk_score);
          if (incidentData[0].files_affected_count > 0) {
            setFilesAffected(incidentData[0].files_affected_count);
          }
          fetchCopilotBriefing(incidentData[0].incident_id)
            .then((b) => setCopilot(b))
            .catch(() => {});
        }

      } catch (err) {
        console.error('Error during initial state load:', err);
      }
    };

    loadInitialState();

    // Regular polling for health / locked count synchronization
    const pollTimer = setInterval(async () => {
      try {
        const h = await fetchHealth();
        setHealth(h);
        if (h.sandbox) {
          setTotalFiles(h.sandbox.total_files || 54);
          if (h.sandbox.locked_files > 0) {
            setFilesAffected(h.sandbox.locked_files);
          }
        }
        if (h.latest_incident && (!activeIncident || activeIncident.status !== 'CONTAINED')) {
          setActiveIncident(h.latest_incident);
        }
      } catch {
        // Backend offline / restarting
      }
    }, 3000);

    return () => clearInterval(pollTimer);
  }, []);

  // WebSocket telemetry & alerts stream
  useEffect(() => {
    const wsClient = new AegisWebSocketClient(
      '/ws/alerts',
      (msg) => {
        if (msg.type === 'telemetry') {
          const evt = msg.payload as TelemetryEvent;
          setEvents((prev) => [evt, ...prev.slice(0, 99)]);
          setCurrentEntropy(evt.entropy_after);

          const timeStr = new Date(evt.timestamp * 1000).toTimeString().split(' ')[0];
          const fileName = evt.file_path.split('/').pop() || evt.file_path;

          setChartData((prev) => {
            const nextPoint: ChartDataPoint = {
              index: chartIndexRef.current++,
              timeStr,
              fileName,
              entropy: evt.entropy_after,
              riskScore: currentRisk,
              isCanary: evt.is_canary,
            };
            return [...prev.slice(-24), nextPoint];
          });

          if (evt.file_path.endsWith('.locked')) {
            setFilesAffected((prev) => prev + 1);
          }
        } else if (msg.type === 'incident') {
          const inc = msg.payload as IncidentAlert;
          setActiveIncident(inc);
          setCurrentRisk(inc.risk_score);
          if (inc.files_affected_count > 0) {
            setFilesAffected(inc.files_affected_count);
          }

          // Mark containment flatline on chart
          setChartData((prev) => {
            const last = prev[prev.length - 1];
            if (!last) return prev;
            const updated = [...prev];
            updated[updated.length - 1] = {
              ...last,
              isContained: true,
              riskScore: inc.risk_score,
            };
            return updated;
          });
        } else if (msg.type === 'copilot') {
          const copilotData = msg.payload as CopilotMessage;
          setCopilot(copilotData);
        }
      },

      (connected) => setWsConnected(connected)
    );

    wsClient.connect();

    return () => {
      wsClient.disconnect();
    };
  }, [currentRisk]);

  // Stage Control Callbacks
  const handleSandboxReset = () => {
    setActiveIncident(null);
    setCopilot(null);
    setFilesAffected(0);

    setCurrentEntropy(3.42);
    setCurrentRisk(10.0);
    setEvents([]);

    // Reset chart to calm baseline
    const now = Date.now();
    const freshPoints: ChartDataPoint[] = [];
    for (let i = 8; i >= 0; i--) {
      const ts = new Date(now - i * 1000);
      freshPoints.push({
        index: chartIndexRef.current++,
        timeStr: ts.toTimeString().split(' ')[0],
        fileName: 'sandbox_restored.txt',
        entropy: 3.42 + (Math.random() * 0.2 - 0.1),
        riskScore: 8.0,
        isCanary: false,
      });
    }
    setChartData(freshPoints);
  };

  const handleAttackTriggered = (mode: string) => {
    // Proactively push a visual pulse indicator if attack started
    if (mode === 'burst' || mode === 'stealth') {
      setCurrentRisk(45.0);
    }
  };

  const handleActionComplete = (action: AnalystAction, result: string) => {
    if (action === 'ROLLBACK_RESTORE') {
      setFilesAffected(0);
      setCurrentEntropy(3.42);
      setCurrentRisk(10.0);
      if (activeIncident) {
        setActiveIncident({ ...activeIncident, status: 'RESTORED' });
      }
    } else if (action === 'TERMINATE_SIGKILL') {
      if (activeIncident) {
        setActiveIncident({ ...activeIncident, status: 'TERMINATED' });
      }
    } else if (action === 'RESUME_SIGCONT') {
      if (activeIncident) {
        setActiveIncident({ ...activeIncident, status: 'RELEASED' });
      }
    }
  };

  const isThreatContained = activeIncident?.status === 'CONTAINED';

  return (
    <div className="min-h-screen bg-cyber-950 text-slate-100 flex flex-col font-sans bg-grid-cyber">
      {/* 1. Top KPI & Health Strip */}
      <Header
        wsConnected={wsConnected}
        health={health}
        activeIncident={activeIncident}
        filesAffected={filesAffected}
        totalFiles={totalFiles}
      />

      {/* Main SOC Dashboard Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-4 sm:px-6 lg:px-8 space-y-4">
        
        {/* 2. Judge Demo Control Bar */}
        <DemoControlBar
          onSandboxReset={handleSandboxReset}
          onAttackTriggered={handleAttackTriggered}
          isThreatContained={isThreatContained}
        />

        {/* 3 & 4. Primary Intelligence Grid (Entropy Chart + Cryo Incident Panel) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          
          {/* Real-Time Shannon Entropy & Risk Timeline Chart (7 cols on lg) */}
          <div className="lg:col-span-7">
            <EntropyRadar
              data={chartData}
              currentEntropy={currentEntropy}
              currentRisk={currentRisk}
              isContained={isThreatContained}
            />
          </div>

          {/* Cryo-Quarantine & XAI Incident Panel (5 cols on lg) */}
          <div className="lg:col-span-5">
            <IncidentPanel
              incident={activeIncident}
              onActionComplete={handleActionComplete}
            />
          </div>

        </div>

        {/* AI Copilot Incident Briefing (Tier-2 Post-Containment Local Gemma 2B) */}
        <div className="w-full">
          <AICopilotCard
            incident={activeIncident}
            copilot={copilot}
            onRefresh={() => {
              if (activeIncident) {
                fetchCopilotBriefing(activeIncident.incident_id)
                  .then(setCopilot)
                  .catch(() => {});
              }
            }}
          />
        </div>

        {/* 5. Live FSEvents Telemetry Stream */}

        <div className="w-full">
          <TelemetryFeed
            events={events}
            onClear={() => setEvents([])}
          />
        </div>

      </main>

      {/* Footer Status Bar */}
      <footer className="border-t border-cyber-800 bg-cyber-900/80 px-4 py-2.5 text-xs font-mono text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <Cpu className="w-3.5 h-3.5 text-cyan-500" />
            <span>Target: macOS Darwin Apple Silicon (ARM64)</span>
            <span className="text-slate-700">|</span>
            <span>POSIX SIGSTOP Containment</span>
            <span className="text-slate-700">|</span>
            <span>Local Scikit-Learn IsolationForest</span>
          </div>
          <div className="flex items-center space-x-2 text-slate-400">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>Zero Cloud Dependencies &bull; 100% Offline Operational</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
