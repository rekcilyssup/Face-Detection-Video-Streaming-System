export interface RoiDetection {
  id: number;
  stream_id: string;
  frame_number: number;
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
  detected_at: string;
}

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';
