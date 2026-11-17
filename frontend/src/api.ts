import { ActionResponse, HealthStatus, IncidentAlert, IncidentStatus, SimulatorResponse, TelemetryEvent } from './types';

const API_BASE = window.location.port === '5173' ? 'http://127.0.0.1:8000' : '';
const WS_BASE = window.location.port === '5173' ? 'ws://127.0.0.1:8000' : ((window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host);

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) {
    throw new Error(`Failed to fetch health: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchIncidents(limit = 20): Promise<IncidentAlert[]> {
  const res = await fetch(`${API_BASE}/api/incidents?limit=${limit}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch incidents: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchTelemetry(limit = 50): Promise<TelemetryEvent[]> {
  const res = await fetch(`${API_BASE}/api/telemetry?limit=${limit}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch telemetry: ${res.statusText}`);
  }
  return res.json();
}

export async function resetSimulator(): Promise<SimulatorResponse> {
  const res = await fetch(`${API_BASE}/api/simulator/reset`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Simulator reset failed: ${res.statusText}`);
  }
  return res.json();
}

export async function startSimulator(mode: 'burst' | 'stealth' | 'normal' | 'benign'): Promise<SimulatorResponse> {
  const res = await fetch(`${API_BASE}/api/simulator/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Simulator start failed: ${res.statusText}`);
  }
  return res.json();
}

export async function executeIncidentAction(
  incidentId: string,
  action: 'RESUME_SIGCONT' | 'TERMINATE_SIGKILL' | 'ROLLBACK_RESTORE'
): Promise<ActionResponse> {
  const res = await fetch(`${API_BASE}/api/incidents/${incidentId}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Action ${action} failed: ${res.statusText}`);
  }
  return res.json();
}

export type WSCallback = (data: { type: 'telemetry' | 'incident'; payload: TelemetryEvent | IncidentAlert }) => void;

export class AegisWebSocketClient {
  private ws: WebSocket | null = null;
  private endpoint: string;
  private onMessageCallback: WSCallback;
  private onStatusChange: (connected: boolean) => void;
  private shouldReconnect = true;
  private reconnectTimer: any = null;
  private pingTimer: any = null;

  constructor(
    endpoint: '/ws/alerts' | '/ws/telemetry',
    onMessage: WSCallback,
    onStatusChange: (connected: boolean) => void
  ) {
    this.endpoint = endpoint;
    this.onMessageCallback = onMessage;
    this.onStatusChange = onStatusChange;
  }

  public connect() {
    this.shouldReconnect = true;
    try {
      const url = `${WS_BASE}${this.endpoint}`;
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.onStatusChange(true);
        // Start keep-alive ping
        this.pingTimer = setInterval(() => {
          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send('ping');
          }
        }, 10000);
      };

      this.ws.onmessage = (event) => {
        if (event.data === 'pong') return;
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.type === 'telemetry') {
            this.onMessageCallback({ type: 'telemetry', payload: parsed });
          } else if (parsed.type === 'incident') {
            this.onMessageCallback({ type: 'incident', payload: parsed });
          } else if (parsed.incident_id) {
            this.onMessageCallback({ type: 'incident', payload: parsed });
          } else if (parsed.event_id) {
            this.onMessageCallback({ type: 'telemetry', payload: parsed });
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err, event.data);
        }
      };

      this.ws.onclose = () => {
        this.onStatusChange(false);
        this.cleanupPing();
        if (this.shouldReconnect) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = (err) => {
        console.warn(`WebSocket error on ${this.endpoint}:`, err);
        if (this.ws) {
          this.ws.close();
        }
      };
    } catch (e) {
      this.onStatusChange(false);
      this.scheduleReconnect();
    }
  }

  private cleanupPing() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (this.shouldReconnect) {
        this.connect();
      }
    }, 2000);
  }

  public disconnect() {
    this.shouldReconnect = false;
    this.cleanupPing();
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.onStatusChange(false);
  }
}
