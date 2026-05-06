import { useState, useRef, useCallback, useEffect } from 'react';
import { config } from '../config';
import type { ConnectionState } from '../types';

export function useStreamConnection() {
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [currentFrame, setCurrentFrame] = useState<string | null>(null);
  const [fps, setFps] = useState(0);
  const [frameCount, setFrameCount] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const frameCountRef = useRef(0);
  const fpsIntervalRef = useRef<number | null>(null);
  const reconnectRef = useRef<number | null>(null);
  const intentionalClose = useRef(false);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    intentionalClose.current = false;
    setConnectionState('connecting');
    const ws = new WebSocket(config.ws.stream);
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => {
      setConnectionState('connected');
      fpsIntervalRef.current = window.setInterval(() => {
        setFps(frameCountRef.current);
        frameCountRef.current = 0;
      }, 1000);
    };

    ws.onmessage = (event) => {
      frameCountRef.current++;
      setFrameCount((prev) => prev + 1);

      if (event.data instanceof ArrayBuffer) {
        const blob = new Blob([event.data], { type: 'image/jpeg' });
        const url = URL.createObjectURL(blob);
        setCurrentFrame((prev) => {
          if (prev?.startsWith('blob:')) URL.revokeObjectURL(prev);
          return url;
        });
      } else if (typeof event.data === 'string') {
        try {
          const msg = JSON.parse(event.data);
          if (msg.frame) {
            setCurrentFrame(`data:image/jpeg;base64,${msg.frame}`);
          }
        } catch {
          setCurrentFrame(`data:image/jpeg;base64,${event.data}`);
        }
      }
    };

    ws.onclose = () => {
      setConnectionState('disconnected');
      if (fpsIntervalRef.current) clearInterval(fpsIntervalRef.current);
      if (!intentionalClose.current) {
        reconnectRef.current = window.setTimeout(() => connect(), 2000);
      }
    };

    ws.onerror = () => {
      setConnectionState('error');
    };

    wsRef.current = ws;
  }, []);

  const disconnect = useCallback(() => {
    intentionalClose.current = true;
    if (reconnectRef.current) clearTimeout(reconnectRef.current);
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (fpsIntervalRef.current) clearInterval(fpsIntervalRef.current);
    setConnectionState('disconnected');
    setCurrentFrame(null);
    setFps(0);
  }, []);

  useEffect(() => {
    return () => disconnect();
  }, [disconnect]);

  return { connectionState, currentFrame, fps, frameCount, connect, disconnect };
}
