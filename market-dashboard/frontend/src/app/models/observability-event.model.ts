export interface ObservabilityEvent {
  ts: string;
  source: string;
  tech: string;
  message: string;
  detail?: Record<string, unknown>;
}
