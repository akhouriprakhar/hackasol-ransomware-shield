export type EventType = 'FILE_CREATE' | 'FILE_MODIFY' | 'FILE_RENAME' | 'FILE_DELETE';

export type IncidentStatus = 'ACTIVE' | 'CONTAINED' | 'RELEASED' | 'TERMINATED' | 'RESTORED';

export type AnalystAction = 'RESUME_SIGCONT' | 'TERMINATE_SIGKILL' | 'ROLLBACK_RESTORE';

export interface TelemetryEvent {
  type?: 'telemetry';
  event_id: string;
  timestamp: number;
  event_type: EventType;
  file_path: string;
  entropy_before: number;
  entropy_after: number;
  entropy_delta: number;
  pid?: number | null;
  process_name?: string | null;
  is_canary: boolean;
}

export interface XAIFactor {
  factor: string;
  weight: number;
}

export interface IncidentAlert {
  type?: 'incident';
  incident_id: string;
  timestamp: number;
  status: IncidentStatus;
  risk_score: number;
  offending_pid: number;
  process_name: string;
  files_affected_count: number;
  detection_latency_ms: number;
  containment_method: string;
  xai_breakdown: XAIFactor[];
}

export interface WatcherStatus {
  active: boolean;
  watch_dir: string;
  queue_size: number;
}

export interface MLModelStatus {
  loaded: boolean;
  model_type: string;
  features: string[];
}

export interface SandboxStatus {
  total_files: number;
  locked_files: number;
}

export interface HealthStatus {
  status: string;
  watcher: WatcherStatus;
  ml_model: MLModelStatus;
  protected_pids: number[];
  contained_pids: number[];
  tracked_pids: number[];
  sandbox?: SandboxStatus;
  latest_incident?: IncidentAlert | null;
  timestamp: number;
}

export interface SimulatorResponse {
  status: string;
  pid?: number;
  mode?: string;
  message: string;
  files_count?: number;
  canaries_count?: number;
}

export interface ActionResponse {
  status: 'success' | 'failed' | 'error';
  incident_id?: string;
  action: string;
  result: string;
}

export interface ChartDataPoint {
  index: number;
  timeStr: string;
  fileName: string;
  entropy: number;
  riskScore: number;
  isCanary: boolean;
  isContained?: boolean;
}

export interface CopilotMessage {
  type: 'copilot';
  incident_id: string;
  status: 'analyzing' | 'streaming' | 'completed' | 'failed';
  model: string;
  done: boolean;
  chunk?: string;
  narrative: string;
  fallback: boolean;
  timestamp?: number;
}

